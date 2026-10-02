# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Test grpc_client module."""

from queue import Empty, Queue
from threading import Event, Thread
from uuid import RFC_4122, UUID

import grpc
import pytest
from unittest.mock import MagicMock, patch
from cloudvision import __version__ as version
from cloudvision.Connector.grpc_client import GRPCClient, PooledGRPCClient
from cloudvision.Connector.gen import notification_pb2 as ntf
from cloudvision.Connector.gen import router_pb2 as rtr


_STREAM_END = object()


class ScriptedStream:
    def __init__(self, initial_metadata=()):
        self._initial_metadata = initial_metadata
        self._results = Queue()
        self.observed = Queue()
        self.cancelled = False
        self.cancel_observed = Event()
        self.terminal_observed = Event()

    def initial_metadata(self):
        if isinstance(self._initial_metadata, Exception):
            raise self._initial_metadata
        if callable(self._initial_metadata):
            return self._initial_metadata()
        return self._initial_metadata

    def deliver(self, batch):
        self._results.put(batch)

    def complete(self):
        self._results.put(_STREAM_END)

    def fail(self, error):
        self._results.put(error)

    def cancel(self):
        self.cancelled = True
        self.cancel_observed.set()
        self._results.put(_STREAM_END)

    def __iter__(self):
        return self

    def __next__(self):
        result = self._results.get()
        self.observed.put(result)
        if result is _STREAM_END:
            self.terminal_observed.set()
            raise StopIteration
        if isinstance(result, Exception):
            self.terminal_observed.set()
            raise result
        return result


