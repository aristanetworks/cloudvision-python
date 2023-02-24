# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Test utility module."""


import pytest

from cloudvision.Connector.core.utils import get_dict


class TestUtils:
    @pytest.mark.parametrize(
        "whatever, want",
        [
            (None, {}),
            (1, {}),
            ("string", {}),
            ([1, 2], {}),
            ((1, 2), {}),
            ({}, {}),
            ({"a": 1}, {"a": 1}),
        ],
    )
    def test_get_dict(self, whatever, want):
        got = get_dict(whatever)
        assert got == want

    @pytest.mark.parametrize(
        "whatever, default, want",
        [
            (None, None, None),
            (1, None, None),
            ("string", None, None),
            ([1, 2], None, None),
            ((1, 2), None, None),
            ({}, None, {}),
            ({}, {}, {}),
            ({"a": 1}, {}, {"a": 1}),
            ({"a": 1}, None, {"a": 1}),
        ],
    )
    def test_get_dict_with_default(self, whatever, default, want):
        got = get_dict(whatever, default)
        assert got == want
