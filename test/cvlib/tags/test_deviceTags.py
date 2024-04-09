# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""tests for the template access to device class tags methods"""

import pytest

from cloudvision.cvlib import (
    Context,
    Device,
    Topology,
    Tags,
    Tag,
    TagErrorException,
    TagOperationException,
    TagMissingException,
    TagTooManyValuesException
)

from arista.tag.v2.services import (
    TagAssignmentServiceStub,
    TagAssignmentConfigServiceStub,
    TagAssignmentStreamResponse,
    TagAssignmentConfigStreamResponse
)
from arista.workspace.v1.services import (
    WorkspaceResponse
)


def convertListToStream(assignmentList):
    stream = []
    for assign in assignmentList:
        device, tag, value = assign
        item = TagAssignmentStreamResponse()
        item.value.key.device_id.value = device
        item.value.key.label.value = tag
        item.value.key.value.value = value
        stream.append(item)
    return stream


def convertListToConfigStream(assignmentConfigList):
    stream = []
    for assign in assignmentConfigList:
        device, tag, value, remove = assign
        item = TagAssignmentConfigStreamResponse()
        item.value.key.device_id.value = device
        item.value.key.label.value = tag
        item.value.key.value.value = value
        item.value.remove.value = remove
        stream.append(item)
    return stream


class mockStudio:
    def __init__(self):
        self.workspaceId = "workspace1"


class mockClient:
    def __init__(self):
        self.stub = None
        self.tagResponse = convertListToStream([])
        self.tagConfigResponse = convertListToConfigStream([])
        self.numGetAlls = 0
        self.numSets = 0

    def GetAll(self, request):
        labelFilters = []
        for afilter in request.partial_eq_filter:
            if afilter.key.label.value:
                labelFilters.append(afilter.key.label.value)
        if self.stub == TagAssignmentServiceStub:
            self.numGetAlls += 1
            response = self.tagResponse
        elif self.stub == TagAssignmentConfigServiceStub:
            self.numGetAlls += 1
            response = self.tagConfigResponse
        if labelFilters:
            for item in list(response):
                if item.value.key.label.value not in labelFilters:
                    response.remove(item)
        return response

    def GetOne(self, _):
        return WorkspaceResponse()

    def SetGetAllResponse(self, response):
        self.tagResponse = response

    def SetGetAllConfigResponse(self, response):
        self.tagConfigResponse = response

    def Set(self, request):
        self.numSets += 1
        return


class mockCtx(Context):
    def __init__(self):
        super().__init__('user')
        self.client = mockClient()
        self.studio = mockStudio()
        self.device = Device()

    def getApiClient(self, stub):
        self.client.stub = stub
        return self.client