class TestGRPCClient:
    @pytest.fixture(autouse=True)
    def get_rpc_resources(self):
        # Scripted unit tests share a stub; integration tests verify actual isolation.
        release = MagicMock()
        with patch.object(
            GRPCClient, "_create_get_rpc_resources",
            lambda client: (client._router_stub(), release),
        ):
            yield release

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

    def test_metadata_provider_is_evaluated_for_router_methods(self):
        request_ids = iter(["request-1", "request-2", "request-3"])
        client = GRPCClient(
            "localhost:443",
            tokenValue="token-value",
            metadata_provider=lambda: (("x-request-id", next(request_ids)),),
        )
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Get.return_value = []
        stream = MagicMock()
        stream.initial_metadata.return_value = (("subscription_active", ""),)
        stream.__iter__.return_value = iter([])
        client._GRPCClient__client.Subscribe.return_value = stream

        list(client.get([]))
        list(client.subscribe([]))
        client.publish("dataset", [])

        assert client._GRPCClient__client.Get.call_args.kwargs["metadata"] == (
            ("access_token", "token-value"),
            ("x-request-id", "request-1"),
        )
        assert client._GRPCClient__client.Subscribe.call_args.kwargs["metadata"] == (
            ("access_token", "token-value"),
            ("x-request-id", "request-2"),
        )
        assert client._GRPCClient__client.Publish.call_args.kwargs["metadata"] == (
            ("access_token", "token-value"),
            ("x-request-id", "request-3"),
        )
        assert client.metadata == (("access_token", "token-value"),)

    @pytest.mark.parametrize("token", [None, "token-value"])
    def test_get_and_subscribe_generates_shared_request_id(self, token):
        client = GRPCClient("localhost:443", tokenValue=token)
        client._GRPCClient__client = MagicMock()
        request_ids = []
        original_metadata = client.metadata

        for _ in range(2):
            client._GRPCClient__client.Subscribe.return_value = ScriptedStream(
                (("subscription_active", ""),)
            )
            client._GRPCClient__client.Get.return_value = ScriptedStream()
            stream = client.getAndSubscribe([])
            try:
                metadata = client._GRPCClient__client.Subscribe.call_args.kwargs["metadata"]
                assert metadata == client._GRPCClient__client.Get.call_args.kwargs["metadata"]
                assert metadata[:-1] == (original_metadata or ())
                assert metadata[-1][0] == "x-request-id"
                request_id = UUID(metadata[-1][1])
                assert request_id.version == 4
                assert request_id.variant == RFC_4122
                request_ids.append(request_id)
            finally:
                stream.close()

        assert request_ids[0] != request_ids[1]
        assert client.metadata == original_metadata

    def test_get_and_subscribe_coordinates_streams(self):
        metadata_calls = 0

        def metadata_provider():
            nonlocal metadata_calls
            metadata_calls += 1
            return (("request-metadata", "value"), ("x-request-id", "provided-id"))

        client = GRPCClient(
            "localhost:443",
            metadata_provider=metadata_provider,
        )
        subscribe_stream = ScriptedStream((("subscription_active", ""),))
        get_stream = ScriptedStream()
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = subscribe_stream
        client._GRPCClient__client.Get.return_value = get_stream

        result = client.getAndSubscribe([], versions=3, exact_range=True, timeout=10)

        subscribe_call = client._GRPCClient__client.Subscribe.call_args
        get_call = client._GRPCClient__client.Get.call_args
        assert subscribe_call.args[0] == rtr.SubscribeRequest()
        assert get_call.args[0] == rtr.GetRequest(versions=3, exact_range=True)
        assert subscribe_call.kwargs["metadata"] == get_call.kwargs["metadata"]
        assert subscribe_call.kwargs["metadata"] == (
            ("request-metadata", "value"),
            ("x-request-id", "provided-id"),
        )
        assert metadata_calls == 1
        assert subscribe_call.kwargs["timeout"] == get_call.kwargs["timeout"] == 10

        subscribe_stream.deliver(
            ntf.NotificationBatch(dataset=ntf.Dataset(type="device", name="subscription"))
        )
        # Subscribe must be deliverable before Get has produced any data.
        assert next(result)["dataset"]["name"] == "subscription"
        get_stream.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="first")))
        get_stream.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="last")))
        get_stream.complete()

        assert next(result)["dataset"]["name"] == "first"
        last = next(result)
        assert last["dataset"]["name"] == "last"
        assert last["metadata"] == {"GetRequest": "EOF"}

        subscribe_stream.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="after")))
        assert next(result)["dataset"]["name"] == "after"
        result.close()
        assert subscribe_stream.cancelled
        assert get_stream.cancelled

    def test_get_and_subscribe_waits_for_subscription_activation(self):
        header_requested = Event()
        header_ready = Event()

        def initial_metadata():
            header_requested.set()
            header_ready.wait()
            return (("subscription_active", ""),)

        client = GRPCClient("localhost:443")
        subscribe_stream = ScriptedStream(initial_metadata)
        get_stream = ScriptedStream()
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = subscribe_stream
        client._GRPCClient__client.Get.return_value = get_stream
        result = Queue()
        worker = Thread(target=lambda: result.put(client.getAndSubscribe([])))

        worker.start()
        assert header_requested.wait(timeout=1)
        client._GRPCClient__client.Get.assert_not_called()
        header_ready.set()
        worker.join(timeout=1)

        assert not worker.is_alive()
        stream = result.get_nowait()
        client._GRPCClient__client.Get.assert_called_once()
        stream.close()
        assert subscribe_stream.cancelled
        assert get_stream.cancelled

    def test_get_and_subscribe_emits_empty_get_marker(self):
        client = GRPCClient("localhost:443")
        subscribe_stream = ScriptedStream((("subscription_active", ""),))
        get_stream = ScriptedStream()
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = subscribe_stream
        client._GRPCClient__client.Get.return_value = get_stream

        result = client.getAndSubscribe([])
        get_stream.complete()

        assert next(result) == {
            "dataset": {"name": "", "type": ""},
            "metadata": {"GetRequest": "EOF"},
            "notifications": [],
        }
        result.close()

    def test_get_and_subscribe_preserves_final_batch_metadata_without_mutating_input(self):
        client = GRPCClient("localhost:443")
        subscribe_stream = ScriptedStream((("subscription_active", ""),))
        get_stream = ScriptedStream()
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = subscribe_stream
        client._GRPCClient__client.Get.return_value = get_stream
        final_batch = ntf.NotificationBatch(metadata={"existing": "value"})
        result = client.getAndSubscribe([])
        get_stream.deliver(final_batch)
        get_stream.complete()

        assert next(result)["metadata"] == {"existing": "value", "GetRequest": "EOF"}
        assert final_batch.metadata == {"existing": "value"}
        result.close()

    def test_get_and_subscribe_rejects_missing_active_header(self):
        client = GRPCClient("localhost:443")
        stream = ScriptedStream((("other-header", "value"),))
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = stream

        with pytest.raises(grpc.RpcError) as exc_info:
            client.getAndSubscribe([])

        assert exc_info.value.code() == grpc.StatusCode.UNAVAILABLE
        assert stream.cancelled
        client._GRPCClient__client.Get.assert_not_called()

    def test_get_and_subscribe_propagates_initial_metadata_error(self):
        client = GRPCClient("localhost:443")
        error = grpc.RpcError("metadata error")
        stream = ScriptedStream(error)
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = stream

        with pytest.raises(grpc.RpcError) as exc_info:
            client.getAndSubscribe([])

        assert exc_info.value is error
        assert stream.cancelled
        client._GRPCClient__client.Get.assert_not_called()

    def test_get_and_subscribe_propagates_stream_error(self):
        client = GRPCClient("localhost:443")
        subscribe_stream = ScriptedStream((("subscription_active", ""),))
        get_stream = ScriptedStream()
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = subscribe_stream
        client._GRPCClient__client.Get.return_value = get_stream
        result = client.getAndSubscribe([])
        error = grpc.RpcError("get failed")

        get_stream.fail(error)

        with pytest.raises(grpc.RpcError) as exc_info:
            next(result)
        assert exc_info.value is error
        assert subscribe_stream.cancelled

    def test_get_and_subscribe_delivers_all_received_batches_before_get_error(self):
        client = GRPCClient("localhost:443")
        subscribe_stream = ScriptedStream((("subscription_active", ""),))
        get_stream = ScriptedStream()
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = subscribe_stream
        client._GRPCClient__client.Get.return_value = get_stream
        result = client.getAndSubscribe([])
        error = grpc.RpcError("get failed")

        get_stream.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="first")))
        get_stream.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="second")))
        get_stream.fail(error)

        assert next(result)["dataset"]["name"] == "first"
        assert next(result)["dataset"]["name"] == "second"
        with pytest.raises(grpc.RpcError) as exc_info:
            next(result)
        assert exc_info.value is error

    @pytest.mark.parametrize("terminal", [None, grpc.RpcError("subscription failed")])
    def test_get_and_subscribe_handles_early_subscription_terminal(self, terminal):
        client = GRPCClient("localhost:443")
        subscribe_stream = ScriptedStream((("subscription_active", ""),))
        get_stream = ScriptedStream()
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = subscribe_stream
        client._GRPCClient__client.Get.return_value = get_stream
        result = client.getAndSubscribe([])

        subscribe_stream.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="buffered")))
        if terminal is None:
            subscribe_stream.complete()
        else:
            subscribe_stream.fail(terminal)
        assert next(result)["dataset"]["name"] == "buffered"
        assert subscribe_stream.terminal_observed.wait(timeout=1)
        if terminal is None:
            get_stream.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="get")))
            get_stream.complete()
            get_result = next(result)
            assert get_result["dataset"]["name"] == "get"
            assert get_result["metadata"] == {"GetRequest": "EOF"}
            with pytest.raises(StopIteration):
                next(result)
        else:
            # A subscription failure is reported even while Get remains blocked.
            with pytest.raises(grpc.RpcError) as exc_info:
                next(result)
            assert exc_info.value is terminal
            assert get_stream.cancelled

    def test_get_and_subscribe_drains_updates_before_post_get_subscription_error(self):
        client = GRPCClient("localhost:443")
        subscribe_stream = ScriptedStream((("subscription_active", ""),))
        get_stream = ScriptedStream()
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = subscribe_stream
        client._GRPCClient__client.Get.return_value = get_stream
        result = client.getAndSubscribe([])
        get_stream.complete()

        assert next(result)["metadata"] == {"GetRequest": "EOF"}

        subscribe_stream.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="first")))
        subscribe_stream.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="second")))
        error = grpc.RpcError("subscription failed")
        subscribe_stream.fail(error)

        assert next(result)["dataset"]["name"] == "first"
        assert next(result)["dataset"]["name"] == "second"
        with pytest.raises(grpc.RpcError) as exc_info:
            next(result)
        assert exc_info.value is error

    def test_subscribe_waits_for_active_header(self):
        client = GRPCClient("localhost:443")
        stream = MagicMock()
        stream.initial_metadata.return_value = (("subscription_active", ""),)
        stream.__iter__.return_value = iter(
            [ntf.NotificationBatch(dataset=ntf.Dataset(type="device", name="dataset"))]
        )
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = stream

        result = client.subscribe([])

        stream.initial_metadata.assert_called_once_with()
        assert list(result) == [
            {
                "dataset": {"name": "dataset", "type": "device"},
                "metadata": {},
                "notifications": [],
            }
        ]

    def test_subscribe_rejects_missing_active_header(self):
        client = GRPCClient("localhost:443")
        stream = MagicMock()
        stream.initial_metadata.return_value = (("other-header", "value"),)
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = stream

        with pytest.raises(grpc.RpcError) as exc_info:
            client.subscribe([])

        assert exc_info.value.code() == grpc.StatusCode.UNAVAILABLE
        stream.cancel.assert_called_once_with()

    def test_subscribe_propagates_initial_metadata_error(self):
        client = GRPCClient("localhost:443")
        stream = MagicMock()
        error = grpc.RpcError("metadata error")
        stream.initial_metadata.side_effect = error
        client._GRPCClient__client = MagicMock()
        client._GRPCClient__client.Subscribe.return_value = stream

        with pytest.raises(grpc.RpcError) as exc_info:
            client.subscribe([])

        assert exc_info.value is error


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

    def _router_stub(self):
        return MagicMock()

    def _get_and_subscribe(self, *args, release_get_resources, **kwargs):
        def fake_stream():
            release_get_resources()
            yield from range(3)
        return fake_stream()

    def get(self, *args, **kwargs):
        return "notification"

    def publish(self, *args, **kwargs):
        return


