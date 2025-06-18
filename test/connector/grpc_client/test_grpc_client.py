# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Test grpc_client module."""

import pytest
from unittest.mock import MagicMock, patch
from cloudvision import __version__ as version
from cloudvision.Connector.grpc_client import GRPCClient, PooledGRPCClient
from cloudvision.Connector.gen import router_pb2 as rtr


class TestGRPCClient:
    @pytest.mark.parametrize(
        "channel_options",
        [
            [
                ("grpc.primary_user_agent", f"cloudvision.Connector/{version}"),
                ("grpc.keepalive_time_ms", 60000),
                ("grpc.http2.max_pings_without_data", 0),
                ("grpc.enable_retries", 1),
                ("grpc.service_config", GRPCClient.GRPC_RETRY_POLICY_JSON),
            ]
        ],
    )
    def test_channel_options_defaults(self, channel_options):
        client = GRPCClient("localhost:443")
        assert hasattr(client, "channel_options")
        got = client.channel_options
        assert sorted(got) == sorted(channel_options)

    @pytest.mark.parametrize(
        "given, want",
        [
            (
                {
                    "grpc.keepalive_time_ms": 30000,
                    "grpc.http2.max_pings_without_data": 0,
                },
                [
                    ("grpc.primary_user_agent", f"cloudvision.Connector/{version}"),
                    ("grpc.keepalive_time_ms", 30000),
                    ("grpc.http2.max_pings_without_data", 0),
                    ("grpc.enable_retries", 1),
                    ("grpc.service_config", GRPCClient.GRPC_RETRY_POLICY_JSON),
                ],
            ),
            (
                {
                    "grpc.primary_user_agent": "torans_grpc_client",
                    "grpc.keepalive_time_ms": 1200000,
                    "grpc.http2.max_pings_without_data": 0,
                },
                [
                    ("grpc.primary_user_agent", "torans_grpc_client"),
                    ("grpc.keepalive_time_ms", 1200000),
                    ("grpc.http2.max_pings_without_data", 0),
                    ("grpc.enable_retries", 1),
                    ("grpc.service_config", GRPCClient.GRPC_RETRY_POLICY_JSON),
                ],
            ),
            (
                {
                    "grpc.primary_user_agent": "torans_grpc_client",
                    "grpc.keepalive_time_ms": 1200000,
                    "grpc.keepalive_timeout_ms": 10000,
                    "grpc.http2.max_pings_without_data": 1,
                },
                [
                    ("grpc.primary_user_agent", "torans_grpc_client"),
                    ("grpc.keepalive_time_ms", 1200000),
                    ("grpc.keepalive_timeout_ms", 10000),
                    ("grpc.http2.max_pings_without_data", 1),
                    ("grpc.enable_retries", 1),
                    ("grpc.service_config", GRPCClient.GRPC_RETRY_POLICY_JSON),
                ],
            ),
            (
                {
                    "grpc.primary_user_agent": "torans_grpc_client",
                    "grpc.keepalive_time_ms": 1200000,
                    "grpc.keepalive_timeout_ms": 10000,
                    "grpc.http2.max_pings_without_data": 1,
                    "grpc.enable_retries": 0,
                },
                [
                    ("grpc.primary_user_agent", "torans_grpc_client"),
                    ("grpc.keepalive_time_ms", 1200000),
                    ("grpc.keepalive_timeout_ms", 10000),
                    ("grpc.http2.max_pings_without_data", 1),
                    ("grpc.enable_retries", 0),
                    ("grpc.service_config", GRPCClient.GRPC_RETRY_POLICY_JSON),
                ],
            ),
        ],
    )
    def test_channel_options_overrides(self, given, want):
        client = GRPCClient("localhost:443", channel_options=given)
        assert hasattr(client, "channel_options")
        got = client.channel_options
        assert sorted(got) == sorted(want)

    def test_create_custom_schema_index_request(self):
        client = GRPCClient("localhost:443")
        d_name = "dataset_name"
        path_elements = ["path", "element"]
        schema = [
            rtr.IndexField(name="FieldName1", type=rtr.INTEGER),
            rtr.IndexField(name="FieldName1", type=rtr.FLOAT),
        ]
        d_type = "device"
        delete_after_days = 50
        request = client.create_custom_schema_index_request(
            d_name, path_elements, schema, delete_after_days, d_type
        )
        assert len(request.schema) == len(schema)
        for idx, fieldSchema in enumerate(request.schema):
            assert fieldSchema == schema[idx]
        assert request.option.delete_after_days == delete_after_days
        assert request.query.dataset.name == d_name
        assert request.query.dataset.type == d_type
        assert len(request.query.paths) == 1
        path = request.query.paths[0]
        for idx, path_element in enumerate(
            [client.encoder.encode(x) for x in path_elements]
        ):
            assert path_element == path.path_elements[idx]


