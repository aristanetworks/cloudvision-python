# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""basic test that converted and encoded types are handled correctly."""

import os.path

from cloudvision.Connector.codec import Decoder, Encoder, Float32, FrozenDict
from cloudvision.Connector.codec.custom_types import Path

import numpy as np

import pytest
import json

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
            inp = str(inp, 'utf-8')
            failed = rev != inp

        assert not failed, "decoding value did not match input value"


def test_decode_breaking_values():
    decodeTcs = [
        {
            # Github Issue 10 BGP field decoding 'sentOpenMsg' decoding example
            "in": b'\xc4$\x04\xfeW\x00\xb4\xac\x14\xfcK\x1a\x02\x18\x01\x04\x00\x01\x00\x01'
            + b'\x02\x00@\x02A,A\x04\x00\x00\xfeWE\x04\x00\x01\x01\x01',
            "exp": '\x04�W\x00��\x14�K\x1a\x02\x18\x01\x04\x00\x01\x00\x01'
            + '\x02\x00@\x02A,A\x04\x00\x00�WE\x04\x00\x01\x01\x01',
            # Expected json is the golang encoded value taken from the same path using apish
            # to ensure that the outputs are consistent
            "exp_json": "{\"value\": \"\\u0004\\ufffdW\\u0000\\ufffd\\ufffd\\u0014\\ufffdK\\u001a"
            + "\\u0002\\u0018\\u0001\\u0004\\u0000\\u0001\\u0000\\u0001\\u0002\\u0000@\\u0002A,A"
            + "\\u0004\\u0000\\u0000\\ufffdWE\\u0004\\u0000\\u0001\\u0001\\u0001\"}"
        },
    ]
    for tc in decodeTcs:
        input = tc["in"]
        exp = tc["exp"]
        out = decoder.decode(bytes(input))
        assert out == exp, f"Bad decoding of {input}\nGot: '{out}'\nExp: '{exp}'"
        out_json = json.JSONEncoder(ensure_ascii=True).encode({"value": out})
        exp_json = tc["exp_json"]
        assert out_json == exp_json, (f"Unexpected json decoding of {input}\n"
                                      f"Got: '{out_json}'\n"
                                      f"Exp: '{exp_json}'")
