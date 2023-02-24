# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Test grpc_client module."""


import pytest

from cloudvision import __version__ as version
from cloudvision.Connector.grpc_client import GRPCClient


class TestGRPCClient:
    @pytest.mark.parametrize(
        "channel_options",
        [
            [
                ("grpc.primary_user_agent", f"cloudvision.Connector/{version}"),
                ("grpc.keepalive_time_ms", 60000),
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
                },
                [
                    ("grpc.primary_user_agent", f"cloudvision.Connector/{version}"),
                    ("grpc.keepalive_time_ms", 30000),
                ],
            ),
            (
                {
                    "grpc.primary_user_agent": "torans_grpc_client",
                    "grpc.keepalive_time_ms": 1200000,
                },
                [
                    ("grpc.primary_user_agent", "torans_grpc_client"),
                    ("grpc.keepalive_time_ms", 1200000),
                ],
            ),
            (
                {
                    "grpc.primary_user_agent": "torans_grpc_client",
                    "grpc.keepalive_time_ms": 1200000,
                    "grpc.keepalive_timeout_ms": 10000,
                },
                [
                    ("grpc.primary_user_agent", "torans_grpc_client"),
                    ("grpc.keepalive_time_ms", 1200000),
                    ("grpc.keepalive_timeout_ms", 10000),
                ],
            ),
        ],
    )
    def test_channel_options_overrides(self, given, want):
        client = GRPCClient("localhost:443", channel_options=given)
        assert hasattr(client, "channel_options")
        got = client.channel_options
        assert sorted(got) == sorted(want)
