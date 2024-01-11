# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""tests for the custom data methods"""

import math
import random
import string

import pytest

from cloudvision.Connector import codec
from cloudvision.Connector.codec import Path
from cloudvision.cvlib import Context, StudioCustomData


class mockStudio:
    def __init__(self):
        self.studioId = "studio1"
        self.workspaceId = "workspace1"
        self.buildId = "build1"


class mockWorkspace:
    def __init__(self):
        self.id = "workspace1"
        self.buildId = "build1"


class mockClient:
    def __init__(self, expPaths):
        self.stub = None
        self.numGetAlls = 0
        self.expPaths = expPaths
        self.dataWritten = dict()

    def publish(self, dId, notifs):
        d = codec.Decoder()
        createdPaths = {}

        for n in notifs:
            for u in n.updates:
                createdPaths[d.decode(u.key)] = d.decode(u.value)

        for k, v in createdPaths.items():
            if isinstance(v, Path):
                expPath = Path(keys=self.expPaths[k])
                assert expPath == v
            else:
                self.dataWritten[k] = v


class mockCtx(Context):
    def __init__(self, client):
        super().__init__('user')
        self.client = client
        self.studio = mockStudio()
        self.workspace = mockWorkspace()

    def getApiClient(self, stub):
        self.client.stub = stub
        return self.client

    def getCvClient(self):
        return self.client

    def Get(self, path, keys, dataset):

        expPaths = (self.client.expPaths["key"] if self.workspace
                    else self.client.expPaths["key"][5:])
        assert path == expPaths
        return self.client.dataWritten


cases = [
    [
        ''.join(random.choices(string.ascii_lowercase, k=15 * 1024 * 1024)),
        ["path1", "path2"],
        "key",
        {
            "studio": ["workspace", "workspace1", "status", "build", "build1",
                       "studio"],
            "studio1": ["workspace", "workspace1", "status", "build", "build1",
                        "studio", "studio1"],
            "customData": ["workspace", "workspace1", "status", "build", "build1",
                           "studio", "studio1", "customData"],
            "path1": ["workspace", "workspace1", "status", "build", "build1",
                      "studio", "studio1", "customData", "path1"],
            "path2": ["workspace", "workspace1", "status", "build", "build1",
                      "studio", "studio1", "customData", "path1", "path2"],
            "key": ["workspace", "workspace1", "status", "build", "build1",
                    "studio", "studio1", "customData", "path1", "path2", "key"]},
    ]
]


@pytest.mark.parametrize('data, path, key, expPaths', cases)
def test_studioCustomData(data, path, key, expPaths):
    client = mockClient(expPaths)
    ctx = mockCtx(client)
    cd = StudioCustomData(ctx)
    cd.store(data, path, key)
    assert len(client.dataWritten.keys()) == math.ceil(len(data) / cd.chunk_size)
    assert data == cd.retrieve('studio1', path, key)
    # verify if the data is read from mainline when
    # context doesnt have workspace
    ctx.studio = None
    ctx.workspace = None
    assert data == cd.retrieve('studio1', path, key)
