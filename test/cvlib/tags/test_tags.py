# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""tests for the template access to Context class tags methods"""

import pytest

from cloudvision.cvlib import (
    Context,
    Device,
    Interface,
    Topology,
    Tags,
    Tag
)

from arista.tag.v2.services import (
    TagAssignmentServiceStub,
    TagAssignmentConfigServiceStub,
    TagAssignmentStreamResponse,
    TagAssignmentConfigStreamResponse,
    TagAssignmentConfigSetSomeResponse,
    TagConfigServiceStub,
    TagConfigSetSomeResponse
)
from arista.workspace.v1.services import (
    WorkspaceResponse
)


def convertListToStream(assignmentList):
    stream = []
    for assign in assignmentList:
        item = TagAssignmentStreamResponse()
        if len(assign) == 3:
            device, tag, value = assign
            item.value.key.device_id.value = device
            item.value.key.label.value = tag
            item.value.key.value.value = value
        elif len(assign) == 4:
            device, interface, tag, value = assign
            item.value.key.device_id.value = device
            item.value.key.interface_id.value = interface
            item.value.key.label.value = tag
            item.value.key.value.value = value
        stream.append(item)
    return stream


def convertListToConfigStream(assignmentConfigList):
    stream = []
    for assign in assignmentConfigList:
        item = TagAssignmentConfigStreamResponse()
        if len(assign) == 4:
            device, tag, value, remove = assign
            item.value.key.device_id.value = device
            item.value.key.label.value = tag
            item.value.key.value.value = value
            item.value.remove.value = remove
        elif len(assign) == 5:
            device, interface, tag, value, remove = assign
            item.value.key.device_id.value = device
            item.value.key.interface_id.value = interface
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

    def GetOne(self, _):
        return WorkspaceResponse()

    def SetGetAllResponse(self, response):
        self.tagResponse = response

    def SetGetAllConfigResponse(self, response):
        self.tagConfigResponse = response

    def Set(self, request):
        return

    def SetSome(self, request):
        if self.stub == TagConfigServiceStub:
            return [TagConfigSetSomeResponse]
        if self.stub == TagAssignmentConfigServiceStub:
            return [TagAssignmentConfigSetSomeResponse]


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
        None,
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
        None,
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
        None,
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
def test_changeDeviceTag(name, getAllResp, deviceId, oper, operLabel, operValue,
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
        None,
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
        None,
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


getInterfacesByTagCases = [
    # name
    # cached tags
    # tagv2 GetAll response
    # devices in topology
    # tag
    # topology flag
    # num GetAll calls
    # expected interfaces
    # expected Error
    [
        "get interfaces matching label with preloaded cache",
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']}},
            'dev3': {'Ethernet1': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
        },
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev3', 'Ethernet1', 'DC', 'DC2'),
                             ('dev3', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev3', 'Ethernet1', 'NodeId', '1'),
                             ]),
        {'dev1': ['Ethernet1'], 'dev2': ['Ethernet1'], 'dev3': ['Ethernet1']},
        Tag('DC', ''),
        True,
        0,
        [Interface('Ethernet1', Device('dev1')),
         Interface('Ethernet1', Device('dev2')),
         Interface('Ethernet1', Device('dev3'))],
        None
    ],
    [
        "try get interfaces not matching label with preloaded cache",
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']}},
            'dev3': {'Ethernet1': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
        },
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev3', 'Ethernet1', 'DC', 'DC2'),
                             ('dev3', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev3', 'Ethernet1', 'NodeId', '1'),
                             ]),
        {'dev1': ['Ethernet1'], 'dev2': ['Ethernet1'], 'dev3': ['Ethernet1']},
        Tag('Role', ''),
        True,
        0,
        [],
        None
    ],
    [
        "get interfaces matching label and value with preloaded cache",
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']}},
            'dev3': {'Ethernet1': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
        },
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev3', 'Ethernet1', 'DC', 'DC2'),
                             ('dev3', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev3', 'Ethernet1', 'NodeId', '1'),
                             ]),
        {'dev1': ['Ethernet1'], 'dev2': ['Ethernet1'], 'dev3': ['Ethernet1']},
        Tag('DC', 'DC1'),
        True,
        0,
        [Interface('Ethernet1', Device('dev1')),
         Interface('Ethernet1', Device('dev2'))],
        None
    ],
    [
        "get only interfaces of devices in topology matching label and value with preloaded cache",
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']}},
            'dev3': {'Ethernet1': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
        },
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev3', 'Ethernet1', 'DC', 'DC2'),
                             ('dev3', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev3', 'Ethernet1', 'NodeId', '1'),
                             ]),
        {'dev1': ['Ethernet1'], 'dev3': ['Ethernet1']},
        Tag('DC', 'DC1'),
        True,
        0,
        [Interface('Ethernet1', Device('dev1'))],
        None
    ],
    [
        "get only interfaces in topology matching label and value with preloaded cache",
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']}},
            'dev3': {'Ethernet1': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
        },
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev3', 'Ethernet1', 'DC', 'DC2'),
                             ('dev3', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev3', 'Ethernet1', 'NodeId', '1'),
                             ]),
        {'dev1': ['Ethernet1'], 'dev2': ['Ethernet2'], 'dev3': ['Ethernet1']},
        Tag('DC', 'DC1'),
        True,
        0,
        [Interface('Ethernet1', Device('dev1'))],
        None
    ],
    [
        "get interfaces of devices not in topology matching label and value with preloaded cache",
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']}},
            'dev3': {'Ethernet1': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
        },
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev3', 'Ethernet1', 'DC', 'DC2'),
                             ('dev3', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev3', 'Ethernet1', 'NodeId', '1'),
                             ]),
        {'dev1': ['Ethernet1'], 'dev3': ['Ethernet1']},
        Tag('DC', 'DC1'),
        False,
        0,
        [Interface('Ethernet1', Device('dev1')),
         Interface('Ethernet1', Device('dev2'))],
        None
    ],
    [
        "get interfaces not in topology matching label and value with preloaded cache",
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']}},
            'dev3': {'Ethernet1': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
        },
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev3', 'Ethernet1', 'DC', 'DC2'),
                             ('dev3', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev3', 'Ethernet1', 'NodeId', '1'),
                             ]),
        {'dev1': [], 'dev3': ['Ethernet1']},
        Tag('DC', 'DC1'),
        False,
        0,
        [Interface('Ethernet1', Device('dev1')),
         Interface('Ethernet1', Device('dev2'))],
        None
    ],
    [
        "try get interfaces with None label and value with preloaded cache",
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2']}},
            'dev3': {'Ethernet1': {'DC': ['DC2'], 'DC-Pod': ['POD1'], 'NodeId':['1']}},
        },
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev3', 'Ethernet1', 'DC', 'DC2'),
                             ('dev3', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev3', 'Ethernet1', 'NodeId', '1'),
                             ]),
        {'dev1': ['Ethernet1'], 'dev2': ['Ethernet1'], 'dev3': ['Ethernet1']},
        Tag('', 'DC1'),
        True,
        0,
        [],
        None
    ],
    [
        "get interfaces matching label without preloaded cache",
        None,
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ]),
        {'dev1': ['Ethernet1'], 'dev2': ['Ethernet1']},
        Tag('DC', ''),
        True,
        2,
        [Interface('Ethernet1', Device('dev1')),
         Interface('Ethernet1', Device('dev2'))],
        None
    ],
    [
        "try get interfaces not matching label without preloaded cache",
        None,
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ]),
        {'dev1': ['Ethernet1'], 'dev2': ['Ethernet1']},
        Tag('Role', ''),
        True,
        2,
        [],
        None
    ],
]


