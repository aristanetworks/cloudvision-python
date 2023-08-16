# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""tests for the template access to Context class tags methods"""

import pytest

from cloudvision.cvlib import (
    Context,
    Device,
    Topology,
    Tags,
    Tag
)

from arista.tag.v2.services import (
    TagAssignmentServiceStub,
    TagAssignmentConfigServiceStub,
    TagAssignmentStreamResponse,
    TagAssignmentConfigStreamResponse
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


class mockWorkspace:
    def __init__(self):
        self.id = "1"


class mockClient:
    def __init__(self):
        self.stub = None
        self.tagResponse = convertListToStream([])
        self.tagConfigResponse = convertListToConfigStream([])
        self.numGetAlls = 0

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

    def SetGetAllResponse(self, response):
        self.tagResponse = response

    def SetGetAllConfigResponse(self, response):
        self.tagConfigResponse = response

    def Set(self, request):
        return


class mockCtx(Context):
    def __init__(self):
        super().__init__('user')
        self.client = mockClient()
        self.studio = mockStudio()
        self.workspace = mockWorkspace()
        self.device = Device()

    def getApiClient(self, stub):
        self.client.stub = stub
        return self.client


getAllDeviceTagsCases = [
    # name
    # original filter
    # new filter
    # preloaded tags
    # validateFunc
    # tagv2 GetAll response
    # num GetAll calls
    # expected tags
    # expected error
    [
        "pre-existing cache",
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1']},
        },
        None,
        [],
        0,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1']},
        },
        None
    ],
    [
        "no pre-existing cache",
        {
        },
        None,
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ]),
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
        },
        None
    ],
]


@pytest.mark.parametrize('name, cacheTags, validateFunc, getAllResp, '
                         + 'expNumGetAlls, expectedTags, expectedError',
                         getAllDeviceTagsCases)
def test_getAllDeviceTags(name, cacheTags, validateFunc, getAllResp,
                          expNumGetAlls, expectedTags, expectedError):
    error = None
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags._setRelevantTagAssigns(cacheTags)
    try:
        allTags = ctx.tags._getAllDeviceTags()
    except Exception as e:
        error = e
    if error or expectedError:
        assert str(error) == str(expectedError)
    assert allTags == expectedTags
    assert ctx.client.numGetAlls == expNumGetAlls


getDeviceTagsCases = [
    # name
    # cached tags
    # tagv2 GetAll response
    # device id
    # num GetAll calls
    # expected tags
    # expected error
    [
        "preloaded tags",
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
        },
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ]),
        'dev1',
        0,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        None
    ],
    [
        "preloaded tags, device has no tags",
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
        },
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ]),
        'dev3',
        0,
        {},
        None
    ],
    [
        "no preloaded tags",
        {
        },
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ]),
        'dev1',
        2,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        None
    ],
    [
        "no preloaded tags, device has no tags",
        {
        },
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ]),
        'dev3',
        2,
        {},
        None
    ],
]


@pytest.mark.parametrize('name, cacheTags, getAllResp, deviceId, '
                         + 'expNumGetAlls, expectedTags, expectedError',
                         getDeviceTagsCases)
def test_getDeviceTags(name, cacheTags, getAllResp, deviceId,
                       expNumGetAlls, expectedTags, expectedError):
    error = None
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags._setRelevantTagAssigns(cacheTags)
    try:
        devTags = ctx.tags._getDeviceTags(deviceId)
    except Exception as e:
        error = e
    if error or expectedError:
        assert str(error) == str(expectedError)
    assert devTags == expectedTags
    assert ctx.client.numGetAlls == expNumGetAlls