class TestPooledGRPCClient:
    @patch("cloudvision.Connector.grpc_client.grpcConnectionPool._StreamAwareGRPCClient")
    def test_get_and_subscribe_releases_stream(self, MockClient):
        MockClient.side_effect = lambda grpcAddr, max_streams, \
            **kwargs: StubStreamAwareGRPCClient(grpcAddr, max_streams)
        pool = PooledGRPCClient("localhost", max_streams_per_connection=1)

        stream = pool.getAndSubscribe([])

        assert pool._pool[0].active_streams == 1
        assert list(stream) == [0, 1, 2]
        assert pool._pool[0].active_streams == 0

    @patch("cloudvision.Connector.grpc_client.grpcConnectionPool._StreamAwareGRPCClient")
    def test_get_and_subscribe_releases_stream_when_closed_before_iteration(self, MockClient):
        MockClient.side_effect = lambda grpcAddr, max_streams, \
            **kwargs: StubStreamAwareGRPCClient(grpcAddr, max_streams)
        pool = PooledGRPCClient("localhost", max_streams_per_connection=1)
        stream = pool.getAndSubscribe([])

        stream.close()

        assert pool._pool[0].active_streams == 0

    @patch("cloudvision.Connector.grpc_client.grpcConnectionPool._StreamAwareGRPCClient")
    def test_get_and_subscribe_releases_stream_after_startup_error(self, MockClient):
        client = MagicMock()
        client._get_and_subscribe.side_effect = grpc.RpcError("startup failed")
        get_client = MagicMock()
        MockClient.side_effect = [client, get_client]
        pool = PooledGRPCClient("localhost", max_streams_per_connection=1)

        with pytest.raises(grpc.RpcError):
            pool.getAndSubscribe([])

        client.release_stream.assert_called_once_with()
        get_client.release_stream.assert_called_once_with()

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