@pytest.mark.parametrize('name, cacheTags, getAllResp, topoDevices, tag, '
                         + 'topoFlag, expNumGetAlls, expectedInterfaces, '
                         + 'expectedError', getInterfacesByTagCases)
def test_getInterfacesByTag(name, cacheTags, getAllResp, topoDevices, tag,
                            topoFlag, expNumGetAlls, expectedInterfaces,
                            expectedError):
    error = None
    tagInterfaces = []
    ctx = mockCtx()
    deviceMap = {}
    for dev, interfaces in topoDevices.items():
        deviceMap[dev] = Device(deviceId=dev)
        for interface in interfaces:
            deviceMap[dev].addInterface(interface)
    topology = Topology(deviceMap)
    ctx.setTopology(topology)
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags._setRelevantInterfaceTagAssigns(cacheTags)
    try:
        tagInterfaces = ctx.getInterfacesByTag(tag, inTopology=topoFlag)
    except Exception as e:
        error = e
    if error or expectedError:
        assert str(error) == str(expectedError)
    intfList = [(intf.name, intf._device.id) for intf in tagInterfaces or []]
    expIntfList = [(intf.name, intf._device.id) for intf in expectedInterfaces or []]
    assert intfList == expIntfList
    assert ctx.client.numGetAlls == expNumGetAlls