assignUnassignDeviceTagCases = [
    # name
    # tagv2 GetAll response
    # device id
    # operation ('assign', 'unassign')
    # operation tag label
    # operation tag value
    # replace flag
    # num GetAll calls
    # expected tags
    # expected error
    [
        "assign additional Role tag value",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        'dev1',
        'assign',
        'Role',
        'Core',
        False,
        2,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'], 'Role':['Spine', 'Core']},
        None
    ],
    [
        "assign replacement Role tag value",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        'dev1',
        'assign',
        'Role',
        'Core',
        True,
        2,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'], 'Role':['Core']},
        None
    ],
    [
        "unassign second Role tag value",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev1', 'Role', 'Core'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        'dev1',
        'unassign',
        'Role',
        'Core',
        False,
        2,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'], 'Role':['Spine']},
        None
    ],
    [
        "unassign last Role tag value",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        'dev1',
        'unassign',
        'Role',
        'Spine',
        False,
        2,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        None
    ],
    [
        "unassign tag value that's not assigned",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        'dev1',
        'unassign',
        'Role',
        'Core',
        False,
        2,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'], 'Role':['Spine']},
        None
    ],
]


@pytest.mark.parametrize('name, getAllResp, deviceId, oper, operLabel, operValue, '
                         + 'replace, expNumGetAlls, expectedTags, expectedError',
                         assignUnassignDeviceTagCases)
def test_changeDeviceTags(name, getAllResp, deviceId, oper, operLabel, operValue,
                          replace, expNumGetAlls, expectedTags, expectedError):
    error = None
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(getAllResp)
    try:
        if oper == 'assign':
            ctx.tags._assignDeviceTag(deviceId, operLabel, operValue,
                                      replaceValue=replace)
        elif oper == 'unassign':
            ctx.tags._unassignDeviceTag(deviceId, operLabel, operValue)
    except Exception as e:
        error = e
    devTags = ctx.tags._getDeviceTags(deviceId)
    if error or expectedError:
        assert str(error) == str(expectedError)
    assert devTags == expectedTags
    assert ctx.client.numGetAlls == expNumGetAlls


