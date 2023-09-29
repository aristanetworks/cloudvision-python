# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Test grpc_client module."""


import pytest

from cloudvision import __version__ as version
from cloudvision.Connector.grpc_client import GRPCClient
from cloudvision.Connector.gen import router_pb2 as rtr


class TestGRPCClient:
    @pytest.mark.parametrize(
        "channel_options",
        [
            [
                ("grpc.primary_user_agent", f"cloudvision.Connector/{version}"),
                ("grpc.keepalive_time_ms", 60000),
                ('grpc.http2.max_pings_without_data', 0),
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
                    'grpc.http2.max_pings_without_data': 0,
                },
                [
                    ("grpc.primary_user_agent", f"cloudvision.Connector/{version}"),
                    ("grpc.keepalive_time_ms", 30000),
                    ('grpc.http2.max_pings_without_data', 0),
                ],
            ),
            (
                {
                    "grpc.primary_user_agent": "torans_grpc_client",
                    "grpc.keepalive_time_ms": 1200000,
                    'grpc.http2.max_pings_without_data': 0,
                },
                [
                    ("grpc.primary_user_agent", "torans_grpc_client"),
                    ("grpc.keepalive_time_ms", 1200000),
                    ('grpc.http2.max_pings_without_data', 0),
                ],
            ),
            (
                {
                    "grpc.primary_user_agent": "torans_grpc_client",
                    "grpc.keepalive_time_ms": 1200000,
                    "grpc.keepalive_timeout_ms": 10000,
                    'grpc.http2.max_pings_without_data': 1,
                },
                [
                    ("grpc.primary_user_agent", "torans_grpc_client"),
                    ("grpc.keepalive_time_ms", 1200000),
                    ("grpc.keepalive_timeout_ms", 10000),
                    ('grpc.http2.max_pings_without_data', 1),
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
        schema = [rtr.IndexField(name="FieldName1", type=rtr.INTEGER),
                  rtr.IndexField(name="FieldName1", type=rtr.FLOAT)]
        d_type = "device"
        delete_after_days = 50
        request = client.create_custom_schema_index_request(
            d_name, path_elements, schema, delete_after_days, d_type)
        assert len(request.schema) == len(schema)
        for idx, fieldSchema in enumerate(request.schema):
            assert fieldSchema == schema[idx]
        assert request.option.delete_after_days == delete_after_days
        assert request.query.dataset.name == d_name
        assert request.query.dataset.type == d_type
        assert len(request.query.paths) == 1
        path = request.query.paths[0]
        for idx, path_element in enumerate([client.encoder.encode(x) for x in path_elements]):
            assert path_element == path.path_elements[idx]
