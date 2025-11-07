# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import ssl
import asyncio
import functools

import pytest
from grpclib import utils, server
import pytest_asyncio
from cloudvision.api.arista.inventory import v1 as inventory
from cloudvision.api.client import AsyncCVClient
from pathlib import Path

TEST_TOKEN = 'test'
THIS_DIR = Path(__file__).parent
TEST_DIR = THIS_DIR.parent
TEST_DATA_DIR = Path.joinpath(TEST_DIR, "test_data")


class MockInventoryService(inventory.DeviceServiceBase):

    async def _call_rpc_handler_server_stream(self, handler, stream, request):
        assert stream.metadata['authorization'] == f'Bearer {TEST_TOKEN}'
        return await super()._call_rpc_handler_server_stream(handler, stream, request)

    async def get_all(self, device_stream_request):
        for i in range(3):
            yield inventory.DeviceStreamResponse(
                value=inventory.Device(
                    key=inventory.DeviceKey(device_id=f'device-{i}')
                )
            )


@pytest_asyncio.fixture
async def grpc_server(unused_tcp_port_factory):
    invService = MockInventoryService()
    srv = server.Server([invService])

    context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=Path.joinpath(TEST_DATA_DIR, "cert.pem"),
                            keyfile=Path.joinpath(TEST_DATA_DIR, "key.pem"))
    with utils.graceful_exit([server]):
        async with srv:
            port = unused_tcp_port_factory()
            await srv.start('localhost', port, ssl=context)
            yield 'localhost', port


@pytest.mark.asyncio
async def test_token_auth(grpc_server):
    host, port = grpc_server
    callable = functools.partial(AsyncCVClient.from_token, TEST_TOKEN, host=host, port=port)
    # Need to run this in executor, otherwise it would block the event loop forever
    client = await asyncio.get_running_loop().run_in_executor(None, callable)
    with client as channel:
        stub = inventory.DeviceServiceStub(channel)
        result = []
        async for device in stub.get_all(inventory.DeviceStreamRequest(), timeout=10):
            result.append(device)

        assert len(result) == 3
        assert set([dev.value.key.device_id for dev in result]) == \
            {'device-0', 'device-1', 'device-2'}
