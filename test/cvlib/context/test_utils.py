# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest

from cloudvision.cvlib.utils import doSHA512Hashing


sha512Cases = [
    pytest.param("", "salt", "", id="empty_input"),
    pytest.param(
        "foo",
        "salt",
        (
            "$6$salt$H5FBI1kANxAmVY5sDfxluSqO9sW8Xdcsr"
            "JNjZbASdPorb44XAobhsMA2pNh4U8FT4GRSmxBj0gLvIQrIw948p/"
        ),
        id="base_case",
    ),
    pytest.param(
        "foo",
        "salt%!~",
        (
            "$6$salt$H5FBI1kANxAmVY5sDfxluSqO9sW8Xdcsr"
            "JNjZbASdPorb44XAobhsMA2pNh4U8FT4GRSmxBj0gLvIQrIw948p/"
        ),
        id="salt_needs_sanitizing",
    ),
]


@pytest.mark.parametrize("input, salt, expected", sha512Cases)
def test_sha512_hashing(input, salt, expected):
    actual = doSHA512Hashing(input, salt)
    assert actual == expected