@pytest.fixture
def scripted_operation():
    client = GRPCClient("localhost:443")
    subscribe = ScriptedStream((("subscription_active", ""),))
    snapshot = ScriptedStream()
    stub = MagicMock()
    stub.Subscribe.return_value = subscribe
    stub.Get.return_value = snapshot
    client._GRPCClient__client = stub
    released = Event()
    release = MagicMock(side_effect=released.set)
    with patch.object(client, "_create_get_rpc_resources", return_value=(stub, release)):
        yield client, subscribe, snapshot, release, released
    client.close()


def test_get_batches_and_updates_interleave_while_get_is_blocked(scripted_operation):
    client, subscribe, snapshot, release, released = scripted_operation
    stream = client.getAndSubscribe([])
    try:
        snapshot.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="first")))
        snapshot.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="last")))
        assert next(stream)["dataset"]["name"] == "first"
        assert not released.is_set()
        subscribe.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="live")))
        assert next(stream)["dataset"]["name"] == "live"
        snapshot.complete()
        last = next(stream)
        assert last["dataset"]["name"] == "last"
        assert last["metadata"] == {"GetRequest": "EOF"}
        assert released.wait(1)
        release.assert_called_once_with()
        subscribe.complete()
        with pytest.raises(StopIteration):
            next(stream)
    finally:
        stream.close()