getSingleTagCases = [
    # name
    # cached tags
    # tagv2 GetAll response
    # devices in topology
    # device to use
    # tag label
    # required
    # expected num GetAlls (includes mainline and workspace)
    # expected Tag
    # err
    [
        "get tag that is assigned correctly to device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        'DC',
        True,
        2,
        Tag('DC', 'DC1'),
        None
    ],
    [
        "get tag that is assigned to device with too many values",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC', 'DC2'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        'DC',
        True,
        2,
        None,
        TagTooManyValuesException('DC', 'J1', ['DC1', 'DC2'])
    ],
    [
        "get required tag that isn't assigned to device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        'Role',
        True,
        2,
        None,
        TagMissingException('Role', 'J1')
    ],
    [
        "get unrequired tag that isn't assigned to device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        'Leaf-Domain',
        False,
        2,
        None,
        None,
    ],
    [
        "try get required tag for device that has no tags",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J3',
        'DC',
        True,
        2,
        None,
        TagMissingException('DC', 'J3')
    ],
    [
        "try get unrequired tag for device that has no tags",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J3',
        'DC',
        False,
        2,
        None,
        None
    ],
    [
        "get tag that is assigned correctly to device with preloaded cache",
        {
            'J1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'J2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
        },
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        'DC',
        True,
        0,
        Tag('DC', 'DC1'),
        None
    ],
    [
        "get tag that is assigned to device with too many values with preloaded cache",
        {
            'J1': {'DC': ['DC1', 'DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'J2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
        },
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC', 'DC2'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        'DC',
        True,
        0,
        None,
        TagTooManyValuesException('DC', 'J1', ['DC1', 'DC2'])
    ],
]


@pytest.mark.parametrize('name, cacheTags, getAllResp, topoDevices, deviceId, label, '
                         + 'required, expNumGetAlls, expectedTag, expectedError',
                         getSingleTagCases)
def test_getSingleTag(name, cacheTags, getAllResp, topoDevices, deviceId, label,
                      required, expNumGetAlls, expectedTag, expectedError):
    atag = None
    error = None
    ctx = mockCtx()
    deviceMap = {}
    for dev in topoDevices:
        deviceMap[dev] = Device(deviceId=dev)
    topology = Topology(deviceMap)
    ctx.setTopology(topology)
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags._setRelevantTagAssigns(cacheTags)
    dev1 = topology.getDevices([deviceId])[0]
    try:
        atag = dev1.getSingleTag(ctx, label, required=required)
    except Exception as e:
        error = e
    if error or expectedError:
        assert str(error) == str(expectedError)
    else:
        assert atag == expectedTag
    assert ctx.client.numGetAlls == expNumGetAlls


getTagsCases = [
    # name
    # cached tags
    # tagv2 GetAll response
    # devices in topology
    # device to use
    # label
    # expected num GetAlls (includes mainline and workspace)
    # expected Tags
    # expected Error
    [
        "get all device tags for device that has tags",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        None,
        2,
        [Tag('DC', 'DC1'), Tag('DC-Pod', 'POD1'), Tag('NodeId', '1')],
        None
    ],
    [
        "get specific label device tags for device that has tags",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        'DC',
        2,
        [Tag('DC', 'DC1')],
        None
    ],
    [
        "get all device tags for dev3 that has no tags",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J3',
        None,
        2,
        [],
        None
    ],
    [
        "get specific label device tags for dev3 that has no tags",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J3',
        'DC',
        2,
        [],
        None
    ],
    [
        "get all device tags for device that has tags with preloaded cache",
        {
            'J1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'J2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
        },
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        None,
        0,
        [Tag('DC', 'DC1'), Tag('DC-Pod', 'POD1'), Tag('NodeId', '1')],
        None
    ],
]


@pytest.mark.parametrize('name, cacheTags, getAllResp, topoDevices, deviceId, label, '
                         + 'expNumGetAlls, expectedTags, expectedError', getTagsCases)
def test_getTags(name, cacheTags, getAllResp, topoDevices, deviceId, label,
                 expNumGetAlls, expectedTags, expectedError):
    error = None
    devTags = None
    ctx = mockCtx()
    deviceMap = {}
    for dev in topoDevices:
        deviceMap[dev] = Device(deviceId=dev)
    topology = Topology(deviceMap)
    ctx.setTopology(topology)
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags._setRelevantTagAssigns(cacheTags)
    dev1 = topology.getDevices([deviceId])[0]
    try:
        devTags = dev1.getTags(ctx, label=label)
    except Exception as e:
        error = e
    if error or expectedError:
        assert str(error) == str(expectedError)
    else:
        assert devTags == expectedTags
    assert ctx.client.numGetAlls == expNumGetAlls


assignTagsCases = [
    # name
    # cached tags
    # tagv2 GetAll response
    # devices in topology
    # device to use
    # tag
    # replace flag
    # expected num GetAlls (includes mainline and workspace)
    # expected num Sets (includes tag creation and assignment)
    # expected Tags
    # expected Error
    [
        "assign new tag to device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('Role', 'Spine'),
        False,
        2,
        2,
        [
            Tag('DC', 'DC1'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
            Tag('Role', 'Spine'),
        ],
        None
    ],
    [
        "assign a new value of existing label to device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('DC', 'DC2'),
        False,
        2,
        2,
        [
            Tag('DC', 'DC1'),
            Tag('DC', 'DC2'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        None
    ],
    [
        "replace value with new value of existing label for device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('DC', 'DC2'),
        True,
        2,
        3,
        [
            Tag('DC', 'DC2'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        None
    ],
    [
        "replace value with already assigned value of another device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('NodeId', '2'),
        True,
        2,
        2,
        [
            Tag('DC', 'DC1'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '2'),
        ],
        None
    ],
    [
        "assign already assigned tag to same device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('DC', 'DC1'),
        True,
        2,
        0,
        [
            Tag('DC', 'DC1'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        None
    ],
    [
        "assign tag with invalid label to device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('', 'Spine'),
        False,
        2,
        0,
        [
            Tag('DC', 'DC1'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        TagOperationException('', 'Spine', 'assign', 'J1')
    ],
    [
        "assign tag with invalid value to device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('DC', ''),
        True,
        2,
        0,
        [
            Tag('DC', 'DC1'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        TagOperationException('DC', '', 'assign', 'J1')
    ],
    [
        "assign new tag to device with preloaded cache",
        {
            'J1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'J2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
        },
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('Role', 'Spine'),
        False,
        0,
        2,
        [
            Tag('DC', 'DC1'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
            Tag('Role', 'Spine'),
        ],
        None
    ],
    [
        "replace value with new value of existing label for device with preloaded cache",
        {
            'J1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'J2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
        },
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('DC', 'DC2'),
        True,
        0,
        3,
        [
            Tag('DC', 'DC2'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        None
    ],
]


@pytest.mark.parametrize('name, cacheTags, getAllResp, topoDevices, deviceId, '
                         + 'tag, replace, expNumGetAlls, expNumSets, '
                         + 'expectedTags, expectedError', assignTagsCases)
def test_assignTags(name, cacheTags, getAllResp, topoDevices, deviceId,
                    tag, replace, expNumGetAlls, expNumSets,
                    expectedTags, expectedError):
    error = None
    devTags = None
    ctx = mockCtx()
    deviceMap = {}
    for dev in topoDevices:
        deviceMap[dev] = Device(deviceId=dev)
    topology = Topology(deviceMap)
    ctx.setTopology(topology)
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags._setRelevantTagAssigns(cacheTags)
    dev = topology.getDevices([deviceId])[0]
    try:
        dev._assignTag(ctx, tag, replaceValue=replace)
    except Exception as e:
        error = e
    devTags = dev.getTags(ctx)
    if error or expectedError:
        assert str(error) == str(expectedError)
    assert sorted(devTags) == sorted(expectedTags)
    assert ctx.client.numGetAlls == expNumGetAlls
    assert ctx.client.numSets == expNumSets


unassignTagsCases = [
    # name
    # cached tags
    # tagv2 GetAll response
    # devices in topology
    # device to use
    # tag
    # expected num GetAlls (includes mainline and workspace)
    # expected num Sets (includes tag creation and assignment)
    # expected Tags
    # expected Error
    [
        "unassign tag from device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('DC', 'DC1'),
        2,
        1,
        [
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        None
    ],
    [
        "unassign one of two values for a label from device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC', 'DC2'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('DC', 'DC2'),
        2,
        1,
        [
            Tag('DC', 'DC1'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        None
    ],
    [
        "unassign all values for a label from device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC', 'DC2'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('DC', ''),
        2,
        2,
        [
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        None
    ],
    [
        "unassign a value that's not assigned for a label from device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('DC', 'DC2'),
        2,
        0,
        [
            Tag('DC', 'DC1'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        None
    ],
    [
        "unassign a tag that's not assigned from device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('Role', ''),
        2,
        0,
        [
            Tag('DC', 'DC1'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        None
    ],
    [
        "unassign tag with invalid label from device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag(None, None),  # type: ignore
        2,
        0,
        [
            Tag('DC', 'DC1'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        TagOperationException('', '', 'unassign', 'J1')
    ],
    [
        "unassign tag with invalid label and valid value from device",
        None,
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag(None, 'Spine'),  # type: ignore
        2,
        0,
        [
            Tag('DC', 'DC1'),
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        TagOperationException(None, 'Spine', 'unassign', 'J1')  # type: ignore
    ],
    [
        "unassign tag from device with preloaded cache",
        {
            'J1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'J2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
        },
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('DC', 'DC1'),
        0,
        1,
        [
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        None
    ],
    [
        "unassign all values for a label from device with preloaded cache",
        {
            'J1': {'DC': ['DC1', 'DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'J2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
        },
        convertListToStream([('J1', 'DC', 'DC1'),
                             ('J1', 'DC', 'DC2'),
                             ('J1', 'DC-Pod', 'POD1'),
                             ('J1', 'NodeId', '1'),
                             ('J2', 'DC', 'DC1'),
                             ('J2', 'DC-Pod', 'POD1'),
                             ('J2', 'NodeId', '2'),
                             ]),
        ['J1', 'J2', 'J3'],
        'J1',
        Tag('DC', ''),
        0,
        2,
        [
            Tag('DC-Pod', 'POD1'),
            Tag('NodeId', '1'),
        ],
        None
    ],
]


@pytest.mark.parametrize('name, cacheTags, getAllResp, topoDevices, deviceId, '
                         + 'tag, expNumGetAlls, expNumSets, expectedTags, '
                         + 'expectedError', unassignTagsCases)
def test_unassignTags(name, cacheTags, getAllResp, topoDevices, deviceId,
                      tag, expNumGetAlls, expNumSets, expectedTags,
                      expectedError):
    error = None
    devTags = None
    ctx = mockCtx()
    deviceMap = {}
    for dev in topoDevices:
        deviceMap[dev] = Device(deviceId=dev)
    topology = Topology(deviceMap)
    ctx.setTopology(topology)
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags._setRelevantTagAssigns(cacheTags)
    dev = topology.getDevices([deviceId])[0]
    try:
        dev._unassignTag(ctx, tag)
    except Exception as e:
        error = e
    devTags = dev.getTags(ctx)
    if error or expectedError:
        assert str(error) == str(expectedError)
    assert sorted(devTags) == sorted(expectedTags)
    assert ctx.client.numGetAlls == expNumGetAlls
    assert ctx.client.numSets == expNumSets
