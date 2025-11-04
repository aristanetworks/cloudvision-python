# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest
import time
from pathlib import Path

from concurrent import futures
from cloudvision.cvlib import Context, User, AuthAndEndpoints
from arista.tag.v2.services import (
    TagServiceServicer,
    TagServiceStub,
    TagStreamRequest,
    TagStreamResponse,
    add_TagServiceServicer_to_server,
)

import grpc


THIS_DIR = Path(__file__).parent
TEST_DIR = THIS_DIR.parent.parent
TEST_DATA_DIR = Path.joinpath(TEST_DIR, "test_data")
GRPC_ATTEMPT = 1


class TagServiceMock(TagServiceServicer):
    def GetAll(self, request, context):
        global GRPC_ATTEMPT
        if GRPC_ATTEMPT < 5:
            GRPC_ATTEMPT = GRPC_ATTEMPT + 1
            context.abort(grpc.StatusCode.UNAVAILABLE, "Service UNAVAILABLE")
        for i in range(5):
            yield TagStreamResponse()


@pytest.fixture(scope="module")
def start_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    add_TagServiceServicer_to_server(TagServiceMock(), server)
    cert_bytes = bytes()
    with open(Path.joinpath(TEST_DATA_DIR, "cert.pem"), "rb") as f:
        cert_bytes = f.read()
    key_bytes = bytes()
    with open(Path.joinpath(TEST_DATA_DIR, "key.pem"), "rb") as f:
        key_bytes = f.read()
    server_cred = grpc.ssl_server_credentials([(key_bytes, cert_bytes)])
    server.add_secure_port("localhost:50051", server_cred)
    server.start()
    yield "localhost:50051"
    server.stop(None)


@pytest.fixture(scope="module")
def grpc_client(start_server):
    conns = AuthAndEndpoints(
        serviceAddr="localhost:50051",
        serviceCACert=Path.joinpath(TEST_DATA_DIR, "cert.pem"),
    )
    ctx = Context(user=User("test_user", "123"), connections=conns)
    yield ctx


def test_get_api_client(grpc_client):
    tagService = grpc_client.getApiClient(TagServiceStub)
    try:
        start_time = time.time()
        responses = list(tagService.GetAll(TagStreamRequest()))
        duration = time.time() - start_time
        # Backoff jitter is +- 0.2. Taking this into account when checking the total duration
        assert duration >= 15 * 0.8
        assert duration <= 15 * 1.2
        assert GRPC_ATTEMPT == 5, (
            "The number of `GetAll` attempts should be increase to 5 after the Unavailables"
        )
        assert len(responses) == 5, (
            "After the Unavailables the service should return 5 responses"
        )
    except grpc.RpcError:
        pytest.fail("Grpc client should use the retry policy. No failure expected")
