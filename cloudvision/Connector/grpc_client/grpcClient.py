# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from argparse import ArgumentError
from datetime import datetime
from queue import Full, Queue
from threading import Event, Lock, Thread
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
from uuid import uuid4

import json
import grpc
from google.protobuf import timestamp_pb2 as pbts
from google.protobuf.empty_pb2 import Empty

from cloudvision import __version__ as version
from cloudvision.Connector import codec
from cloudvision.Connector.auth.cert import gen_csr_der
from cloudvision.Connector.core.utils import get_dict
from cloudvision.Connector.gen import ca_pb2 as ca
from cloudvision.Connector.gen import ca_pb2_grpc as ca_client
from cloudvision.Connector.gen import notification_pb2 as ntf
from cloudvision.Connector.gen import router_pb2 as rtr
from cloudvision.Connector.gen import router_pb2_grpc as rtr_client

TIME_TYPE = Union[pbts.Timestamp, datetime]
UPDATE_TYPE = Tuple[Any, Any]
UPDATES_TYPE = List[UPDATE_TYPE]
DEFAULT_DELETE_AFTER_DAYS = 34
DATASET_TYPE_DEVICE = "device"
# General timeout for Get requests
TIMEOUT_REQUEST = 60
# Flags/Headers used for indicating that subscriptions are active/get requests have finished
SUBSCRIPTION_ACTIVE_HEADER = "subscription_active"
GET_REQUEST_METADATA_KEY = "GetRequest"
END_OF_GET_METADATA_VALUE = "EOF"
# Markers for use in get and subscribe
_STREAM_COMPLETE = object()
_STREAM_READY = object()
_STREAM_CANCELLED = object()


def _once(callback):
    """Make resource release safe across the reader and RPC workers."""
    lock = Lock()
    released = False

    def release():
        nonlocal released
        with lock:
            if not released:
                released = True
                callback()

    return release


class _CancellableStream:
    """Iterator with cancellation that is safe while another thread calls next()."""

    def __init__(self, stream, cancel):
        self._stream = stream
        self._cancel = cancel

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._stream)

    def cancel(self):
        """Stop the RPCs and readers; pending iteration ends with StopIteration."""
        self._cancel()

    def close(self):
        """Cancel and close the iterator when it is not being iterated elsewhere."""
        self.cancel()
        self._stream.close()


class _SubscriptionActiveError(grpc.RpcError):
    def code(self):
        return grpc.StatusCode.UNAVAILABLE

    def details(self):
        return "received no subscription active header"

    def __str__(self):
        return self.details()


def to_pbts(ts: TIME_TYPE) -> pbts.Timestamp:
    if isinstance(ts, datetime):
        x = pbts.Timestamp()
        x.FromDatetime(ts)  # type: ignore
        return x
    elif isinstance(ts, pbts.Timestamp):
        return ts
    else:
        raise TypeError("timestamp must be a datetime or protobuf timestamp")


def create_query(pathKeys: List[Any], dId: str, dtype: str = DATASET_TYPE_DEVICE) -> rtr.Query:
    """
    create_query creates a protobuf query message with dataset ID dId
    and dataset type dtype.
    pathKeys must be of the form [([pathElts...], [keys...])...]
    """
    encoder = codec.Encoder()
    paths = [
        rtr.Path(
            keys=[encoder.encode(k) for k in keys],
            path_elements=[encoder.encode(elt) for elt in path],
        )
        for path, keys in pathKeys
        if keys is not None
    ]
    return rtr.Query(
        dataset=ntf.Dataset(type=dtype, name=dId),
        paths=paths,
    )


def create_notification(
    ts: TIME_TYPE,
    paths: List[Any],
    deletes: Optional[List[Any]] = None,
    updates: Optional[UPDATES_TYPE] = None,
    retracts: Optional[List[Any]] = None,
) -> ntf.Notification:
    """
    create_notification creates a notification protobuf message.
    ts must be a google.protobuf.timestamp_pb2.Timestamp or a
    python datetime object.
    paths must be a list of path elements.
    deletes and retracts, if present, must be lists of keys.
    updates, if present, must be of the form [(key, value)...].
    """
    proto_ts = to_pbts(ts)
    encoder = codec.Encoder()
    # An empty list would mean deleteAll so there is a need to distinguish between empty and None
    deleteAll = False
    dels = None
    if deletes is not None and not deletes:
        # Passed deletes is an empty list, e.g. deleteAll
        deleteAll = True
    elif deletes:
        dels = [encoder.encode(d) for d in deletes]

    upds = None
    if updates is not None:
        upds = [ntf.Notification.Update(key=encoder.encode(k),
                                        value=encoder.encode(v)) for k, v in updates]
    rets = None
    if retracts is not None:
        rets = [encoder.encode(r) for r in retracts]

    pathElts = [encoder.encode(elt) for elt in paths]
    return ntf.Notification(
        timestamp=proto_ts,
        delete_all=deleteAll,
        deletes=dels,
        updates=upds,
        retracts=rets,
        path_elements=pathElts,
    )


