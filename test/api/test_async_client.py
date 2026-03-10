# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import ssl
import functools
import tempfile

import urllib3
import pytest
from cloudvision.api.client import AsyncCVClient, UnableToAuthenticateException
from pathlib import Path

from . import utils

pytestmark = [pytest.mark.filterwarnings(
    "ignore:Unverified HTTPS request is being made to host 'localhost'")]


@pytest.fixture
def tmp_dir_factory():
    with tempfile.TemporaryDirectory() as td:
        counter = 1
        td = Path(td)

        def factory():
            nonlocal counter
            d = td / str(counter)
            d.mkdir()
            counter += 1
            return d

        yield factory


@pytest.mark.asyncio
async def test_self_signed(tmp_dir_factory, unused_tcp_port_factory):
    certs = utils.create_self_signed_cert(tmp_dir_factory())
    async with utils.grpc_server(unused_tcp_port_factory(), certs) as (host, port):
        f = functools.partial(AsyncCVClient.from_token, utils.TEST_TOKEN, host=host,
                              port=port)
        await utils.assert_grpc_response(f)


@pytest.mark.asyncio
async def test_self_signed_insecure(tmp_dir_factory, unused_tcp_port_factory):
    certs = utils.create_self_signed_cert(tmp_dir_factory())

    async with utils.grpc_server(unused_tcp_port_factory(), certs) as (host, port):
        f = functools.partial(AsyncCVClient.from_token, utils.TEST_TOKEN, host=host,
                              port=port, insecure=True)
        await utils.assert_grpc_response(f)


@pytest.mark.asyncio
async def test_self_signed_insecure_wrong_host(tmp_dir_factory, unused_tcp_port_factory):
    certs = utils.create_self_signed_cert(tmp_dir_factory(), hostname='example.org')
    async with utils.grpc_server(unused_tcp_port_factory(), certs) as (host, port):
        f = functools.partial(AsyncCVClient.from_token, utils.TEST_TOKEN, host=host,
                              port=port, insecure=True)
        await utils.assert_grpc_response(f)


@pytest.mark.asyncio
async def test_self_signed_wrong_host(tmp_dir_factory, unused_tcp_port_factory):
    certs = utils.create_self_signed_cert(tmp_dir_factory(), hostname='example.org')
    async with utils.grpc_server(unused_tcp_port_factory(), certs) as (host, port):
        f = functools.partial(AsyncCVClient.from_token, utils.TEST_TOKEN, host=host,
                              port=port)
        with pytest.raises(ssl.SSLCertVerificationError):
            await utils.assert_grpc_response(f)


@pytest.mark.asyncio
async def test_ca_cert_provided(tmp_dir_factory, unused_tcp_port_factory):
    certs = utils.create_ca_signed_certs(tmp_dir_factory())
    async with utils.grpc_server(unused_tcp_port_factory(), certs) as (host, port):
        f = functools.partial(AsyncCVClient.from_token, utils.TEST_TOKEN, host=host,
                              port=port, cacert=certs.cacert)

        await utils.assert_grpc_response(f)


@pytest.mark.asyncio
async def test_bogus_ca_cert(tmp_dir_factory, unused_tcp_port_factory):
    realCerts = utils.create_ca_signed_certs(tmp_dir_factory())
    bogusCerts = utils.create_ca_signed_certs(tmp_dir_factory())

    async with utils.grpc_server(unused_tcp_port_factory(), bogusCerts) as (host, port):
        f = functools.partial(AsyncCVClient.from_token, utils.TEST_TOKEN, host=host,
                              port=port, cacert=realCerts.cacert)
        with pytest.raises(ssl.SSLCertVerificationError):
            await utils.assert_grpc_response(f)


@pytest.mark.asyncio
async def test_insecure(tmp_dir_factory, unused_tcp_port_factory):
    bogusCerts = utils.create_ca_signed_certs(tmp_dir_factory())

    async with utils.grpc_server(unused_tcp_port_factory(), bogusCerts) as (host, port):
        f = functools.partial(AsyncCVClient.from_token, utils.TEST_TOKEN, host=host,
                              port=port, insecure=True)
        await utils.assert_grpc_response(f)


@pytest.mark.asyncio
async def test_user_password_sefl_signed(tmp_dir_factory, unused_tcp_port_factory):
    certs = utils.create_self_signed_cert(tmp_dir_factory())
    port = unused_tcp_port_factory()
    async with utils.http_server(port=port, certs=certs):
        client = AsyncCVClient.from_user_credentials(username=utils.USERNAME,
                                                     password=utils.PASSWORD, host='localhost',
                                                     port=port)
        assert client.token == utils.TEST_TOKEN


@pytest.mark.asyncio
async def test_user_password_with_ca(tmp_dir_factory, unused_tcp_port_factory):
    certs = utils.create_ca_signed_certs(tmp_dir_factory())
    port = unused_tcp_port_factory()
    async with utils.http_server(port=port, certs=certs):
        client = AsyncCVClient.from_user_credentials(username=utils.USERNAME,
                                                     password=utils.PASSWORD, host='localhost',
                                                     port=port, cacert=certs.cacert)
        assert client.token == utils.TEST_TOKEN


@pytest.mark.asyncio
async def test_user_password_wrong_ca_cert(tmp_dir_factory, unused_tcp_port_factory):
    realCert = utils.create_ca_signed_certs(tmp_dir_factory())
    bogusCert = utils.create_ca_signed_certs(tmp_dir_factory())

    port = unused_tcp_port_factory()
    async with utils.http_server(port=port, certs=bogusCert):
        with pytest.raises(UnableToAuthenticateException):
            AsyncCVClient.from_user_credentials(username=utils.USERNAME,
                                                password=utils.PASSWORD, host='localhost',
                                                port=port, cacert=realCert.cacert)


@pytest.mark.asyncio
async def test_user_password_wrong_ca_cert_insecure(tmp_dir_factory, unused_tcp_port_factory):
    bogusCert = utils.create_ca_signed_certs(tmp_dir_factory())

    port = unused_tcp_port_factory()
    async with utils.http_server(port=port, certs=bogusCert):
        client = AsyncCVClient.from_user_credentials(username=utils.USERNAME,
                                                     password=utils.PASSWORD, host='localhost',
                                                     port=port,
                                                     insecure=True)
        assert client.token == utils.TEST_TOKEN


@pytest.mark.asyncio
async def test_user_password_wrong_password(tmp_dir_factory, unused_tcp_port_factory):
    certs = utils.create_ca_signed_certs(tmp_dir_factory())

    port = unused_tcp_port_factory()
    async with utils.http_server(port=port, certs=certs):
        with pytest.raises(UnableToAuthenticateException):
            AsyncCVClient.from_user_credentials(username=utils.USERNAME,
                                                password='wrong', host='localhost',
                                                port=port, cacert=certs.cacert)