mergeGetAllDeviceTagsCases = [
    # name
    # mainline state response
    # workspace config response
    # expected tags
    # expected error
    [
        "no workspace updates",
        convertListToStream([
                            ('dev1', 'DC', 'DC1'),
                            ('dev1', 'DC-Pod', 'POD1'),
                            ('dev1', 'NodeId', '1'),
                            ('dev1', 'Role', 'Spine'),
                            ('dev2', 'DC', 'DC1'),
                            ('dev2', 'DC-Pod', 'POD1'),
                            ('dev2', 'NodeId', '2'),
                            ('dev2', 'Role', 'Leaf'),
                            ]),
        convertListToConfigStream([]),
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'], 'Role':['Spine']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'], 'Role':['Leaf']},
        },
        None
    ],
    [
        "no mainline tags",
        convertListToStream([]),
        convertListToConfigStream([
                                  ('dev1', 'DC', 'DC1', False),
                                  ('dev1', 'DC-Pod', 'POD1', False),
                                  ('dev1', 'NodeId', '1', False),
                                  ('dev1', 'Role', 'Spine', False),
                                  ('dev2', 'DC', 'DC1', False),
                                  ('dev2', 'DC-Pod', 'POD1', False),
                                  ('dev2', 'NodeId', '2', False),
                                  ('dev2', 'Role', 'Leaf', False),
                                  ]),
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'], 'Role':['Spine']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'], 'Role':['Leaf']},
        },
        None
    ],
    [
        "mainline with workspace remove",
        convertListToStream([
                            ('dev1', 'DC', 'DC1'),
                            ('dev1', 'DC-Pod', 'POD1'),
                            ('dev1', 'NodeId', '1'),
                            ('dev1', 'Role', 'Spine'),
                            ('dev2', 'DC', 'DC1'),
                            ('dev2', 'DC-Pod', 'POD1'),
                            ('dev2', 'NodeId', '2'),
                            ('dev2', 'Role', 'Leaf'),
                            ]),
        convertListToConfigStream([
                                  ('dev1', 'Role', 'Spine', True),
                                  ]),
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'], 'Role':['Leaf']},
        },
        None
    ],
    [
        "mainline with workspace add",
        convertListToStream([
                            ('dev1', 'DC', 'DC1'),
                            ('dev1', 'DC-Pod', 'POD1'),
                            ('dev1', 'NodeId', '1'),
                            ('dev2', 'DC', 'DC1'),
                            ('dev2', 'DC-Pod', 'POD1'),
                            ('dev2', 'NodeId', '2'),
                            ('dev2', 'Role', 'Leaf'),
                            ]),
        convertListToConfigStream([
                                  ('dev1', 'Role', 'Spine', False),
                                  ]),
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'], 'Role':['Spine']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'], 'Role':['Leaf']},
        },
        None
    ],
    [
        "mainline with workspace add/remove",
        convertListToStream([
                            ('dev1', 'DC', 'DC1'),
                            ('dev1', 'DC-Pod', 'POD1'),
                            ('dev1', 'NodeId', '1'),
                            ('dev1', 'Role', 'Spine'),
                            ('dev2', 'DC', 'DC1'),
                            ('dev2', 'DC-Pod', 'POD1'),
                            ('dev2', 'NodeId', '2'),
                            ('dev2', 'Role', 'Leaf'),
                            ]),
        convertListToConfigStream([
                                  ('dev1', 'Role', 'Spine', True),
                                  ('dev1', 'Role', 'Leaf', False),
                                  ]),
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'], 'Role':['Leaf']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'], 'Role':['Leaf']},
        },
        None
    ],
    [
        "mainline with workspace remove all for a device",
        convertListToStream([
                            ('dev1', 'DC', 'DC1'),
                            ('dev1', 'DC-Pod', 'POD1'),
                            ('dev1', 'NodeId', '1'),
                            ('dev1', 'Role', 'Spine'),
                            ('dev2', 'DC', 'DC1'),
                            ('dev2', 'DC-Pod', 'POD1'),
                            ('dev2', 'NodeId', '2'),
                            ('dev2', 'Role', 'Leaf'),
                            ]),
        convertListToConfigStream([
                                  ('dev1', 'DC', 'DC1', True),
                                  ('dev1', 'DC-Pod', 'POD1', True),
                                  ('dev1', 'NodeId', '1', True),
                                  ('dev1', 'Role', 'Spine', True),
                                  ]),
        {
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'], 'Role':['Leaf']},
        },
        None
    ],
    [
        "mainline with workspace add for new device",
        convertListToStream([
                            ('dev2', 'DC', 'DC1'),
                            ('dev2', 'DC-Pod', 'POD1'),
                            ('dev2', 'NodeId', '2'),
                            ('dev2', 'Role', 'Leaf'),
                            ]),
        convertListToConfigStream([
                                  ('dev1', 'DC', 'DC1', False),
                                  ('dev1', 'DC-Pod', 'POD1', False),
                                  ('dev1', 'NodeId', '1', False),
                                  ('dev1', 'Role', 'Spine', False),
                                  ]),
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'], 'Role':['Spine']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'], 'Role':['Leaf']},
        },
        None
    ],
]


@pytest.mark.parametrize('name, mainlineStateResp, workspaceConfigResp, '
                         + 'expectedTags, expectedError', mergeGetAllDeviceTagsCases)
def test_mergeTags(name, mainlineStateResp, workspaceConfigResp,
                   expectedTags, expectedError):
    error = None
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(mainlineStateResp)
    ctx.client.SetGetAllConfigResponse(workspaceConfigResp)
    try:
        allTags = ctx.tags._getAllDeviceTags()
    except Exception as e:
        error = e
    if error or expectedError:
        assert str(error) == str(expectedError)
    assert allTags == expectedTags