@pytest.mark.parametrize("source", ["subscribe", "get"])
def test_paused_reader_backpressures_and_close_joins_workers(scripted_operation, source):
    client, subscribe, snapshot, release, released = scripted_operation
    workers = []

    def create_thread(**kwargs):
        worker = Thread(**kwargs)
        workers.append(worker)
        return worker

    with patch("cloudvision.Connector.grpc_client.grpcClient.Thread", side_effect=create_thread):
        stream = client.getAndSubscribe([])
    producer = subscribe if source == "subscribe" else snapshot
    batches = [ntf.NotificationBatch(dataset=ntf.Dataset(name=str(i))) for i in range(20)]
    try:
        for batch in batches:
            producer.deliver(batch)
        # Subscribe retains a queued batch and one blocked on put. Get additionally retains
        # one lookahead batch. Neither worker can continue draining the upstream stream.
        read_ahead = 2 if source == "subscribe" else 3
        for batch in batches[:read_ahead]:
            assert producer.observed.get(timeout=1) is batch
        with pytest.raises(Empty):
            producer.observed.get(timeout=0.2)
        assert next(stream)["dataset"]["name"] == "0"
        assert producer.observed.get(timeout=1) is batches[read_ahead]
    finally:
        stream.close()
    assert subscribe.cancelled
    assert snapshot.cancelled
    assert released.wait(1)
    release.assert_called_once_with()
    assert len(workers) == 2
    assert all(not worker.is_alive() for worker in workers)


def test_get_capacity_released_before_eof_is_consumed(scripted_operation):
    client, subscribe, snapshot, release, released = scripted_operation
    stream = client.getAndSubscribe([])
    try:
        subscribe.deliver(ntf.NotificationBatch(dataset=ntf.Dataset(name="live")))
        assert subscribe.observed.get(timeout=1).dataset.name == "live"
        snapshot.complete()
        assert released.wait(1)
        results = [next(stream), next(stream)]
        assert any(result["metadata"] == {"GetRequest": "EOF"} for result in results)
        release.assert_called_once_with()
    finally:
        stream.close()


def test_second_worker_start_failure_joins_first_worker(scripted_operation):
    client, subscribe, snapshot, release, released = scripted_operation
    workers = []

    def create_thread(**kwargs):
        worker = Thread(**kwargs)
        workers.append(worker)
        if len(workers) == 2:
            worker.start = MagicMock(side_effect=RuntimeError("cannot start Get worker"))
        return worker

    with patch("cloudvision.Connector.grpc_client.grpcClient.Thread", side_effect=create_thread):
        with pytest.raises(RuntimeError, match="cannot start Get worker"):
            client.getAndSubscribe([])
    assert not workers[0].is_alive()
    assert subscribe.cancelled
    assert snapshot.cancelled
    release.assert_called_once_with()


