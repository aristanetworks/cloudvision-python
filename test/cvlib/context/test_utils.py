# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest

from cloudvision.cvlib.utils import doSHA512Hashing, doType7Obfuscation


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


type7ObfuscationCases = [
    # Success cases (exception=False)
    pytest.param("", 0, None, "", False, id="empty_input"),
    pytest.param("password", 10, None, "105E080A16001D1908", False, id="base_case"),
    pytest.param("password", 0, None, "00141215174C04140B", False, id="salt_zero"),
    pytest.param("password", 15, None, "15020A1F173D24362C", False, id="salt_fifteen"),
    pytest.param("茶", 10, None, "10C6E5CF", False, id="unicode_input"),
    pytest.param(
        "password",
        10,
        "ABCDEFGHIJKLMNOPQRST",
        "103B2D3E3D383F2336",
        False,
        id="custom_obfuscator",
    ),
    pytest.param(
        "password",
        10,
        "茶",
        "10FCD79BFFC187FED2",
        False,
        id="unicode_obfuscator",
    ),
    # Error cases (exception=True)
    pytest.param(
        "password",
        -1,
        None,
        "Salt must be between 0 and 15",
        True,
        id="salt_negative",
    ),
    pytest.param(
        "password",
        16,
        None,
        "Salt must be between 0 and 15",
        True,
        id="salt_too_large",
    ),
]


@pytest.mark.parametrize("input, salt, obf, expected, exception", type7ObfuscationCases)
def test_type7_obfuscation(input, salt, obf, expected, exception):
    if exception:
        with pytest.raises(ValueError) as exc_info:
            doType7Obfuscation(input, salt, obf)
        assert expected in str(exc_info.value), "Unexpected exception"
    else:
        actual = doType7Obfuscation(input, salt, obf)
        assert actual == expected, "Response is not expected"
