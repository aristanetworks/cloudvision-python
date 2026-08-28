# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest
import time
from pathlib import Path
from unittest.mock import patch

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
REQUEST_METADATA = []


class TagServiceMock(TagServiceServicer):
    def GetAll(self, request, context):
        REQUEST_METADATA.append(tuple(context.invocation_metadata()))
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
    REQUEST_METADATA.clear()
    conns = AuthAndEndpoints(
        serviceAddr="localhost:50051",
        serviceCACert=Path.joinpath(TEST_DATA_DIR, "cert.pem"),
    )
    ctx = Context(
        user=User("test_user", "123"),
        connections=conns,
        metadata_provider=lambda: (("x-request-id", "request-123"),),
    )
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
        for _ in range(3):
            responses = list(tagService.GetAll(TagStreamRequest()))
            assert len(responses) == 5
        request_ids = [
            [item.value for item in metadata if item.key.lower() == "x-request-id"]
            for metadata in REQUEST_METADATA
        ]
        assert request_ids == [["request-123"]] * len(REQUEST_METADATA)
    except grpc.RpcError:
        pytest.fail("Grpc client should use the retry policy. No failure expected")


def test_get_api_client_shared_channel(start_server):
    REQUEST_METADATA.clear()
    context = Context(
        user=User("test_user", "123"),
        connections=AuthAndEndpoints(
            apiserverAddr=start_server,
            serviceCACert=Path.joinpath(TEST_DATA_DIR, "cert.pem"),
            aerisCACert=Path.joinpath(TEST_DATA_DIR, "cert.pem"),
        ),
        metadata_provider=lambda: (("x-request-id", "request-123"),),
    )
    try:
        tag_service = context.getApiClient(TagServiceStub)
        for _ in range(3):
            assert len(list(tag_service.GetAll(TagStreamRequest()))) == 5

        request_ids = [
            [item.value for item in metadata if item.key.lower() == "x-request-id"]
            for metadata in REQUEST_METADATA
        ]
        assert request_ids == [["request-123"]] * len(REQUEST_METADATA)
    finally:
        context.cleanup()


def test_get_cv_client_passes_metadata_provider():
    def metadata_provider():
        return (("x-request-id", "request-123"),)

    connections = AuthAndEndpoints(
        apiserverAddr="localhost:443",
        aerisCACert=Path.joinpath(TEST_DATA_DIR, "cert.pem"),
    )
    with patch("cloudvision.cvlib.context.GRPCClient") as grpc_client:
        context = Context(
            user=User("test_user", "123"),
            connections=connections,
            metadata_provider=metadata_provider,
        )
        context.getCvClient()

    grpc_client.assert_called_once_with(
        "localhost:443",
        ca=connections.aerisCACert,
        tokenValue="123",
        metadata_provider=metadata_provider,
    )