class GRPCClient(object):
    """
    GRPCClient implements the protobuf client as well as its methods.
    grpcAddr must be a valid apiserver address in the format <ADDRESS>:<PORT>.
    certs, if present, must be the path to the cert file.
    key, if present, must be the path to a .pem key file.
    ca, if present, must be the path to a root certificate authority file.
    token, if present, must be the path a .tok user access token.
    tokenValue, if present, is the actual token in string form. Cannot be set with token
    certsValue, if present, is the actual certs in string form. Cannot be set with certs
    keyValue, if present, is the actual key in string form. Cannot be set with key
    caValue, if present, is the actual ca in string form. Cannot be set with ca
    """

    AUTH_KEY_PATH = "access_token"
    DEFAULT_CHANNEL_OPTIONS = {
        "grpc.primary_user_agent": f"cloudvision.Connector/{version}",
        # 60 seconds
        "grpc.keepalive_time_ms": 60000,
        # 0 means infinite, as keepalive_time_ms is 60 seconds client will send 1 ping every minute
        "grpc.http2.max_pings_without_data": 0,
        # enable retries for the grpc client
        # https://grpc.github.io/grpc/core/group__grpc__arg__keys.html#ga212f667ecbcee3b100898ba7e88454df
        "grpc.enable_retries": 1,
    }
    GRPC_RETRY_POLICY_JSON = json.dumps(
        {
            "methodConfig": [
                {
                    "name": [{"service": ""}],
                    "retryPolicy": {
                        "maxAttempts": 5,
                        "initialBackoff": "1s",
                        "maxBackoff": "16s",
                        "backoffMultiplier": 2.0,
                        "retryableStatusCodes": ["UNAVAILABLE"],
                    },
                }
            ]
        }
    )

    def __init__(
        self,
        grpcAddr: str,
        *,
        certs: Optional[str] = None,
        key: Optional[str] = None,
        ca: Optional[str] = None,
        token: Optional[str] = None,
        tokenValue: Optional[str] = None,
        certsValue: Optional[str] = None,
        keyValue: Optional[str] = None,
        caValue: Optional[str] = None,
        channel_options: Dict[str, Any] = {},
        metadata_provider: Optional[Callable[[], Iterable[Tuple[str, str]]]] = None,
    ) -> None:
        # used to store the auth token for per request auth
        self.metadata = None
        self.metadata_provider = metadata_provider
        # create a channel option by merging the default channel options and the user provided one
        # NOTE: default options will be overriden if provided by the user
        channel_options = get_dict(channel_options)
        self.channel_options = [
            (k, v) for k, v in dict(GRPCClient.DEFAULT_CHANNEL_OPTIONS, **channel_options).items()
        ]
        self.channel_options.append(
            ("grpc.service_config", GRPCClient.GRPC_RETRY_POLICY_JSON)
        )
        creds = None
        if not ((certs is None or key is None) and (token is None and tokenValue is None)):
            tokCreds = None
            if token or tokenValue:
                if token and tokenValue:
                    raise ArgumentError(None, "Cannot supply both token and token value")
                tokData = ""
                if token:
                    with open(token, 'r') as f:
                        tokData = f.read().strip()
                elif tokenValue:
                    # need the elif to validate that tokenValue is string for typing
                    tokData = tokenValue
                tokCreds = grpc.access_token_call_credentials(tokData)
                self.metadata = (
                    (
                        self.AUTH_KEY_PATH,
                        tokData,
                    ),
                )

            certData = None
            if certs or certsValue:
                if certs and certsValue:
                    raise ArgumentError(None, "Cannot supply both certs and certs value")
                if certs:
                    with open(certs, 'rb') as cf:
                        certData = cf.read()
                elif certsValue:
                    certData = certsValue.encode('utf-8')
            keyData = None
            if key or keyValue:
                if key and keyValue:
                    raise ArgumentError(None, "Cannot supply both key and key value")
                if key:
                    with open(key, 'rb') as kf:
                        keyData = kf.read()
                elif keyValue:
                    keyData = keyValue.encode('utf-8')
            caData = None
            if ca or caValue:
                if ca and caValue:
                    raise ArgumentError(None, "Cannot supply both ca and ca value")
                if ca:
                    with open(ca, 'rb') as cf:
                        caData = cf.read()
                elif caValue:
                    caData = caValue.encode('utf-8')

            creds = grpc.ssl_channel_credentials(
                certificate_chain=certData,
                private_key=keyData,
                root_certificates=caData,
            )

            if tokCreds:
                creds = grpc.composite_channel_credentials(creds, tokCreds)

        self._grpc_addr = grpcAddr
        self._channel_credentials = creds
        self._get_resources_lock = Lock()
        self._get_resource_releases: set[Callable[[], None]] = set()
        self._combined_cancellations: set[Callable[[], None]] = set()
        self._closed = False
        self.channel = self._create_channel()
        self.__client = rtr_client.RouterV1Stub(self.channel)
        self.__auth_client = rtr_client.AuthStub(self.channel)
        self.__search_client = rtr_client.SearchStub(self.channel)
        self.__ca_client = ca_client.CertificateAuthorityStub(self.channel)

        self.encoder = codec.Encoder()
        self.decoder = codec.Decoder()

    def _create_channel(self, independent=False):
        options = dict(self.channel_options)
        if independent:
            # Otherwise gRPC can share a transport with the subscription channel.
            options["grpc.use_local_subchannel_pool"] = 1
        if self._channel_credentials is None:
            return grpc.insecure_channel(self._grpc_addr, options=list(options.items()))
        return grpc.secure_channel(
            self._grpc_addr, self._channel_credentials, options=list(options.items())
        )

    def _create_get_rpc_resources(self):
        """Create a temporary channel for Get and return its stub and cleanup callback.

        This only allocates RPC resources; the coordinator starts Get after Subscribe returns
        the subscription_active header. Cleanup closes this channel, leaving Subscribe's channel
        open. Tracking the callback also lets client.close() release an outstanding Get channel.
        """
        channel = self._create_channel(independent=True)
        try:
            stub = rtr_client.RouterV1Stub(channel)

            def close_get_connection():
                with self._get_resources_lock:
                    self._get_resource_releases.discard(release_get_resources)
                channel.close()

            release_get_resources = _once(close_get_connection)
            with self._get_resources_lock:
                if self._closed:
                    raise ValueError("Cannot invoke RPC on closed client")
                self._get_resource_releases.add(release_get_resources)
            return stub, release_get_resources
        except Exception:
            channel.close()
            raise

    def _router_stub(self):
        return self.__client

    # Make GRPCClient usable with `with` statement
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        with self._get_resources_lock:
            self._closed = True
            releases = tuple(self._get_resource_releases)
            cancellations = tuple(self._combined_cancellations)
        try:
            try:
                for cancel in cancellations:
                    cancel()
            finally:
                for release in releases:
                    release()
        finally:
            self.channel.close()

    def _get_rpc_metadata(self):
        metadata = self.metadata
        if self.metadata_provider:
            rpc_metadata = self.metadata_provider()
            if rpc_metadata:
                metadata = (*(metadata or ()), *rpc_metadata)
        return metadata

    def get(
        self,
        queries: List[rtr.Query],
        start: Optional[TIME_TYPE] = None,
        end: Optional[TIME_TYPE] = None,
        versions=0,
        sharding=None,
        exact_range=False,
        timeout: Optional[float] = TIMEOUT_REQUEST,
    ):
        """
        Get creates and executes a Get protobuf message, returning a stream of
        notificationBatch.
        queries must be a list of querry protobuf messages.
        start and end, if present, must be nanoseconds timestamps (uint64).
        sharding, if present must be a protobuf sharding message.
        """
        end_ts = 0
        start_ts = 0
        if end:
            end_ts = to_pbts(end).ToNanoseconds()

        if start:
            start_ts = to_pbts(start).ToNanoseconds()

        request = rtr.GetRequest(
            query=queries,
            start=start_ts,
            end=end_ts,
            versions=versions,
            sharded_sub=sharding,
            exact_range=exact_range,
        )
        stream = self.__client.Get(request, metadata=self._get_rpc_metadata(), timeout=timeout)
        return (self.decode_batch(nb) for nb in stream)

    def subscribe(self, queries, sharding=None, timeout: Optional[float] = None):
        """
        Subscribe creates and executes a Subscribe protobuf message,
        returning a stream of notificationBatch.
        queries must be a list of query protobuf messages.
        sharding, if present must be a protobuf sharding message.
        timeout: if present, sets the GRPC timeout in seconds. Default is None (no timeout).
        """
        stream = self._create_subscribe(
            queries=queries,
            sharding=sharding,
            timeout=timeout,
            metadata=self._get_rpc_metadata(),
        )
        return (self.decode_batch(nb) for nb in stream)

    def _create_subscribe(
        self,
        queries,
        sharding=None,
        timeout: Optional[float] = None,
        metadata: Any = None,
    ):
        req = rtr.SubscribeRequest(
            query=queries,
            sharded_sub=sharding,
        )
        stream = self.__client.Subscribe(req, metadata=metadata, timeout=timeout)
        try:
            initial_metadata = stream.initial_metadata()
            if not initial_metadata or not any(
                key == SUBSCRIPTION_ACTIVE_HEADER for key, _ in initial_metadata
            ):
                raise _SubscriptionActiveError()
        except Exception:
            stream.cancel()
            raise
        return stream

    def getAndSubscribe(
        self,
        queries: List[rtr.Query],
        start: Optional[TIME_TYPE] = None,
        versions=0,
        sharding=None,
        exact_range=False,
        timeout: Optional[float] = None,
    ):
        """
        Fetches current state and relays updates to the client.
        Results for Get and Subscribe are relayed concurrently, with no ordering guarantees.
        Clients must handle out-of-order notifications, including subscription updates
        preceding Get results.
        GetRequest:EOF marks only Get completion, on its final batch or an empty batch when Get
        returns no results.

        queries must be a list of query protobuf messages.
        start must be a protobuf Timestamp or datetime, if present.
        versions specifies the maximum number of versions to retrieve.
        sharding must be a protobuf sharding message, if present.
        exact_range specifies whether to return the initial state at time `start`.
        timeout sets the timeout of each RPC in seconds; None means no timeout.
        Two daemon reader threads use a single-batch handoff with backpressure when callers pause.
        Close the returned stream to cancel its RPCs and stop both reader threads.
        Use stream.cancel() when another thread may be blocked in next(stream); pending
        iteration ends with StopIteration. Closing the client also stops active readers.
        """
        # Create a temporary channel for Get and start Subscribe on the client's existing channel.
        get_stub, release_get_resources = self._create_get_rpc_resources()
        return self._get_and_subscribe(
            queries,
            start,
            versions,
            sharding,
            exact_range,
            timeout,
            get_stub=get_stub,
            release_get_resources=release_get_resources,
        )

    def _get_and_subscribe(
        self,
        queries,
        start=None,
        versions=0,
        sharding=None,
        exact_range=False,
        timeout=None,
        *,
        get_stub,
        release_get_resources,
    ):
        """Coordinate both RPCs using the caller's Get resource ownership policy.

        release_get_resources closes a direct client's temporary Get channel or releases a
        pooled client's reserved Get slot. RPC cancellation is handled separately below.
        """
        release_get_resources = _once(release_get_resources)
        subscribe_stream = None
        get_stream = None
        workers = []
        stopped = Event()
        results: Queue[Tuple[Any, Any]] = Queue(maxsize=1)

        def put(source, result):
            # A paused caller backpressures both RPCs. Timed puts let close() stop workers
            # even when no reader remains to make room in the handoff.
            while not stopped.is_set():
                try:
                    results.put((source, result), timeout=0.1)
                    return True
                except Full:
                    pass
            return False

        def cancel_streams():
            stopped.set()
            # Wake a blocked consumer without polling. A full queue already provides a wakeup;
            # the consumer checks stopped after taking that queued item and discards it.
            try:
                results.put_nowait((None, _STREAM_CANCELLED))
            except Full:
                pass
            try:
                if subscribe_stream is not None:
                    subscribe_stream.cancel()
            finally:
                try:
                    if get_stream is not None:
                        get_stream.cancel()
                finally:
                    release_get_resources()

        def cleanup():
            try:
                cancel_streams()
            finally:
                for worker in workers:
                    worker.join(timeout=1)
                with self._get_resources_lock:
                    self._combined_cancellations.discard(cleanup)

        cleanup = _once(cleanup)

        def consume_subscribe():
            try:
                for batch in subscribe_stream:
                    if not put("subscribe", batch):
                        return
                put("subscribe", _STREAM_COMPLETE)
            except Exception as error:
                put("subscribe", error)

        def consume_get():
            previous_batch = None
            try:
                for batch in get_stream:
                    if previous_batch is not None and not put("get", previous_batch):
                        return
                    previous_batch = batch
                # Release capacity before handing off EOF: callers may pause indefinitely.
                release_get_resources()
                eof_batch = ntf.NotificationBatch()
                if previous_batch is not None:
                    eof_batch.CopyFrom(previous_batch)
                eof_batch.metadata[GET_REQUEST_METADATA_KEY] = END_OF_GET_METADATA_VALUE
                if put("get", eof_batch):
                    put("get", _STREAM_COMPLETE)
            except Exception as error:
                release_get_resources()
                if previous_batch is not None and not put("get", previous_batch):
                    return
                put("get", error)
            finally:
                release_get_resources()

        try:
            start_ts = to_pbts(start).ToNanoseconds() if start else 0
            get_request = rtr.GetRequest(
                query=queries,
                start=start_ts,
                versions=versions,
                sharded_sub=sharding,
                exact_range=exact_range,
            )
            # Resolve dynamic metadata once for the logical operation.
            # Both RPCs share the x-request-id from metadata, or a generated UUID if absent.
            rpc_metadata = self._get_rpc_metadata()
            if not any(key == "x-request-id" for key, _ in (rpc_metadata or ())):
                rpc_metadata = (*(rpc_metadata or ()), ("x-request-id", str(uuid4())))
            subscribe_stream = self._create_subscribe(
                queries=queries,
                sharding=sharding,
                timeout=timeout,
                metadata=rpc_metadata,
            )
            # Wait for the subscription to be active before issuing Get on the temporary channel.
            get_stream = get_stub.Get(
                get_request, metadata=rpc_metadata, timeout=timeout
            )
            for name, consume in (
                ("grpc-subscribe", consume_subscribe),
                ("grpc-get", consume_get),
            ):
                worker = Thread(target=consume, name=name, daemon=True)
                worker.start()
                workers.append(worker)
            with self._get_resources_lock:
                if self._closed:
                    raise ValueError("Cannot invoke RPC on closed client")
                self._combined_cancellations.add(cleanup)
        except Exception:
            cleanup()
            raise

        def combined_stream():
            try:
                # Priming allows close() to reach finally before the first public result.
                yield _STREAM_READY
                completed = set()
                while len(completed) < 2 and not stopped.is_set():
                    source, result = results.get()
                    if result is _STREAM_CANCELLED or stopped.is_set():
                        return
                    if result is _STREAM_COMPLETE:
                        completed.add(source)
                    elif isinstance(result, Exception):
                        raise result
                    else:
                        yield self.decode_batch(result)
            finally:
                cleanup()

        stream = combined_stream()
        next(stream)
        return _CancellableStream(stream, cleanup)

    def publish(
        self,
        dId,
        notifs: List[ntf.Notification],
        dtype: str = DATASET_TYPE_DEVICE,
        sync: bool = True,
        compare: Optional[UPDATE_TYPE] = None,
        timeout: Optional[float] = TIMEOUT_REQUEST,
    ) -> None:
        """
        Publish creates and executes a Publish protobuf message.
        refer to cloudvision/Connector/protobufs/router.proto:124
        default to sync publish being true so that changes are reflected
        """
        comp_pb = None
        if compare:
            key = compare[0]
            value = compare[1]
            comp_pb = ntf.Notification.Update(
                key=self.encoder.encode(key),
                value=self.encoder.encode(value),
            )

        req = rtr.PublishRequest(
            batch=ntf.NotificationBatch(
                d=DATASET_TYPE_DEVICE,
                dataset=ntf.Dataset(type=dtype, name=dId),
                notifications=notifs,
            ),
            sync=sync,
            compare=comp_pb,
        )
        self.__client.Publish(req, metadata=self._get_rpc_metadata(), timeout=timeout)

    def get_datasets(self, types: Optional[List[str]] = None):
        """
        GetDatasets retrieves all the datasets streaming on CloudVision.
        types, if present, filter the queried dataset by types
        """
        req = rtr.DatasetsRequest(
            types=types,
        )
        stream = self.__client.GetDatasets(req, metadata=self.metadata)
        return stream

    def create_dataset(self, dtype, dId) -> None:
        req = rtr.CreateDatasetRequest(
            dataset=ntf.Dataset(type=dtype, name=dId),
        )
        self.__auth_client.CreateDataset(req, metadata=self.metadata)

    def decode_batch(self, batch):
        res = {
            "dataset": {
                "name": batch.dataset.name,
                "type": batch.dataset.type,
            },
            "metadata": batch.metadata,
            "notifications": [self.decode_notification(n) for n in batch.notifications],
        }
        return res

    def decode_notification(self, notif):
        res = {
            "timestamp": notif.timestamp,
            "deletes": [self.decoder.decode(d) for d in notif.deletes],
            "updates": {self.decoder.decode(u.key):
                        self.decoder.decode(u.value) for u in notif.updates},
            "retracts": [self.decoder.decode(r) for r in notif.retracts],
            "path_elements": [self.decoder.decode(elt) for elt in notif.path_elements],
        }
        return res

    def search(
        self,
        search_type=rtr.SearchRequest.CUSTOM,
        d_type: str = DATASET_TYPE_DEVICE,
        d_name: str = "",
        result_size: int = 1,
        start: Optional[TIME_TYPE] = None,
        end: Optional[TIME_TYPE] = None,
        path_elements=[],
        key_filters: Iterable[rtr.Filter] = [],
        value_filters: Iterable[rtr.Filter] = [],
        exact_range: bool = False,
        offset: int = 0,
        exact_term: bool = False,
        sort: Iterable[rtr.Sort] = [],
        count_only: bool = False,
    ):
        start_ts = to_pbts(start).ToNanoseconds() if start else 0
        end_ts = to_pbts(end).ToNanoseconds() if end else 0
        encoded_path_elements = [self.encoder.encode(x) for x in path_elements]
        req = rtr.SearchRequest(
            search_type=search_type,
            start=start_ts,
            end=end_ts,
            query=[
                rtr.Query(
                    dataset=ntf.Dataset(type=d_type, name=d_name),
                    paths=[
                        rtr.Path(path_elements=encoded_path_elements),
                    ],
                ),
            ],
            result_size=result_size,
            key_filters=key_filters,
            value_filters=value_filters,
            exact_range=exact_range,
            offset=offset,
            exact_term=exact_term,
            sort=sort,
            count_only=count_only,
        )
        res = self.__search_client.Search(req)
        return (self.decode_batch(nb) for nb in res)

    def set_custom_schema(
        self,
        d_name: str,
        path_elements: Iterable[str],
        schema: Iterable[rtr.IndexField],
        delete_after_days: int = DEFAULT_DELETE_AFTER_DAYS,
        d_type: str = DATASET_TYPE_DEVICE,
    ) -> Empty:
        """Set custom index schema for given path.

        :param d_name: Dataset name on aeris
        :param path_elements: Path elements for which schema needs to be set
        :param schema: Schema to be set
        :param delete_after_days: Number of days after which data would be deleted
        :param d_type: Type of the dataset
        :return: Empty message
        """
        req = self.create_custom_schema_index_request(
            d_name, path_elements, schema, delete_after_days, d_type)
        return self.__search_client.SetCustomSchema(req)

    def create_custom_schema_index_request(
        self,
        d_name,
        path_elements, schema,
        delete_after_days, d_type
    ) -> rtr.CustomIndexSchema:
        """Create custom index schema request from given imputs.

        :param d_name: Dataset name on aeris
        :param path_elements: Path elements for which schema needs to be set
        :param schema: Schema to be set
        :param delete_after_days: Number of days after which data would be deleted
        :param d_type: Type of the dataset
        :return: Custom index schema request
        """
        encoded_path_elements = [self.encoder.encode(x) for x in path_elements]
        req = rtr.CustomIndexSchema(
            query=rtr.Query
            (
                dataset=ntf.Dataset(type=d_type, name=d_name),
                paths=[rtr.Path(path_elements=encoded_path_elements)],
            ),
            schema=schema,
            option=rtr.CustomIndexOptions(delete_after_days=delete_after_days)
        )
        return req

    def reenroll(self, cert_path: str, key_path: str) -> bytes:
        """Reenroll the existing certificate.

        Caller can pass their current key and certificate and receive a renewed
        certificate in return.
        The default validity of the renewed certificate is 90 days.

        :param cert_path: Certificate file path
        :param key_path: Private Key file path
        :return: Renewed Certificate in ASN.1 DER
        """

        csr_der: bytes = gen_csr_der(cert_path, key_path)
        crt = self.__ca_client.Reenroll(ca.CSR(csr=csr_der))
        return crt.crt