@pytest.mark.parametrize("failure", ["metadata", "header", "get", "thread", "query"])
def test_startup_failures_release_get_resources(scripted_operation, failure):
    client, subscribe, snapshot, release, released = scripted_operation
    stub = client._router_stub()
    queries = []
    if failure == "metadata":
        subscribe._initial_metadata = grpc.RpcError("metadata failure")
    elif failure == "header":
        subscribe._initial_metadata = ()
    elif failure == "get":
        stub.Get.side_effect = grpc.RpcError("get startup failure")
    elif failure == "query":
        queries = [object()]
    with patch("cloudvision.Connector.grpc_client.grpcClient.Thread") as thread:
        if failure == "thread":
            thread.return_value.start.side_effect = RuntimeError("cannot start thread")
        with pytest.raises(Exception):
            client.getAndSubscribe(queries)
    release.assert_called_once_with()
    assert released.is_set()
    if failure != "query":
        assert subscribe.cancelled
    if failure == "thread":
        assert snapshot.cancelled


@patch("cloudvision.Connector.grpc_client.grpcConnectionPool._StreamAwareGRPCClient")
def test_combined_pool_limit_rolls_back_before_rpc_start(MockClient):
    created = []

    def create(address, max_streams, **kwargs):
        client = StubStreamAwareGRPCClient(address, max_streams)
        client._get_and_subscribe = MagicMock()
        created.append(client)
        return client

    MockClient.side_effect = create
    pool = PooledGRPCClient("localhost", max_streams_per_connection=1, max_connections=1)
    with pytest.raises(RuntimeError, match="two distinct connections"):
        pool.getAndSubscribe([])
    assert len(created) == 1
    assert created[0].active_streams == 0
    created[0]._get_and_subscribe.assert_not_called()
    # The rolled-back slot remains available to an ordinary subscription.
    stream = pool.subscribe([])
    assert list(stream) == [0, 1, 2]


@patch("cloudvision.Connector.grpc_client.grpcConnectionPool._StreamAwareGRPCClient")
def test_combined_pool_releases_snapshot_before_subscription(MockClient):
    MockClient.side_effect = StubStreamAwareGRPCClient
    pool = PooledGRPCClient("localhost", max_streams_per_connection=1, max_connections=2)
    stream = pool.getAndSubscribe([])
    try:
        assert [client.active_streams for client in pool._pool] == [1, 1]
        assert next(stream) == 0
        assert [client.active_streams for client in pool._pool] == [1, 0]
    finally:
        stream.close()
    assert all(client.active_streams == 0 for client in pool._pool)


@patch("cloudvision.Connector.grpc_client.grpcConnectionPool._StreamAwareGRPCClient")
def test_combined_pool_reservation_is_atomic(MockClient):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    MockClient.side_effect = StubStreamAwareGRPCClient
    pool = PooledGRPCClient("localhost", max_streams_per_connection=1, max_connections=2)
    barrier = Barrier(8)

    def reserve():
        barrier.wait(timeout=2)
        try:
            return pool._reserve_combined_clients()
        except RuntimeError:
            return None

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda _: reserve(), range(8)))
    successes = [result for result in results if result is not None]
    assert len(successes) == 1
    assert len(pool._pool) == 2
    assert all(client.active_streams == 1 for client in pool._pool)
    assert successes[0][0] is not successes[0][1]
    for client in successes[0]:
        client.release_stream()
    assert all(client.active_streams == 0 for client in pool._pool)


def test_get_rpc_resources_reuses_credentials_and_forces_independent_transport():
    client = GRPCClient(
        "localhost:443", tokenValue="test-token",
        channel_options={"grpc.use_local_subchannel_pool": 0, "grpc.keepalive_time_ms": 1000},
    )
    try:
        channel = MagicMock()
        with patch("grpc.secure_channel", return_value=channel) as create:
            stub, release = client._create_get_rpc_resources()
        args, kwargs = create.call_args
        assert args == ("localhost:443", client._channel_credentials)
        options = dict(kwargs["options"])
        assert options["grpc.use_local_subchannel_pool"] == 1
        assert options["grpc.keepalive_time_ms"] == 1000
        assert options["grpc.service_config"] == GRPCClient.GRPC_RETRY_POLICY_JSON
        assert stub is not client._router_stub()
        release()
        release()
        channel.close.assert_called_once_with()
    finally:
        client.close()


