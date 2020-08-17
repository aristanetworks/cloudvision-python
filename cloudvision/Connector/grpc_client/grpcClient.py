# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from datetime import datetime
from typing import List, Optional, Any, Tuple, Union

import cloudvision.Connector.codec as codec
import cloudvision.Connector.gen.notification_pb2 as ntf
import cloudvision.Connector.gen.router_pb2 as rtr
import cloudvision.Connector.gen.router_pb2_grpc as rtr_client

import grpc
import google.protobuf.timestamp_pb2 as pbts

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
        for path, keys in pathKeys if keys is not None
    ]
    return rtr.Query(
        dataset=ntf.Dataset(type=dtype, name=dId),
        paths=paths
    )


def create_notification(ts: TIME_TYPE,
                        paths: List[Any],
                        deletes: Optional[List[Any]] = None,
                        updates: Optional[UPDATES_TYPE] = None,
                        retracts: Optional[List[Any]] = None) \
        -> ntf.Notification:
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
        upds = [
            ntf.Notification.Update(
                key=encoder.encode(k),
                value=encoder.encode(v)) for k, v in updates
        ]
    rets = None
    if retracts is not None:
        rets = [encoder.encode(r) for r in retracts]

    pathElts = [encoder.encode(elt) for elt in paths]
    return ntf.Notification(
        timestamp=proto_ts,
        deletes=dels,
        updates=upds,
        retracts=rets,
        path_elements=pathElts
    )


class GRPCClient(object):
    """
    GRPCClient implements the protobuf client as well as its methods.
    grpcAddr must be a valid apiserver adress in the format <ADDRESS>:<PORT>.
    certs, if present, must be the path to the cert file.
    key, if present, must be the path to .pem key file.
    ca, if present, must be the path to a root certificate authority file.
    token, if present, must be the path a .tok user access token.
    """

    AUTH_KEY_PATH = "access_token"

    def __init__(self, grpcAddr: str, *, certs: Optional[str] = None,
                 key: Optional[str] = None, ca: Optional[str] = None,
                 token: Optional[str] = None) -> None:

        # used to store the auth token for per request auth
        self.metadata = None

        if (certs is None or key is None) and token is None:
            self.channel = grpc.insecure_channel(grpcAddr)
        else:
            tokCreds = None
            if token:
                with open(token, 'rb') as f:
                    tokData = f.read()
                    tokCreds = grpc.access_token_call_credentials(tokData)
                    self.metadata = ((self.AUTH_KEY_PATH,
                                      tokData.decode("ASCII").replace("\n", "")),)

            certData = None
            if certs:
                with open(certs, 'rb') as f:
                    certData = f.read()
            keyData = None
            if key:
                with open(key, 'rb') as f:
                    keyData = f.read()
            caData = None
            if ca:
                with open(ca, 'rb') as f:
                    caData = f.read()

            creds = grpc.ssl_channel_credentials(certificate_chain=certData,
                                                 private_key=keyData,
                                                 root_certificates=caData)

            if tokCreds:
                creds = grpc.composite_channel_credentials(creds, tokCreds)

            self.channel = grpc.secure_channel(grpcAddr, creds)
        self.__client = rtr_client.RouterV1Stub(self.channel)
        self.__auth_client = rtr_client.AuthStub(self.channel)

        self.encoder = codec.Encoder()
        self.decoder = codec.Decoder()

    # Make GRPCClient usable with `with` statement
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self.channel.__exit__(type, value, traceback)

    def close(self):
        self.channel.close()

    def get(self, queries: List[rtr.Query], start: Optional[TIME_TYPE] = None,
            end: Optional[TIME_TYPE] = None,
            versions: Optional[int] = None, sharding=None):
        """
        Get creates and executes a Get protobuf message, returning a stream of
        notificationBatch.
        queries must be a list of querry protobuf messages.
        start and end, if present, must be nanoseconds timestamps (uint64).
        sharding, if present must be a protobuf sharding message.
        """
        end_ts: Optional[int] = None
        start_ts: Optional[int] = None
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
            sharded_sub=sharding
        )
        stream = self.__client.Subscribe(req, metadata=self.metadata)
        return (self.decode_batch(nb) for nb in stream)

    def publish(self, dId, notifs: List[ntf.Notification],
                dtype: str = "device", sync: bool = True,
                compare: Optional[UPDATE_TYPE] = None) -> None:
        """
        Publish creates and executes a Publish protobuf message.
        refer to cloudvision/Connector/protobufs/router.proto:124
        default to sync publish being true so that changes are reflected
        """
        comp_pb = None
        if compare:
            key = compare[0]
            value = compare[1]
            comp_pb = ntf.Notification.Update(key=self.encoder.encode(key),
                                              value=self.encoder.encode(value))

        req = rtr.PublishRequest(
            batch=ntf.NotificationBatch(
                d="device",
                dataset=ntf.Dataset(type=dtype, name=dId),
                notifications=notifs
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
            types=types
        )
        stream = self.__client.GetDatasets(req)
        return stream

    def create_dataset(self, dtype, dId) -> None:
        req = rtr.CreateDatasetRequest(
            dataset=ntf.Dataset(type=dtype, name=dId)
        )
        self.__auth_client.CreateDataset(req, metadata=self.metadata)

    def decode_batch(self, batch):
        res = {
            "dataset": {
                "name": batch.dataset.name,
                "type": batch.dataset.type
            },
            "notifications": [self.decode_notification(n)
                              for n in batch.notifications]
        }
        return res

    def decode_notification(self, notif):
        res = {
            "timestamp": notif.timestamp,
            "deletes": [self.decoder.decode(d) for d in notif.deletes],
            "updates": {
                self.decoder.decode(u.key): self.decoder.decode(u.value)
                for u in notif.updates
            },
            "retracts": [self.decoder.decode(r) for r in notif.retracts],
            "path_elements": [
                self.decoder.decode(elt) for elt in notif.path_elements
            ]
        }
        return res