getDevicesByTagCases = [
    # name
    # cached tags
    # tagv2 GetAll response
    # devices in topology
    # tag
    # topology flag
    # num GetAll calls
    # expected devices
    # expected Error
    [
        "get devices matching label with preloaded cache",
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
            'dev3': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        },
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev3', 'DC', 'DC2'),
                             ('dev3', 'DC-Pod', 'POD1'),
                             ('dev3', 'NodeId', '1'),
                             ]),
        ['dev1', 'dev2', 'dev3'],
        Tag('DC', ''),
        True,
        0,
        [Device('dev1'), Device('dev2'), Device('dev3')],
        None
    ],
    [
        "try get devices not matching label with preloaded cache",
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
            'dev3': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        },
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev3', 'DC', 'DC2'),
                             ('dev3', 'DC-Pod', 'POD1'),
                             ('dev3', 'NodeId', '1'),
                             ]),
        ['dev1', 'dev2', 'dev3'],
        Tag('Role', ''),
        True,
        0,
        [],
        None
    ],
    [
        "get devices matching label and value with preloaded cache",
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
            'dev3': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        },
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev3', 'DC', 'DC2'),
                             ('dev3', 'DC-Pod', 'POD1'),
                             ('dev3', 'NodeId', '1'),
                             ]),
        ['dev1', 'dev2', 'dev3'],
        Tag('DC', 'DC1'),
        True,
        0,
        [Device('dev1'), Device('dev2')],
        None
    ],
    [
        "get devices in topology matching label and value with preloaded cache",
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
            'dev3': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        },
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev3', 'DC', 'DC2'),
                             ('dev3', 'DC-Pod', 'POD1'),
                             ('dev3', 'NodeId', '1'),
                             ]),
        ['dev1', 'dev3'],
        Tag('DC', 'DC1'),
        True,
        0,
        [Device('dev1')],
        None
    ],
    [
        "get devices not in topology matching label and value with preloaded cache",
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
            'dev3': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        },
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev3', 'DC', 'DC2'),
                             ('dev3', 'DC-Pod', 'POD1'),
                             ('dev3', 'NodeId', '1'),
                             ]),
        ['dev1', 'dev3'],
        Tag('DC', 'DC1'),
        False,
        0,
        [Device('dev1'), Device('dev2')],
        None
    ],
    [
        "try get devices with None label and value with preloaded cache",
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']},
            'dev3': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        },
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev3', 'DC', 'DC2'),
                             ('dev3', 'DC-Pod', 'POD1'),
                             ('dev3', 'NodeId', '1'),
                             ]),
        ['dev1', 'dev2', 'dev3'],
        Tag('', 'DC1'),
        True,
        0,
        [],
        None
    ],
    [
        "get devices matching label without preloaded cache",
        {
        },
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ]),
        ['dev1', 'dev2'],
        Tag('DC', ''),
        True,
        2,
        [Device('dev1'), Device('dev2')],
        None
    ],
    [
        "try get devices not matching label without preloaded cache",
        {
        },
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ]),
        ['dev1', 'dev2'],
        Tag('Role', ''),
        True,
        2,
        [],
        None
    ],
]


@pytest.mark.parametrize('name, cacheTags, getAllResp, topoDevices, tag, '
                         + 'topoFlag, expNumGetAlls, expectedDevices, expectedError',
                         getDevicesByTagCases)
def test_getDevicesByTag(name, cacheTags, getAllResp, topoDevices, tag,
                         topoFlag, expNumGetAlls, expectedDevices, expectedError):
    error = None
    ctx = mockCtx()
    deviceMap = {}
    for dev in topoDevices:
        deviceMap[dev] = Device(deviceId=dev)
    topology = Topology(deviceMap)
    ctx.setTopology(topology)
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags._setRelevantTagAssigns(cacheTags)
    try:
        devices = ctx.getDevicesByTag(tag, inTopology=topoFlag)
    except Exception as e:
        error = e
    if error or expectedError:
        assert str(error) == str(expectedError)
    assert devices == expectedDevices
    assert ctx.client.numGetAlls == expNumGetAlls