# StubStreamAwareGRPCClient simulates real _StreamAwareGRPCClient behavior
class StubStreamAwareGRPCClient:
    def __init__(self, grpcAddr, max_streams, **kwargs):
        self.grpcAddr = grpcAddr
        self.max_streams = max_streams
        self.active_streams = 0
        self._id = id(self)

    def try_reserve_stream(self):
        if self.active_streams < self.max_streams:
            self.active_streams += 1
            return True
        return False

    def release_stream(self):
        self.active_streams -= 1

    def subscribe(self, *args, **kwargs):
        def fake_stream():
            yield from range(3)
        return fake_stream()

    def get(self, *args, **kwargs):
        return "notification"

    def publish(self, *args, **kwargs):
        return


class TestPooledGRPCClient:
    @patch("cloudvision.Connector.grpc_client.grpcConnectionPool._StreamAwareGRPCClient")
    def test_subscribe(self, MockClient):
        '''
        test_subscribe tests subscribe() of a PooledGRPCClient.
        This test:
        - Creates a PooledGRPCClient with max_streams_per_connection = 10
        - Creates 50 subscription
        - Verify that total 5 connections got created
        - Verify that each connection is serving 10 subscriptions
        - Verify that once subscription finishes, the active stream count in each connection is 0
        - Verify that the subscriptions are evenly distributed across connections pool
        '''
        MockClient.side_effect = lambda grpcAddr, max_streams, \
            **kwargs: StubStreamAwareGRPCClient(grpcAddr, max_streams)
        pool = PooledGRPCClient("localhost", max_streams_per_connection=10)

        # Request 50 streams
        streams = [pool.subscribe(["/test"]) for _ in range(50)]

        # Validate 50/10 = 5 connections got created
        assert len(pool._pool) == 5

        # Validate each connection has 10 active streams
        assert all(c.active_streams == 10 for c in pool._pool)

        # Consume streams to end subscription
        assert all(list(s) == [0, 1, 2] for s in streams)

        # Validate that we still have 5 connections in pool
        assert len(pool._pool) == 5

        # Validate that the active streams in each connection is 0
        assert all(c.active_streams == 0 for c in pool._pool)

        # Verify that the subscriptions are evenly distributed across connection pool
        streams = [pool.subscribe(["/test"]) for _ in range(35)]
        assert all(c.active_streams == 7 for c in pool._pool)
        assert all(list(s) == [0, 1, 2] for s in streams)

    @patch("cloudvision.Connector.grpc_client.grpcConnectionPool._StreamAwareGRPCClient")
    def test_connection_limit_reached(self, MockClient):
        '''
        test_connection_limit_reached verifies that the error is thrown when max_total_connection
        limit is reached.
        This test:
        - Creates a PooledGRPCClient with max_streams_per_connection=10 and max_connections=4
        - Creates 40 subscription to create 4 connections to reach max_connections limit
        - Creates a new subscription to expect runtime related to max_connections limit reached
        - Validate data received on all 40 subscription and close them to free up connections
        - Verify that the new subscriptions can be started when connections are freed up
        '''
        MockClient.side_effect = lambda grpcAddr, max_streams, \
            **kwargs: StubStreamAwareGRPCClient(grpcAddr, max_streams)
        pool = PooledGRPCClient("localhost", max_streams_per_connection=10, max_connections=4)

        # Create 40 subscription to reach max connection limit of 4
        streams = [pool.subscribe(["/test"]) for _ in range(40)]

        # Validate that exception is raised while trying to subscribe after all connections are
        # exhousted.
        with pytest.raises(RuntimeError, match="Maximum number of gRPC connections reached"):
            pool.subscribe(["/overflow"])

        # Consume streams to end subscription
        assert all(list(s) == [0, 1, 2] for s in streams)

        # Start 40 subscription again to validate that the new subscriptions can be created
        # once the stream capacity of connections is available again
        streams = [pool.subscribe(["/test"]) for _ in range(40)]
        assert all(list(s) == [0, 1, 2] for s in streams)

    @patch("cloudvision.Connector.grpc_client.grpcConnectionPool._StreamAwareGRPCClient")
    def test_get_publish(self, MockClient):
        '''
        test_get_publish tests PooledGRPCClient.get and PooledGRPCClient.publish
        This test verifies that new connection is created for publish and get requests
        when all connections in pool are maxed out.
        '''
        # Dynamically construct stubs with max_streams = 1 to simulate pressure
        self.stub_cl = [StubStreamAwareGRPCClient("localhost", max_streams=1) for _ in range(4)]
        MockClient.side_effect = lambda *args, **kwargs: self.stub_cl.pop(0)

        pool = PooledGRPCClient("localhost", max_streams_per_connection=1)

        # Verify initial pool of size 0
        assert len(pool._pool) == 0

        # Fill streams to pressure the pool
        streams = [pool.subscribe(["/test"]) for _ in range(3)]

        # Verify pool of size 3 after creating 3 subscriptions
        assert len(pool._pool) == 3

        # Verify that get and publish doesnt fail when all connections have reached out max_streams
        # capacity
        assert all(pool.get("/test/path") == "notification" for _ in range(5))
        [pool.publish(dId="testdataset", notifs=["notification"]) for _ in range(5)]

        # Verify that new connection is created to handle additional unary requests
        assert len(pool._pool) == 4

        # Consume streams to finish subscriptions
        assert all(list(s) == [0, 1, 2] for s in streams)

        # Validate that there are no active streams on any connection
        assert all(c.active_streams == 0 for c in pool._pool)
