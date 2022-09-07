# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import msgpack
import io
from cloudvision.Connector.codec import Float32, PointerType, WildcardType
from cloudvision.Connector.codec import Wildcard, Path, FrozenDict


class Encoder(object):

    def __init__(self):
        self.__packer = msgpack.Packer(use_single_float=False)
        self.__buffer = io.BytesIO()

    def encode_string(self, s):
        return self.__packer.pack(bytes(s, 'utf-8', 'replace'))

    def encode_array(self, a):
        res = b""
        res += self.__packer.pack_array_header(len(a))
        res += b"".join(self.encode(val) for val in a)
        return res

    def encode_map(self, m):
        res = b""
        res += self.__packer.pack_map_header(len(m))
        dictItems = []
        for k, v in m.items():
            buf = b"".join((self.encode(k), self.encode(v)))
            dictItems.append(buf)
        res += b"".join(sorted(dictItems))
        return res

    def encode(self, val):
        res = b""
        if isinstance(val, str):
            res = self.encode_string(val)
        elif isinstance(val, Float32):
            res = msgpack.packb(val, use_single_float=True)
        elif isinstance(val, list):
            res = self.encode_array(val)
        elif isinstance(val, (dict, FrozenDict)):
            res = self.encode_map(val)
        elif isinstance(val, Wildcard):
            res = self.__packer.pack(msgpack.ExtType(
                WildcardType, b""))
        elif isinstance(val, Path):
            keys = self.encode(val._keys)
            res = self.__packer.pack(msgpack.ExtType(
                PointerType, keys))
        else:
            res = self.__packer.pack(val)
        return res