assignUnassignDeviceTagsCases = [
    # name
    # tagv2 GetAll response
    # assigns as List of (deviceId, label, value, replace)
    # unassigns as List of (deviceId, label, value)
    # operation ('assign', 'unassign')
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
        [('dev1', 'Role', 'Core', False)],
        None,
        'assign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'],
                     'Role':['Spine', 'Core']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2'],
                     'Role':['Leaf']},
        },
        None
    ],
    [
        "assign multiple additional Role tag values to same device",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        [('dev1', 'Role', 'Core', False), ('dev1', 'Role', 'RR', False)],
        None,
        'assign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'],
                     'Role':['Spine', 'Core', 'RR']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2'],
                     'Role':['Leaf']},
        },
        None
    ],
    [
        "assign multiple additional Role tag values to multiple devices",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        [('dev1', 'Role', 'Core', False), ('dev1', 'Role', 'RR', False),
         ('dev2', 'Role', 'Edge', False), ('dev2', 'Role', 'RR', False),
         ],
        None,
        'assign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'],
                     'Role':['Spine', 'Core', 'RR']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2'],
                     'Role':['Leaf', 'Edge', 'RR']},
        },
        None
    ],
    [
        "assign multiple additional new tags to multiple devices",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        [('dev1', 'AS', '65000', False), ('dev1', 'RouterId', '10.0.0.1', False),
         ('dev2', 'AS', '65001', False), ('dev2', 'RouterId', '11.0.0.1', False),
         ],
        None,
        'assign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'],
                     'Role':['Spine'], 'AS': ['65000'], 'RouterId': ['10.0.0.1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2'],
                     'Role':['Leaf'], 'AS': ['65001'], 'RouterId': ['11.0.0.1']},
        },
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
        [('dev1', 'Role', 'Core', True)],
        None,
        'assign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'],
                     'Role':['Core']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2'],
                     'Role':['Leaf']},
        },
        None
    ],
    [
        "assign multiple replacement Role tag values",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        [('dev1', 'Role', 'Core', True), ('dev1', 'Role', 'RR', True)],
        None,
        'assign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'],
                     'Role':['RR']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2'],
                     'Role':['Leaf']},
        },
        None
    ],
    [
        "assign multiple replacement tag values to multiple devices",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        [('dev1', 'Role', 'RR', True), ('dev1', 'DC-Pod', 'POD2', True),
         ('dev2', 'NodeId', '3', True), ('dev2', 'DC-Pod', 'POD2', True),
         ],
        None,
        'assign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD2'], 'NodeId':['1'],
                     'Role':['RR']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD2'], 'NodeId':['3'],
                     'Role':['Leaf']},
        },
        None
    ],
    [
        "assign multiple additional and replacement tag values to multiple devices",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        [('dev1', 'Role', 'RR', False), ('dev1', 'DC-Pod', 'POD2', True),
         ('dev2', 'NodeId', '3', True), ('dev2', 'DC-Pod', 'POD2', True),
         ('dev2', 'Role', 'Edge', False),
         ],
        None,
        'assign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD2'], 'NodeId':['1'],
                     'Role':['Spine', 'RR']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD2'], 'NodeId':['3'],
                     'Role':['Leaf', 'Edge']},
        },
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
        None,
        [('dev1', 'Role', 'Core')],
        'unassign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'],
                     'Role':['Spine']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2'],
                     'Role':['Leaf']},
        },
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
        None,
        [('dev1', 'Role', 'Spine')],
        'unassign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2'],
                     'Role':['Leaf']},
        },
        None
    ],
    [
        "unassign tag label that's not assigned",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        None,
        [('dev1', 'AS', '65000')],
        'unassign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'],
                     'Role':['Spine']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2'],
                     'Role':['Leaf']},
        },
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
        None,
        [('dev1', 'Role', 'Core')],
        'unassign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'],
                     'Role':['Spine']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['2'],
                     'Role':['Leaf']},
        },
        None
    ],
    [
        "unassign all role and nodeId tags from multiple devices",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev1', 'Role', 'Core'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ('dev2', 'Role', 'Edge'),
                             ]),
        None,
        [('dev1', 'Role', None), ('dev2', 'Role', None),
         ('dev1', 'NodeId', None), ('dev2', 'NodeId', None),
         ],
        'unassign',
        2,
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1']}
        },
        None
    ],
    [
        "unassign all tags across multiple devices",
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev1', 'Role', 'Spine'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ('dev2', 'Role', 'Leaf'),
                             ]),
        None,
        [('dev1', 'DC', 'DC1'), ('dev1', 'DC-Pod', 'POD1'),
         ('dev1', 'NodeId', '1'), ('dev1', 'Role', 'Spine'),
         ('dev2', 'DC', 'DC1'), ('dev2', 'DC-Pod', 'POD1'),
         ('dev2', 'NodeId', '2'), ('dev2', 'Role', 'Leaf'),
         ],
        'unassign',
        2,
        {
        },
        None
    ],
]


