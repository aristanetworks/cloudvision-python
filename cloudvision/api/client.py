# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import urllib3
import pathlib
import ssl
from grpclib import client, events
from base64 import b64encode


class UnableToAuthenticateException(Exception):
    """
    Is thrown when unable to authenticate using username and password
    """
    pass


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
    def _get_ssl_context(cls, host, port=443, cacert=None, insecure=False):
        if not insecure:
            if not cacert:
                # This would be the case for on prem deployments as they will have self-signed
                # certificates. This won't save from bogus cert, but at least it verify that
                # the cert didn't expired and the hostname is right
                cadata = ssl.get_server_certificate((host, port))
            else:
                cacert = pathlib.Path(cacert)
                with cacert.open("r") as f:
                    cadata = f.read()

            context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH,
                                                 cadata=cadata)
            context.set_alpn_protocols(["h2"])
        else:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        return context

    @classmethod
    def from_token(cls, token, host, port=443, username=None, insecure=False, cacert=None):
        """
        If you would like to use service accounts, you can create them in CloudVision UI
        https://my-cloudvision-instance.io/cv/setting/aaa-service-accounts

        Generate a token for service account and pass it to this method to get an instance of
        the client.

        .. note::
            With default parameters, it would assume that the host has a self-signed certificate and
            it will fetch it and verify hostname and expiry. It is recommended that you use
            CA signed certificate in your CloudVision deployment, so you'd either add this CA to
            the list of trusted CAs, or provide it's certificate via `cacert` parameter

        .. DANGER::
            Avoid setting `insecure=True` as this would disable certificate check

        .. versionchanged:: 1.27.2
            Added `insecure` and `cacert` parameters

        :param host: CloudVision hostname

        :param insecure:
            skip certificate verification

        :param cacert:
            path to CA certificate to use for verifying the host's certificate
        :type cacert: :class:`pathlib.Path` or str

        :rtype: AsyncCVClient
        """
        ssl_context = cls._get_ssl_context(host, port, cacert=cacert, insecure=insecure)
        return cls(token=token, ssl_context=ssl_context, port=port, host=host, username=username)

    @classmethod
    def from_user_credentials(cls, username, password, host, port=443,
                              insecure=False, cacert=None):
        """
        Use usename and password to authenticate in CloudVision

        .. note::
            With default parameters, it would assume that the host has a self-signed certificate and
            it will fetch it and verify hostname and expiry. It is recommended that you use
            CA signed certificate in your CloudVision deployment, so you'd either add this CA to
            the list of trusted CAs, or provide it's certificate via `cacert` parameter


        .. DANGER::
            Avoid setting `insecure=True` as this would disable certificate check

        .. versionchanged:: 1.27.2
            Added `insecure` and `cacert` parameters

        :param host: CloudVision hostname

        :param insecure:
            skip certificate verification

        :param cacert:
            path to CA certificate to use for verifying the host's certificate
        :type cacert: :class:`pathlib.Path` or str

        :rtype: AsyncCVClient
        :raises UnableToAuthenticateException:
        """

        headers = {
            "Authorization": f"Basic {b64encode(":".join((username, password)).encode()).decode()}",
        }
        try:
            context = cls._get_ssl_context(host, port, cacert=cacert, insecure=insecure)
            with urllib3.PoolManager(ssl_context=context) as pool:
                resp = pool.request('POST',
                                    f'https://{host}:{port}/cvpservice/login/authenticate.do',
                                    headers=headers)
                if resp.status != 200:
                    raise Exception(f"Status code {resp.status}: {resp.read()}")
                data = resp.json()
        except Exception as e:
            raise UnableToAuthenticateException(
                f"Unable to authenticate using user and password. Cause: {e}") from e

        # Apparently we can't reuse ssl context, so creating a new one
        context = cls._get_ssl_context(host, port, cacert=cacert, insecure=insecure)

        return cls(token=data['sessionId'], ssl_context=context, port=port,
                   host=host, username=username)

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
