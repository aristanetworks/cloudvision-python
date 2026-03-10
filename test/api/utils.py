# Copyright (c) 2026 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import collections
import asyncio
import subprocess
import ssl
import json
import contextlib
import http.server
import base64
import threading
from grpclib import utils, server

from cloudvision.api.arista.inventory import v1 as inventory

TEST_TOKEN = 'test'

USERNAME = "admin"
PASSWORD = "password123"


Certs = collections.namedtuple("Certs", ["key", "cert", "cacert"])


def create_ca_signed_certs(dstDir):
    caKey, caPem = dstDir / "ca.key", dstDir / "ca.pem"

    serverKey, serverCsr, serverCert, serverExt = (
        dstDir / "server.key", dstDir / "server.csr", dstDir / "server.crt",
        dstDir / "server.ext",)
    run_cmd([
        "openssl", "req", "-x509", "-sha256", "-nodes", "-newkey", "rsa:4096",
        "-days", "365", "-keyout", str(caKey), "-out", str(caPem),
        "-subj", "/CN=MyLocalCA/O=Development"
    ])

    run_cmd([
        "openssl", "genrsa", "-out", str(serverKey), "2048"
    ])

    with serverExt.open("w") as f:
        f.write("authorityKeyIdentifier=keyid,issuer\n")
        f.write("basicConstraints=CA:FALSE\n")
        f.write("keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment\n")
        f.write("subjectAltName = @alt_names\n")
        f.write("\n[alt_names]\nDNS.1 = localhost\nIP.1 = 127.0.0.1")

    run_cmd([
        "openssl", "req", "-new", "-key", serverKey, "-out", serverCsr,
        "-subj", "/CN=localhost"
    ])

    run_cmd([
        "openssl", "x509", "-req", "-in", serverCsr,
        "-CA", caPem, "-CAkey", caKey,
        "-CAcreateserial", "-out", serverCert,
        "-days", "365", "-sha256", "-extfile", serverExt
    ])

    return Certs(serverKey, serverCert, caPem)


def create_self_signed_cert(dstDir, hostname='localhost'):
    keyFile, certFile = dstDir / "key.pem", dstDir / "cert.pem"
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:2048",
        "-keyout", str(keyFile), "-out", str(certFile), "-sha256", "-nodes", "-days", "365",
        "-subj", f"/C=US/ST=New York/L=Brooklyn/O=Example Org/OU=IT/CN={hostname}"]
    run_cmd(cmd)
    return Certs(keyFile, certFile, None)


def run_cmd(command):
    subprocess.run(command, check=True, capture_output=True, text=True)


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


@contextlib.asynccontextmanager
async def grpc_server(port: int, certs: Certs):
    invService = MockInventoryService()
    srv = server.Server([invService])

    context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=certs.cert,
                            keyfile=certs.key)
    with utils.graceful_exit([server]):
        async with srv:
            await srv.start('localhost', port, ssl=context)
            yield 'localhost', port


async def assert_grpc_response(func):
    # Need to run this in executor, otherwise it would block the event loop forever
    client = await asyncio.get_running_loop().run_in_executor(None, func)
    with client as channel:
        stub = inventory.DeviceServiceStub(channel)
        result = []
        async for device in stub.get_all(inventory.DeviceStreamRequest(), timeout=10):
            result.append(device)

        assert len(result) == 3
        assert set([dev.value.key.device_id for dev in result]) == \
            {'device-0', 'device-1', 'device-2'}


@contextlib.asynccontextmanager
async def http_server(port, certs: Certs, username=USERNAME, password=PASSWORD):

    class CustomHTTPServer(BasicHttpServer, username=username, password=password):
        pass

    httpd = http.server.HTTPServer(('localhost', port), CustomHTTPServer)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certs.cert, keyfile=certs.key)

    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    t = threading.Thread(target=httpd.serve_forever)
    try:
        t.start()
        yield
    finally:
        httpd.shutdown()
        t.join()


class BasicHttpServer(http.server.BaseHTTPRequestHandler):
    def __init_subclass__(cls, username=USERNAME, password=PASSWORD, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.username = username
        cls.password = password

    def do_POST(self):
        auth_header = self.headers.get('Authorization')
        if auth_header is None or not self.check_auth(auth_header):
            self.send_auth_request()
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        resp = json.dumps({"sessionId": TEST_TOKEN}).encode()
        self.wfile.write(resp)
        self.wfile.flush()

    def check_auth(self, auth_header):
        # Expecting "Basic <base64_string>"
        if not auth_header.startswith('Basic '):
            return False

        encoded_creds = auth_header.split(' ')[1]
        decoded_creds = base64.b64decode(encoded_creds).decode('utf-8')
        return decoded_creds == f"{self.username}:{self.password}"

    def send_auth_request(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Test"')
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b'401 Unauthorized')