@pytest.mark.parametrize('name, getAllResp, assigns, unassigns, oper, '
                         + 'expNumGetAlls, expectedTags, expectedError',
                         assignUnassignDeviceTagsCases)
def test_changeDeviceTags(name, getAllResp, assigns, unassigns, oper,
                          expNumGetAlls, expectedTags, expectedError):
    error = None
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(getAllResp)
    try:
        if oper == 'assign':
            ctx.tags._assignDeviceTags(assigns)
        elif oper == 'unassign':
            ctx.tags._unassignDeviceTags(unassigns)
    except Exception as e:
        error = e
    devTags = ctx.tags._getAllDeviceTags()
    if error or expectedError:
        assert str(error) == str(expectedError)
    assert devTags == expectedTags
    assert ctx.client.numGetAlls == expNumGetAlls


assignUnassignInterfaceTagCases = [
    # name
    # tagv2 GetAll response
    # device id
    # interface id
    # operation ('assign', 'unassign')
    # operation tag label
    # operation tag value
    # replace flag
    # num GetAll calls
    # expected tags
    # expected error
    [
        "assign additional Role tag value",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        'dev1',
        'Ethernet1',
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
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        'dev1',
        'Ethernet1',
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
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev1', 'Ethernet1', 'Role', 'Core'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        'dev1',
        'Ethernet1',
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
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        'dev1',
        'Ethernet1',
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
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        'dev1',
        'Ethernet1',
        'unassign',
        'Role',
        'Core',
        False,
        2,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'], 'Role':['Spine']},
        None
    ],
]


@pytest.mark.parametrize('name, getAllResp, deviceId, interfaceId, oper, operLabel, '
                         + 'operValue, replace, expNumGetAlls, expectedTags, '
                         + 'expectedError',
                         assignUnassignInterfaceTagCases)
def test_changeInterfaceTag(name, getAllResp, deviceId, interfaceId, oper, operLabel,
                            operValue, replace, expNumGetAlls, expectedTags,
                            expectedError):
    error = None
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(getAllResp)
    try:
        if oper == 'assign':
            ctx.tags._assignInterfaceTag(deviceId, interfaceId, operLabel, operValue,
                                         replaceValue=replace)
        elif oper == 'unassign':
            ctx.tags._unassignInterfaceTag(deviceId, interfaceId, operLabel, operValue)
    except Exception as e:
        error = e
    intfTags = ctx.tags._getInterfaceTags(deviceId, interfaceId)
    if error or expectedError:
        assert str(error) == str(expectedError)
    assert intfTags == expectedTags
    assert ctx.client.numGetAlls == expNumGetAlls


