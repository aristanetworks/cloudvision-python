# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import requests
import ssl
from grpclib import client, events
import tempfile


class AsyncCVClient:
    """
    This class enables access to CloudVision GRPC API using grpclib stubs.

    Use one of classmethods :py:func:`from_token` :py:func:`from_user_credentials`
    to intantialize the client, and use it with stubs from
    :py:mod:`cloudvision.api.arista`

    It is implemented as contextmanager, that provides instance of grpclib.client.Channel_.
    See example below

    .. _grpclib.client.Channel: https://grpclib.readthedocs.io/en/latest/client.html

    .. versionadded:: 1.26.1

    .. code-block:: python

        import asyncio
        from cloudvision.api.client import AsyncCVClient
        from cloudvision.api.arista.inventory.v1 import DeviceServiceStub, DeviceStreamRequest

        async def get_devices():
            client = AsyncCVClient.from_token('<your service account token>', 'your-cvp.io')

            # get channel
            with client as channel:

                # pass it to the stub
                service = DeviceServiceStub(channel)

                # execute one of stub's methods
                async for item in service.get_all(DeviceStreamRequest()):
                    print(item)

        asyncio.run(get_devices())

    .. note::
        If for some reason multiple context managers with the same client are
        used, each will produce a new channel that would be closed accordingly (see below)

        .. code-block:: python

            client = AsyncCVCClient(...)

            with client as channel1:
                # channel1 is open
                with client as channel2:
                    ... # both channel1 and channel2 are open
                # channel2 is closed while channel 1 is still open
            # channel1 is closed
    """
    def __init__(self, token, ssl_context, host, port=443, username=None):
        self.token = token
        self.ssl_context = ssl_context
        self._channel = None
        self.host = host
        self.port = port
        self.username = username
        self._channel_stack = []

    @classmethod
    def from_token(cls, token, host, port=443, username=None):
        """
        If you would like to use service accounts, you can create them in CloudVision UI
        https://my-cloudvision-instance.io/cv/setting/aaa-service-accounts

        Generate a token for service account and pass it to this method to get an instance of
        the client.

        :rtype: AsyncCVClient
        """
        cadata = ssl.get_server_certificate((host, port))

        context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH,
                                             cadata=cadata)
        context.set_alpn_protocols(["h2"])

        return cls(token=token, ssl_context=context, port=port, host=host, username=username)

    @classmethod
    def from_user_credentials(cls, username, password, host, port=443):
        """
        Use usename and password to authenticate in CloudVision

        :rtype: AsyncCVClient
        """
        cadata = ssl.get_server_certificate((host, port))

        with tempfile.NamedTemporaryFile("a+") as fw:
            fw.write(cadata)
            fw.flush()

            r = requests.post(
                'https://' + host + '/cvpservice/login/authenticate.do',
                auth=(username, password), verify=fw.name)

            r.raise_for_status()
            token = r.json()['sessionId']

        context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH,
                                             cadata=cadata)
        context.set_alpn_protocols(["h2"])

        return cls(token=token, ssl_context=context, port=port, host=host, username=username)

    def _init_channel(self):
        """
        Initializes an authenticated Channel for sending GRPC requests. When using this method,
        ensure that Channel is duly closed (`channel.close()`) after it's being used. Using context
        manager `with client as channel: ...` is more recommended for this reason.

        :rtype: grpclib.client.Channel
        """
        async def _auth_middleware(event: events.SendRequest):
            if self.username:
                event.metadata['username'] = str(self.username)
            event.metadata['authorization'] = f'Bearer {self.token}'

        channel = client.Channel(
            host=self.host,
            port=self.port,
            ssl=self.ssl_context
        )
        events.listen(channel, events.SendRequest, _auth_middleware)
        return channel

    def __enter__(self):
        """
        Returns an authenticated GRPC channel, that would be closed upon exitting
        the context manager.

        :rtype: grpclib.client.Channel
        """
        channel = self._init_channel()
        self._channel_stack.append(channel)
        return channel

    def __exit__(self, *args):
        channel = self._channel_stack.pop()
        channel.close()
