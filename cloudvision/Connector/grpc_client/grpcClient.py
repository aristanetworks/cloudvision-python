# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from argparse import ArgumentError
from datetime import datetime
from typing import Any, Iterable, List, Optional, Tuple, Union

import grpc
from google.protobuf import timestamp_pb2 as pbts

from cloudvision.Connector import codec as codec
from cloudvision.Connector.gen import notification_pb2 as ntf
from cloudvision.Connector.gen import router_pb2 as rtr
from cloudvision.Connector.gen import router_pb2_grpc as rtr_client

TIME_TYPE = Union[pbts.Timestamp, datetime]
UPDATE_TYPE = Tuple[Any, Any]
UPDATES_TYPE = List[UPDATE_TYPE]


def to_pbts(ts: TIME_TYPE) -> pbts.Timestamp:
    if isinstance(ts, datetime):
        x = pbts.Timestamp()
        x.FromDatetime(ts)  # type: ignore
        return x
    elif isinstance(ts, pbts.Timestamp):
        return ts
    else:
        raise TypeError("timestamp must be a datetime or protobuf timestamp")


def create_query(pathKeys: List[Any], dId: str, dtype: str = "device") -> rtr.Query:
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
    # An empty list would mean deleteAll so distinguish z/w empty and None
    dels = None
    if deletes is not None:
        dels = [encoder.encode(d) for d in deletes]

    upds = None
    if updates is not None:
        upds = [ntf.Notification.Update(key=encoder.encode(k), value=encoder.encode(v)) for k, v in updates]
    rets = None
    if retracts is not None:
        rets = [encoder.encode(r) for r in retracts]

    pathElts = [encoder.encode(elt) for elt in paths]
    return ntf.Notification(
        timestamp=proto_ts,
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
        caValue: Optional[str] = None
    ) -> None:
        # used to store the auth token for per request auth
        self.metadata = None

        if (certs is None or key is None) and (token is None and tokenValue is None):
            self.channel = grpc.insecure_channel(grpcAddr)
        else:
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

            self.channel = grpc.secure_channel(grpcAddr, creds)
        self.__client = rtr_client.RouterV1Stub(self.channel)
        self.__auth_client = rtr_client.AuthStub(self.channel)
        self.__search_client = rtr_client.SearchStub(self.channel)

        self.encoder = codec.Encoder()
        self.decoder = codec.Decoder()

    # Make GRPCClient usable with `with` statement
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self.channel.__exit__(type, value, traceback)

    def close(self):
        self.channel.close()

    def get(
        self,
        queries: List[rtr.Query],
        start: Optional[TIME_TYPE] = None,
        end: Optional[TIME_TYPE] = None,
        versions=0,
        sharding=None,
        exact_range=False,
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
        stream = self.__client.Get(request, metadata=self.metadata)
        return (self.decode_batch(nb) for nb in stream)

    def subscribe(self, queries, sharding=None):
        """
        Subscribe creates and executes a Subscribe protobuf message,
        returning a stream of notificationBatch.
        queries must be a list of querry protobuf messages.
        sharding, if present must be a protobuf sharding message.
        """

        req = rtr.SubscribeRequest(
            query=queries,
            sharded_sub=sharding,
        )
        stream = self.__client.Subscribe(req, metadata=self.metadata)
        return (self.decode_batch(nb) for nb in stream)

    def publish(
        self,
        dId,
        notifs: List[ntf.Notification],
        dtype: str = "device",
        sync: bool = True,
        compare: Optional[UPDATE_TYPE] = None,
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
                d="device",
                dataset=ntf.Dataset(type=dtype, name=dId),
                notifications=notifs,
            ),
            sync=sync,
            compare=comp_pb,
        )
        self.__client.Publish(req, metadata=self.metadata)

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
            "notifications": [self.decode_notification(n) for n in batch.notifications],
        }
        return res

    def decode_notification(self, notif):
        res = {
            "timestamp": notif.timestamp,
            "deletes": [self.decoder.decode(d) for d in notif.deletes],
            "updates": {self.decoder.decode(u.key): self.decoder.decode(u.value) for u in notif.updates},
            "retracts": [self.decoder.decode(r) for r in notif.retracts],
            "path_elements": [self.decoder.decode(elt) for elt in notif.path_elements],
        }
        return res

    def search(
        self,
        search_type=rtr.SearchRequest.CUSTOM,
        d_type: str = "device",
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