assignUnassignInterfaceTagsCases = [
    # name
    # tagv2 GetAll response
    # assigns as List of (deviceId, interfaceId, label, value, replace)
    # unassigns as List of (deviceId, interfaceId, label, value)
    # operation ('assign', 'unassign')
    # num GetAll calls
    # expected tags
    # expected error
    [
        "assign additional Role tag value",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        [('dev1', 'Ethernet1', 'Role', 'Core', False)],
        None,
        'assign',
        2,
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'],
                                   'Role': ['Spine', 'Core']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'],
                                   'Role': ['Leaf']}},
        },
        None
    ],
    [
        "assign multiple additional Role tag values to same interface",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        [('dev1', 'Ethernet1', 'Role', 'Core', False),
         ('dev1', 'Ethernet1', 'Role', 'RR', False)
         ],
        None,
        'assign',
        2,
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'],
                                   'Role': ['Spine', 'Core', 'RR']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'],
                                   'Role': ['Leaf']}},
        },
        None
    ],
    [
        "assign multiple additional Role tag values to multiple interfaces",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        [('dev1', 'Ethernet1', 'Role', 'Core', False),
         ('dev1', 'Ethernet1', 'Role', 'RR', False),
         ('dev1', 'Ethernet2', 'Role', 'Core', False),
         ('dev1', 'Ethernet2', 'Role', 'RR', False),
         ('dev2', 'Ethernet1', 'Role', 'Edge', False),
         ('dev2', 'Ethernet1', 'Role', 'RR', False)
         ],
        None,
        'assign',
        2,
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'],
                                   'Role': ['Spine', 'Core', 'RR']},
                     'Ethernet2': {'Role': ['Core', 'RR']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'],
                                   'Role': ['Leaf', 'Edge', 'RR']}},
        },
        None
    ],
    [
        "assign replacement Role tag value",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        [('dev1', 'Ethernet1', 'Role', 'Core', True)],
        None,
        'assign',
        2,
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'],
                                   'Role': ['Core']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'],
                                   'Role': ['Leaf']}},
        },
        None
    ],
    [
        "assign multiple replacement Role tag values to multiple interfaces",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        [('dev1', 'Ethernet1', 'Role', 'Core', True),
         ('dev1', 'Ethernet1', 'Role', 'RR', True),
         ('dev1', 'Ethernet2', 'Role', 'Core', True),
         ('dev1', 'Ethernet2', 'Role', 'RR', True)
         ],
        None,
        'assign',
        2,
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'],
                                   'Role': ['RR']},
                     'Ethernet2': {'Role': ['RR']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'],
                                   'Role': ['Leaf']}},
        },
        None
    ],
    [
        "assign multiple additional and replacement tag values to multiple interfaces",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ('dev2', 'Ethernet2', 'DC', 'DC1'),
                             ('dev2', 'Ethernet2', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet2', 'NodeId', '3'),
                             ('dev2', 'Ethernet2', 'Role', 'Leaf'),
                             ]),
        [('dev1', 'Ethernet1', 'Role', 'RR', False),
         ('dev1', 'Ethernet1', 'DC-Pod', 'POD2', True),
         ('dev1', 'Ethernet2', 'NodeId', '2', True),
         ('dev1', 'Ethernet2', 'Role', 'Core', True),
         ('dev1', 'Ethernet2', 'Role', 'RR', True),
         ('dev2', 'Ethernet1', 'NodeId', '3', True),
         ('dev2', 'Ethernet1', 'Role', 'Edge', False),
         ('dev2', 'Ethernet2', 'NodeId', '4', True),
         ('dev2', 'Ethernet2', 'Role', 'Edge', False),
         ],
        None,
        'assign',
        2,
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD2'], 'NodeId': ['1'],
                                   'Role':['Spine', 'RR']},
                     'Ethernet2': {'NodeId': ['2'], 'Role': ['RR']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['3'],
                                   'Role': ['Leaf', 'Edge']},
                     'Ethernet2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['4'],
                                   'Role': ['Leaf', 'Edge']}},
        },
        None
    ],
    [
        "unassign second Role tag value",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev1', 'Ethernet1', 'Role', 'Core'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        None,
        [('dev1', 'Ethernet1', 'Role', 'Core')],
        'unassign',
        2,
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'],
                                   'Role': ['Spine']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'],
                                   'Role': ['Leaf']}},
        },
        None
    ],
    [
        "unassign last Role tag value",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        None,
        [('dev1', 'Ethernet1', 'Role', 'Spine')],
        'unassign',
        2,
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'],
                                   'Role': ['Leaf']}},
        },
        None
    ],
    [
        "unassign tag label that's not assigned",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        None,
        [('dev1', 'Ethernet1', 'AS', '65000')],
        'unassign',
        2,
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'],
                                   'Role': ['Spine']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'],
                                   'Role': ['Leaf']}},
        },
        None
    ],
    [
        "unassign tag value that's not assigned",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ]),
        None,
        [('dev1', 'Ethernet1', 'Role', 'Core')],
        'unassign',
        2,
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1'],
                                   'Role': ['Spine']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2'],
                                   'Role': ['Leaf']}},
        },
        None
    ],
    [
        "unassign all role and nodeId tags from multiple interfaces",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev1', 'Ethernet1', 'Role', 'Core'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ('dev2', 'Ethernet1', 'Role', 'Edge'),
                             ('dev2', 'Ethernet2', 'DC', 'DC1'),
                             ('dev2', 'Ethernet2', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet2', 'NodeId', '3'),
                             ('dev2', 'Ethernet2', 'Role', 'Leaf'),
                             ('dev2', 'Ethernet2', 'Role', 'Edge'),
                             ]),
        None,
        [('dev1', 'Ethernet1', 'Role', None),
         ('dev1', 'Ethernet1', 'NodeId', None),
         ('dev2', 'Ethernet1', 'Role', None),
         ('dev2', 'Ethernet1', 'NodeId', None),
         ('dev2', 'Ethernet2', 'Role', None),
         ('dev2', 'Ethernet2', 'NodeId', None),
         ],
        'unassign',
        2,
        {
            'dev1': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1']}},
            'dev2': {'Ethernet1': {'DC': ['DC1'], 'DC-Pod': ['POD1']},
                     'Ethernet2': {'DC': ['DC1'], 'DC-Pod': ['POD1']}},
        },
        None
    ],
    [
        "unassign all tags across multiple interfaces",
        convertListToStream([('dev1', 'Ethernet1', 'DC', 'DC1'),
                             ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev1', 'Ethernet1', 'NodeId', '1'),
                             ('dev1', 'Ethernet1', 'Role', 'Spine'),
                             ('dev2', 'Ethernet1', 'DC', 'DC1'),
                             ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet1', 'NodeId', '2'),
                             ('dev2', 'Ethernet1', 'Role', 'Leaf'),
                             ('dev2', 'Ethernet2', 'DC', 'DC1'),
                             ('dev2', 'Ethernet2', 'DC-Pod', 'POD1'),
                             ('dev2', 'Ethernet2', 'NodeId', '3'),
                             ('dev2', 'Ethernet2', 'Role', 'Leaf'),
                             ]),
        None,
        [('dev1', 'Ethernet1', 'DC', 'DC1'),
         ('dev1', 'Ethernet1', 'DC-Pod', 'POD1'),
         ('dev1', 'Ethernet1', 'NodeId', '1'),
         ('dev1', 'Ethernet1', 'Role', 'Spine'),
         ('dev2', 'Ethernet1', 'DC', 'DC1'),
         ('dev2', 'Ethernet1', 'DC-Pod', 'POD1'),
         ('dev2', 'Ethernet1', 'NodeId', '2'),
         ('dev2', 'Ethernet1', 'Role', 'Leaf'),
         ('dev2', 'Ethernet2', 'DC', 'DC1'),
         ('dev2', 'Ethernet2', 'DC-Pod', 'POD1'),
         ('dev2', 'Ethernet2', 'NodeId', '3'),
         ('dev2', 'Ethernet2', 'Role', 'Leaf'),
         ],
        'unassign',
        2,
        {
        },
        None
    ],
]


@pytest.mark.parametrize('name, getAllResp, assigns, unassigns, oper, '
                         + 'expNumGetAlls, expectedTags, expectedError',
                         assignUnassignInterfaceTagsCases)
def test_changeInterfaceTags(name, getAllResp, assigns, unassigns, oper,
                             expNumGetAlls, expectedTags, expectedError):
    error = None
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(getAllResp)
    try:
        if oper == 'assign':
            ctx.tags._assignInterfaceTags(assigns)
        elif oper == 'unassign':
            ctx.tags._unassignInterfaceTags(unassigns)
    except Exception as e:
        error = e
    intfTags = ctx.tags._getAllInterfaceTags()
    if error or expectedError:
        assert str(error) == str(expectedError)
    assert intfTags == expectedTags
    assert ctx.client.numGetAlls == expNumGetAlls
