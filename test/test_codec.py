# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""basic test that converted and encoded types are handled correctly."""

import os.path

from cloudvision.Connector.codec import Decoder, Encoder, Float32, FrozenDict
from cloudvision.Connector.codec.custom_types import Path

import numpy as np

import pytest


import yaml

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


def group(it, n):  # noqa: D401
    """Groups together dictionaries."""
    return zip(*[iter(it)] * n)


def make_complex(pairs):
    """make_complex creates a complex dictionary using a list of pairs."""
    res = {}
    for k, v in group(pairs, 2):
        if isinstance(k, dict):
            k = FrozenDict(k)
        res[k] = v
    return FrozenDict(res)


def identity(x):
    return x  # noqa: E731


preprocessing = {
    "bool": identity,
    "i8": identity,
    "i16": identity,
    "i32": identity,
    "i64": int,
    "f32": lambda x: Float32(np.float32(x)),
    "f64": float,
    "str": identity,
    "bytes": bytes,
    "array": identity,
    "map": lambda x: FrozenDict(x),
    "complex": make_complex,
    "pointer": lambda x: Path(keys=x),
    "nil": lambda x: None
}

encoder = Encoder()
decoder = Decoder()
cases = []

with open(os.path.join(TEST_DIR, "test_codec.yml"), "r") as file:
    test_dict = yaml.load(file.read(), Loader=yaml.FullLoader)

for test, i in zip(test_dict["tests"], range(len(test_dict["tests"]))):
    test_type, test_val = next(((key, val) for key, val in test.items()
                                if key not in ('name', 'out')))
    test_val = preprocessing[test_type](test_val)  # type: ignore
    cases.append([test["name"], test_val, bytes(test["out"])])


@pytest.mark.parametrize('name, inp, expected', cases)
def test_encode_decode(name, inp, expected):
    """Test whether values are encoded and decoded correctly."""
    res = encoder.encode(inp)
    if res != expected:
        assert res == expected, "Bad encoding for %s Got %s expected %s" \
            % (name, res, expected)
    rev = decoder.decode(res)
    if rev != inp:
        failed = True
        if isinstance(inp, bytes):
            # NEAT doesn't distinguish z/w byte/string change to string and check
            inp = str(inp, 'ascii')
            failed = rev != inp

        assert not failed, "decoding value did not match input value"
