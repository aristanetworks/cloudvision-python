# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import logging
import threading
from typing import Any, Dict, List, Optional
from cloudvision.Connector.gen import notification_pb2 as ntf
from cloudvision.Connector.gen import router_pb2 as rtr
from cloudvision.Connector.grpc_client.grpcClient import GRPCClient, TIME_TYPE, UPDATE_TYPE, \
    DATASET_TYPE_DEVICE


class _StreamAwareGRPCClient(GRPCClient):
    """Extends GRPCClient with stream counting capability."""
    def __init__(self, grpcAddr, max_streams, **kwargs):
        super().__init__(grpcAddr=grpcAddr, **kwargs)
        self.active_streams = 0
        self.max_streams = max_streams
        self._lock = threading.Lock()
        self._id = id(self)
        logging.debug(f"{self._id} | create new connection")

    def try_reserve_stream(self):
        with self._lock:
            if self.active_streams < self.max_streams:
                self.active_streams += 1
                logging.debug(f"{self._id} | add stream({self.active_streams}/{self.max_streams})")
                return True
            return False

    def release_stream(self):
        with self._lock:
            self.active_streams -= 1
            logging.debug(f"{self._id} | release stream({self.active_streams}/{self.max_streams})")

    def print_client_info(self):
        with self._lock:
            logging.info(f"{self._id} | streams({self.active_streams}/{self.max_streams})")


class PooledGRPCClient:
    """
    PooledGRPCClient manages a connection pool of GRPCClient instances.
    It balances long-lived subscription streams using round-robin distribution,
    and routes unary `get` and `publish` calls without consuming stream slots.
    It also creates a new GRPCClient instances when all clients in pool has
    maxed out it's stream usage.

    If single instance of GRPCClient is being used to have 100+ subscription, it's
    recommended to use PooledGRPCClient instead.

    grpcAddr: must be a valid apiserver address in the format <ADDRESS>:<PORT>.
    certs: if present, must be the path to the cert file.
    key: if present, must be the path to a .pem key file.
    ca: if present, must be the path to a root certificate authority file.
    token: if present, must be the path a .tok user access token.
    tokenValue: if present, is the actual token in string form. Cannot be set with token
    certsValue: if present, is the actual certs in string form. Cannot be set with certs
    keyValue: if present, is the actual key in string form. Cannot be set with key
    caValue: if present, is the actual ca in string form. Cannot be set with ca
    """
    def __init__(
        self,
        grpcAddr,
        max_streams_per_connection=100,
        max_connections=21474837,
        token: Optional[str] = None,
        certs: Optional[str] = None,
        key: Optional[str] = None,
        ca: Optional[str] = None,
        tokenValue: Optional[str] = None,
        certsValue: Optional[str] = None,
        keyValue: Optional[str] = None,
        caValue: Optional[str] = None,
        channel_options: Dict[str, Any] = {},
    ) -> None:
        self.grpcAddr = grpcAddr
        self._max_streams = max_streams_per_connection
        self._max_connections = max_connections
        self.token = token
        self.certs = certs
        self.key = key
        self.ca = ca
        self.tokenValue = tokenValue
        self.certsValue = certsValue
        self.keyValue = keyValue
        self.caValue = caValue
        self.channel_options = channel_options
        self._pool: List[_StreamAwareGRPCClient] = []
        self._lock = threading.Lock()
        self._rr_index = 0        # round-robin cursor for subscribe
        self._unary_rr_index = 0  # round-robin cursor for get/publish

    def _print_connection_state(self):
        with self._lock:
            for client in self._pool:
                client.print_client_info()

    def _create_new_client(self):
        client = _StreamAwareGRPCClient(
            self.grpcAddr,
            self._max_streams,
            token=self.token,
            certs=self.certs,
            key=self.key,
            ca=self.ca,
            tokenValue=self.tokenValue,
            certsValue=self.certsValue,
            keyValue=self.keyValue,
            caValue=self.caValue,
            channel_options=self.channel_options,
        )
        self._pool.append(client)
        return client

    def _get_or_create_client(self):
        """
        _get_or_create_client returns a connection from connection pool on round-robin basid.
        If all connections have reached max_streams_per_connection limit, it
        creates a new connection and add it to connection pool.
        Raises a RuntimeError if new connection can't be created because max_connections limit
        is reached.
        """
        with self._lock:
            pool_size = len(self._pool)

            if pool_size > 0:
                start = self._rr_index % pool_size
                for i in range(pool_size):
                    idx = (start + i) % pool_size
                    client = self._pool[idx]
                    if client.try_reserve_stream():
                        self._rr_index = (idx + 1) % pool_size
                        return client

            if len(self._pool) >= self._max_connections:
                raise RuntimeError("Maximum number of gRPC connections reached")

            new_client = self._create_new_client()
            new_client.try_reserve_stream()
            self._rr_index = len(self._pool) % self._max_connections
            return new_client

    def _get_any_client(self):
        """
        Select a connection for unary RPCs (get, publish) without stream reservation.
        If all connections have reached max_streams_per_connection limit, it
        creates a new connection and add it to connection pool.
        Raises a RuntimeError if new connection can't be created because max_connections limit
        is reached
        """
        with self._lock:
            pool_size = len(self._pool)
            if pool_size == 0:
                return self._create_new_client()

            start = self._unary_rr_index % pool_size
            for i in range(pool_size):
                idx = (start + i) % pool_size
                client = self._pool[idx]
                if client.active_streams < client.max_streams:
                    self._unary_rr_index = (idx + 1) % pool_size
                    return client

            if len(self._pool) >= self._max_connections:
                raise RuntimeError("Maximum number of gRPC connections reached")

            return self._create_new_client()

    def subscribe(self, queries, sharding=None):
        """
        Subscribe creates and executes a Subscribe protobuf message,
        returning a stream of notificationBatch.
        queries must be a list of querry protobuf messages.
        sharding, if present must be a protobuf sharding message.
        """
        client = self._get_or_create_client()
        stream = client.subscribe(queries, sharding)

        def wrapped_stream():
            try:
                for item in stream:
                    yield item
            finally:
                client.release_stream()

        return wrapped_stream()

    def get(
        self,
        queries: List[rtr.Query],
        start: Optional[TIME_TYPE] = None,
        end: Optional[TIME_TYPE] = None,
        versions=0,
        sharding=None,
        exact_range=False
    ):
        """
        Get creates and executes a Get protobuf message, returning a stream of
        notificationBatch.
        queries must be a list of querry protobuf messages.
        start and end, if present, must be nanoseconds timestamps (uint64).
        sharding, if present must be a protobuf sharding message.
        Unary get request — uses any client, does not reserve a stream.
        """
        client = self._get_any_client()
        return client.get(
            queries=queries,
            start=start,
            end=end,
            versions=versions,
            sharding=sharding,
            exact_range=exact_range
        )

    def publish(
        self,
        dId,
        notifs: List[ntf.Notification],
        dtype: str = DATASET_TYPE_DEVICE,
        sync: bool = True,
        compare: Optional[UPDATE_TYPE] = None
    ):
        """
        Publish creates and executes a Publish protobuf message.
        refer to cloudvision/Connector/protobufs/router.proto:124
        default to sync publish being true so that changes are reflected
        Unary publish request — uses any client, does not reserve a stream.
        """
        client = self._get_any_client()
        return client.publish(
            dId=dId,
            notifs=notifs,
            dtype=dtype,
            sync=sync,
            compare=compare
        )
