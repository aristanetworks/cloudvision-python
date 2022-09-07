# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import msgpack
from .custom_types import Wildcard, WildcardType, FrozenDict, PointerType, Path
__all__ = ["Decoder"]


def pair_hook(data):
    res = FrozenDict({
        FrozenDict(k) if isinstance(k, dict) else k: v
        for k, v in data
    })
    return res


def ext_hook(code, data):
    decoder = Decoder()
    if code == PointerType:
        return Path(keys=decoder.decode(data))
    elif code == WildcardType:
        return Wildcard()
    return msgpack.ExtType(code, data)


class Decoder(object):

    def __init__(self):
        self.__unpacker = msgpack.Unpacker(strict_map_key=False,
                                           object_pairs_hook=pair_hook,
                                           ext_hook=ext_hook)

    def decode_array(self, arr):
        return [self.__postProcess(v) for v in arr]

    def decode_map(self, m):
        return FrozenDict({
            self.__postProcess(k): self.__postProcess(v)
            for k, v in m.items()
        })

    def __postProcess(self, b):
        if isinstance(b, bytes):
            return b.decode('utf-8', 'replace')
        elif isinstance(b, list):
            return self.decode_array(b)
        elif isinstance(b, (dict, FrozenDict)):
            return self.decode_map(b)
        else:
            return b

    def decode(self, buf):
        self.__unpacker.feed(buf)
        res = self.__unpacker.unpack()
        return self.__postProcess(res)
