# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""tests for the template access to tags """

import pytest

from cloudvision.cvlib import (
    Tags
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
        self.workspaceId = "1"


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


class mockDevice:
    def __init__(self):
        self.id = None


class mockCtx:
    def __init__(self):
        self.client = mockClient()
        self.studio = mockStudio()
        self.device = mockDevice()
        self.tags = Tags(self)

    def getApiClient(self, stub):
        self.client.stub = stub
        return self.client

    def getDevice(self):
        return self.device


getAllDeviceTagsCases = [
    # name
    # original filter
    # new filter
    # preloaded tags
    # validateFunc
    # tagv2 GetAll response
    # num GetAll calls
    # expected
    # err
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
                         + 'expNumGetAlls, expected, err', getAllDeviceTagsCases)
def test_getAllDeviceTags(name, cacheTags, validateFunc, getAllResp,
                          expNumGetAlls, expected, err):
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags._setRelevantTagAssigns(cacheTags)
    allTags = ctx.tags._getAllDeviceTags()
    assert allTags == expected
    assert ctx.client.numGetAlls == expNumGetAlls


getDeviceTagsCases = [
    # name
    # tagv2 GetAll response
    # device id
    # num GetAll calls
    # expected
    # err
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
                         + 'expNumGetAlls, expected, err', getDeviceTagsCases)
def test_getDeviceTags(name, cacheTags, getAllResp, deviceId,
                       expNumGetAlls, expected, err):
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags._setRelevantTagAssigns(cacheTags)
    error = ""
    try:
        devTags = ctx.tags._getDeviceTags(deviceId)
    except Exception as e:
        error = str(e).split("assert")[0]
    if error:
        assert error == err
    else:
        assert devTags == expected
        assert ctx.client.numGetAlls == expNumGetAlls


assignUnassignDeviceTagCases = [
    # name
    # tagv2 GetAll response
    # device id
    # operation ('assign', 'unassign')
    # operation tag label
    # operation tag value
    # multiAllowed
    # num GetAll calls
    # expected
    # err
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
        True,
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
        False,
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
        True,
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
        True,
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
        True,
        2,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'], 'Role':['Spine']},
        None
    ],
]


@pytest.mark.parametrize('name, getAllResp, deviceId, oper, operLabel, operValue, '
                         + 'multiAllowed, expNumGetAlls, expected, err',
                         assignUnassignDeviceTagCases)
def test_changeDeviceTags(name, getAllResp, deviceId, oper, operLabel, operValue,
                          multiAllowed, expNumGetAlls, expected, err):
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(getAllResp)
    error = ""
    try:
        if oper == 'assign':
            ctx.tags._assignDeviceTag(deviceId, operLabel, operValue, multiValue=multiAllowed)
        elif oper == 'unassign':
            ctx.tags._unassignDeviceTag(deviceId, operLabel, operValue)
        devTags = ctx.tags._getDeviceTags(deviceId)
    except Exception as e:
        error = str(e).split("assert")[0]
    if error:
        assert error == err
    else:
        assert devTags == expected
        assert ctx.client.numGetAlls == expNumGetAlls


mergeGetAllDeviceTagsCases = [
    # name
    # mainline state response
    # workspace config response
    # expected
    # err
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
                         + 'expected, err', mergeGetAllDeviceTagsCases)
def test_mergeTags(name, mainlineStateResp, workspaceConfigResp,
                   expected, err):
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(mainlineStateResp)
    ctx.client.SetGetAllConfigResponse(workspaceConfigResp)
    allTags = ctx.tags._getAllDeviceTags()
    assert allTags == expected
