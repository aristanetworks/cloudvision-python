# Copyright (c) 2026 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Verify Get-and-Subscribe against actual HTTP/2 connection limits."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event

import grpc
import pytest

from cloudvision.Connector.gen import notification_pb2 as ntf
from cloudvision.Connector.gen import router_pb2_grpc as rpc
from cloudvision.Connector.grpc_client import GRPCClient, PooledGRPCClient


@pytest.fixture
def one_stream_server(request):
    get_allowed = Event()
    get_allowed.set()
    get_started = Event()

    class Router(rpc.RouterV1Servicer):
        def Subscribe(self, request, context):
            context.send_initial_metadata((("subscription_active", ""),))
            yield ntf.NotificationBatch(dataset=ntf.Dataset(name="live"))
            done = Event()
            if not context.add_callback(done.set):
                done.set()
            done.wait()

        def Get(self, request, context):
            get_started.set()
            get_allowed.wait(timeout=3)
            yield ntf.NotificationBatch(dataset=ntf.Dataset(name="snapshot"))

    executor = ThreadPoolExecutor(max_workers=8)
    stream_limit = getattr(request, "param", 1)
    server = grpc.server(executor, options=(("grpc.max_concurrent_streams", stream_limit),))
    rpc.add_RouterV1Servicer_to_server(Router(), server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    try:
        yield f"127.0.0.1:{port}", get_allowed, get_started
    finally:
        get_allowed.set()
        server.stop(0).wait(timeout=3)
        executor.shutdown(wait=True)


@pytest.mark.parametrize("mode", ["direct", "pooled", "pooled_existing"])
def test_snapshot_completes_while_subscription_is_active(one_stream_server, mode):
    address, _, _ = one_stream_server
    stream = None
    existing = None
    pooled = mode != "direct"
    if pooled:
        client = PooledGRPCClient(
            address, max_streams_per_connection=1, max_connections=3,
            channel_options={"grpc.use_local_subchannel_pool": 0},
        )
    else:
        client = GRPCClient(address)
    try:
        if mode == "pooled_existing":
            existing = client.subscribe([])
            assert next(existing)["dataset"]["name"] == "live"
        stream = client.getAndSubscribe([], timeout=2)
        initial = [next(stream), next(stream)]
        snapshot = next(batch for batch in initial if batch["dataset"]["name"] == "snapshot")
        assert snapshot["dataset"]["name"] == "snapshot"
        assert snapshot["metadata"] == {"GetRequest": "EOF"}
        # Both streams deliver successfully even with one HTTP/2 stream per connection.
        assert any(batch["dataset"]["name"] == "live" for batch in initial)
        if pooled:
            assert len(client._pool) == (3 if existing is not None else 2)
            assert sum(c.active_streams for c in client._pool) == (2 if existing else 1)
    finally:
        if stream is not None:
            stream.close()
        if existing is not None:
            existing.close()
        if pooled:
            assert all(c.active_streams == 0 for c in client._pool)
            for connection in client._pool:
                connection.close()
        else:
            client.close()


@pytest.mark.parametrize("pooled", [False, True])
def test_subscription_delivers_while_get_is_blocked(one_stream_server, pooled):
    address, get_allowed, get_started = one_stream_server
    get_allowed.clear()
    client = (PooledGRPCClient(address, max_streams_per_connection=1, max_connections=2)
              if pooled else GRPCClient(address))
    stream = None
    try:
        stream = client.getAndSubscribe([], timeout=2)
        assert get_started.wait(timeout=1)
        assert next(stream)["dataset"]["name"] == "live"
        # Get cannot complete until this test explicitly permits it.
        assert not get_allowed.is_set()
        get_allowed.set()
        snapshot = next(stream)
        assert snapshot["dataset"]["name"] == "snapshot"
        assert snapshot["metadata"] == {"GetRequest": "EOF"}
    finally:
        get_allowed.set()
        if stream is not None:
            stream.close()
        if pooled:
            assert all(connection.active_streams == 0 for connection in client._pool)
            for connection in client._pool:
                connection.close()
        else:
            client.close()


@pytest.mark.parametrize("one_stream_server", [2], indirect=True)
def test_combined_pool_reuses_transports_with_existing_subscriptions(one_stream_server):
    address, _, _ = one_stream_server
    client = PooledGRPCClient(address, max_streams_per_connection=2, max_connections=2)
    streams = []
    try:
        for _ in range(3):
            stream = client.getAndSubscribe([], timeout=5)
            streams.append(stream)
            batches = [next(stream), next(stream)]
            assert {batch["dataset"]["name"] for batch in batches} == {"live", "snapshot"}
            snapshot = next(batch for batch in batches if batch["dataset"]["name"] == "snapshot")
            assert snapshot["metadata"] == {"GetRequest": "EOF"}
        assert len(client._pool) == 2
        assert sorted(connection.active_streams for connection in client._pool) == [1, 2]
    finally:
        for stream in streams:
            stream.close()
        assert all(connection.active_streams == 0 for connection in client._pool)
        for connection in client._pool:
            connection.close()


def test_pooled_cancel_unblocks_pending_iteration_and_releases_slots(one_stream_server):
    address, get_allowed, get_started = one_stream_server
    get_allowed.clear()
    client = PooledGRPCClient(address, max_streams_per_connection=1, max_connections=2)
    stream = client.getAndSubscribe([], timeout=5)
    started = Event()

    def read():
        started.set()
        return next(stream)

    try:
        assert get_started.wait(timeout=1)
        assert next(stream)["dataset"]["name"] == "live"
        with ThreadPoolExecutor(max_workers=1) as executor:
            pending = executor.submit(read)
            try:
                assert started.wait(timeout=1)
                stream.cancel()
                stream.cancel()
                with pytest.raises(StopIteration):
                    pending.result(timeout=1)
                assert all(connection.active_streams == 0 for connection in client._pool)
            finally:
                stream.cancel()
    finally:
        get_allowed.set()
        stream.close()
        for connection in client._pool:
            connection.close()
