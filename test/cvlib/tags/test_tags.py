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


def deviceTagValidationFunc(deviceID, deviceTags):
    def checkCount(values, count):
        if not count:
            return True
        elif isinstance(count, int) and len(values) != count:
            return False
        elif count == "0-1" and not len(values) <= 1:
            return False
        elif count == "1-*" and not len(values) >= 1:
            return False
        return True

    tagChecks = {
        'NodeId': {
            'checkFunctions': [
                ('Integer Check', lambda values: all(value.isdigit() for value in values)),
                ('Count Check', lambda values: checkCount(values, '0-1'))
            ]
        },
    }
    for tag, checks in tagChecks.items():
        values = deviceTags.get(tag, [])
        for checkName, func in checks.get('checkFunctions'):
            assert func(values), (f'Tag validation error: tag {tag} values {values} assigned'
                                  + f' to {deviceID} failed {checkName}')
    return deviceTags


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
        "set same filter as pre-existing cache",
        [],
        ['DC', 'DC-Pod'],
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
        "set more specific filter as pre-existing cache",
        [],
        ['DC'],
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1']},
        },
        None,
        [],
        0,
        {
            'dev1': {'DC': ['DC1']},
            'dev2': {'DC': ['DC1']},
        },
        None
    ],
    [
        "set less specific filter as pre-existing cache",
        ['DC', 'DC-Pod'],
        ['DC', 'DC-Pod', 'NodeId'],
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1']},
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
    [
        "set less specific no filter as pre-existing cache",
        ['DC', 'DC-Pod'],
        [],
        {
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1']},
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


@pytest.mark.parametrize('name, filter1, filter2, cacheTags, validateFunc, getAllResp, '
                         + 'expNumGetAlls, expected, err', getAllDeviceTagsCases)
def test_getAllDeviceTags(name, filter1, filter2, cacheTags, validateFunc, getAllResp,
                          expNumGetAlls, expected, err):
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags.setFilter(filter1)
    ctx.tags.setRelevantTagAssigns(cacheTags)
    ctx.tags.setFilter(filter2)
    allTags = ctx.tags.getAllDeviceTags()
    assert allTags == expected
    assert ctx.client.numGetAlls == expNumGetAlls


getDeviceTagsCases = [
    # name
    # validateFunc
    # tagv2 GetAll response
    # device id
    # num GetAll calls
    # expected
    # err
    [
        "no validation",
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
        "passing validation",
        deviceTagValidationFunc,
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
        "passing validation where unused devices would fail validation",
        deviceTagValidationFunc,
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', '1'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', 'a'),
                             ]),
        'dev1',
        2,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        None
    ],
    [
        "failing validation",
        deviceTagValidationFunc,
        convertListToStream([('dev1', 'DC', 'DC1'),
                             ('dev1', 'DC-Pod', 'POD1'),
                             ('dev1', 'NodeId', 'a'),
                             ('dev2', 'DC', 'DC1'),
                             ('dev2', 'DC-Pod', 'POD1'),
                             ('dev2', 'NodeId', '2'),
                             ]),
        'dev1',
        2,
        None,
        "Tag validation error: tag NodeId values ['a'] assigned to dev1 failed Integer Check\n"
    ],
]


@pytest.mark.parametrize('name, validateFunc, getAllResp, deviceId, '
                         + 'expNumGetAlls, expected, err', getDeviceTagsCases)
def test_getDeviceTags(name, validateFunc, getAllResp, deviceId,
                       expNumGetAlls, expected, err):
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags.setDeviceTagValidationFunc(validateFunc)
    error = ""
    try:
        devTags = ctx.tags.getDeviceTags(deviceId)
    except Exception as e:
        error = str(e).split("assert")[0]
    if error:
        assert error == err
    else:
        assert devTags == expected
        assert ctx.client.numGetAlls == expNumGetAlls


assignUnassignDeviceTagCases = [
    # name
    # validateFunc
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
        deviceTagValidationFunc,
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
        deviceTagValidationFunc,
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
        "assign additional Node tag value failing validation check",
        deviceTagValidationFunc,
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
        'NodeId',
        '3',
        True,
        2,
        None,
        "Tag validation error: tag NodeId values ['1', '3'] assigned to dev1 failed Count Check\n"
    ],
    [
        "unassign second Role tag value",
        deviceTagValidationFunc,
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
        deviceTagValidationFunc,
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
        deviceTagValidationFunc,
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


@pytest.mark.parametrize('name, validateFunc, getAllResp, deviceId, oper, operLabel, operValue, '
                         + 'multiAllowed, expNumGetAlls, expected, err',
                         assignUnassignDeviceTagCases)
def test_changeDeviceTags(name, validateFunc, getAllResp, deviceId, oper, operLabel, operValue,
                          multiAllowed, expNumGetAlls, expected, err):
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(getAllResp)
    ctx.tags.setDeviceTagValidationFunc(validateFunc)
    error = ""
    try:
        if oper == 'assign':
            ctx.tags.assignDeviceTag(deviceId, operLabel, operValue, multiValue=multiAllowed)
        elif oper == 'unassign':
            ctx.tags.unassignDeviceTag(deviceId, operLabel, operValue)
        devTags = ctx.tags.getDeviceTags(deviceId)
    except Exception as e:
        error = str(e).split("assert")[0]
    if error:
        assert error == err
    else:
        assert devTags == expected
        assert ctx.client.numGetAlls == expNumGetAlls


mergeGetAllDeviceTagsCases = [
    # name
    # filter
    # validateFunc
    # mainline state response
    # workspace config response
    # expected
    # err
    [
        "no workspace updates",
        ['DC', 'DC-Pod', 'NodeId', 'Role'],
        None,
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
        ['DC', 'DC-Pod', 'NodeId', 'Role'],
        None,
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
        ['DC', 'DC-Pod', 'NodeId', 'Role'],
        None,
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
        ['DC', 'DC-Pod', 'NodeId', 'Role'],
        None,
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
        ['DC', 'DC-Pod', 'NodeId', 'Role'],
        None,
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
        ['DC', 'DC-Pod', 'NodeId', 'Role'],
        None,
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
        ['DC', 'DC-Pod', 'NodeId', 'Role'],
        None,
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
    [
        "mainline with workspace add/remove while filtering out",
        ['DC', 'DC-Pod', 'NodeId'],
        None,
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
            'dev1': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['1']},
            'dev2': {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId': ['2']},
        },
        None
    ],
]


@pytest.mark.parametrize('name, filter1, validateFunc, mainlineStateResp, workspaceConfigResp, '
                         + 'expected, err', mergeGetAllDeviceTagsCases)
def test_mergeTags(name, filter1, validateFunc, mainlineStateResp, workspaceConfigResp,
                   expected, err):
    ctx = mockCtx()
    ctx.client.SetGetAllResponse(mainlineStateResp)
    ctx.client.SetGetAllConfigResponse(workspaceConfigResp)
    ctx.tags.setFilter(filter1)
    allTags = ctx.tags.getAllDeviceTags()
    assert allTags == expected