@pytest.mark.parametrize("context_exit", [False, True])
def test_client_close_releases_owned_get_rpc_resourcess(context_exit):
    client = GRPCClient("localhost:443")
    channel = MagicMock()
    with patch("grpc.insecure_channel", return_value=channel):
        _, release = client._create_get_rpc_resources()
    if context_exit:
        client.__exit__(None, None, None)
    else:
        client.close()
    release()
    channel.close.assert_called_once_with()
    with patch("grpc.insecure_channel", return_value=channel):
        with pytest.raises(ValueError, match="closed client"):
            client._create_get_rpc_resources()


@patch("cloudvision.Connector.grpc_client.grpcConnectionPool._StreamAwareGRPCClient")
def test_combined_pool_balances_subscriptions_after_snapshot_release(MockClient):
    MockClient.side_effect = StubStreamAwareGRPCClient
    pool = PooledGRPCClient("localhost", max_streams_per_connection=10, max_connections=2)
    streams = []
    try:
        streams = [pool.getAndSubscribe([]) for _ in range(4)]
        assert all(next(stream) == 0 for stream in streams)
        assert [client.active_streams for client in pool._pool] == [2, 2]
    finally:
        for stream in streams:
            stream.close()
    assert all(client.active_streams == 0 for client in pool._pool)


@pytest.mark.parametrize("context_exit", [False, True])
def test_client_shutdown_stops_paused_combined_readers(scripted_operation, context_exit):
    client, subscribe, snapshot, release, _ = scripted_operation
    workers = []

    def create_thread(**kwargs):
        worker = Thread(**kwargs)
        workers.append(worker)
        return worker

    with patch("cloudvision.Connector.grpc_client.grpcClient.Thread", side_effect=create_thread):
        stream = client.getAndSubscribe([])
    try:
        for _ in range(3):
            subscribe.deliver(ntf.NotificationBatch())
        # Subscribe fills the queue first, so both workers deterministically block on handoff.
        subscribe.observed.get(timeout=1)
        subscribe.observed.get(timeout=1)
        for _ in range(3):
            snapshot.deliver(ntf.NotificationBatch())
        snapshot.observed.get(timeout=1)
        snapshot.observed.get(timeout=1)
        if context_exit:
            client.__exit__(None, None, None)
        else:
            client.close()
        assert all(not worker.is_alive() for worker in workers)
        assert subscribe.cancelled and snapshot.cancelled
        release.assert_called_once_with()
        assert not client._combined_cancellations
        with pytest.raises(StopIteration):
            next(stream)
    finally:
        stream.close()


@pytest.mark.parametrize("shutdown", ["cancel", "client_close"])
def test_combined_shutdown_unblocks_pending_iteration(scripted_operation, shutdown):
    from concurrent.futures import ThreadPoolExecutor

    client, subscribe, snapshot, release, _ = scripted_operation
    started = Event()

    class BlockingHandoff(Queue):
        def get(self, block=True, timeout=None):
            # Cancellation must wake an indefinite wait rather than rely on timed polling.
            assert block and timeout is None
            started.set()
            return super().get(block=block, timeout=timeout)

    with patch("cloudvision.Connector.grpc_client.grpcClient.Queue", BlockingHandoff):
        stream = client.getAndSubscribe([])

    def read():
        return next(stream)

    with ThreadPoolExecutor(max_workers=1) as executor:
        pending = executor.submit(read)
        try:
            assert started.wait(timeout=1)
            if shutdown == "cancel":
                stream.cancel()
                stream.cancel()
            else:
                client.close()
            with pytest.raises(StopIteration):
                pending.result(timeout=1)
            assert subscribe.cancelled and snapshot.cancelled
            release.assert_called_once_with()
            assert not client._combined_cancellations
        finally:
            stream.cancel()
    stream.close()
