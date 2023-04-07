# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import json
from cloudvision.Connector.codec import Path, FrozenDict
from google.protobuf.timestamp_pb2 import Timestamp


def pretty_print(dataDict):
    def default(obj):
        if isinstance(obj, Path):
            return obj._keys
        if isinstance(obj, (FrozenDict, dict)):
            return obj._dict
        if isinstance(obj, Timestamp):
            return obj.ToNanoseconds()
    print(json.dumps(
        dataDict, default=default, indent=4,
        sort_keys=True, separators=(",", ":")
    ))
