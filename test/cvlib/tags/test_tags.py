# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""tests for the template access to tags """

import pytest

from cloudvision.cvlib import (
    Tags
)

from arista.tag.v2.services import (
    TagAssignmentStreamResponse
)


class mockStudio:
    def __init__(self):
        self.workspaceId = "1"


class mockClient:
    def __init__(self):
        self.stuff = None
        self.tagResponse = TagAssignmentStreamResponse()
        self.numGetAlls = 0

    def GetAll(self, request):
        self.numGetAlls += 1
        return self.tagResponse

    def SetGetAllResponse(self, response):
        self.tagResponse = response

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
        return self.client

    def getDevice(self):
        return self.device


def convertMapToStream(assignmentList):
    stream = []
    for assign in assignmentList:
        device, tag, value = assign
        item = TagAssignmentStreamResponse()
        item.value.key.device_id.value = device
        item.value.key.label.value = tag
        item.value.key.value.value = value
        stream.append(item)
    return stream


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
        convertMapToStream([('dev1', 'DC', 'DC1'),
                            ('dev1', 'DC-Pod', 'POD1'),
                            ('dev1', 'NodeId', '1'),
                            ('dev2', 'DC', 'DC1'),
                            ('dev2', 'DC-Pod', 'POD1'),
                            ('dev2', 'NodeId', '2'),
                            ]),
        1,
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
        convertMapToStream([('dev1', 'DC', 'DC1'),
                            ('dev1', 'DC-Pod', 'POD1'),
                            ('dev1', 'NodeId', '1'),
                            ('dev2', 'DC', 'DC1'),
                            ('dev2', 'DC-Pod', 'POD1'),
                            ('dev2', 'NodeId', '2'),
                            ]),
        1,
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
        convertMapToStream([('dev1', 'DC', 'DC1'),
                            ('dev1', 'DC-Pod', 'POD1'),
                            ('dev1', 'NodeId', '1'),
                            ('dev2', 'DC', 'DC1'),
                            ('dev2', 'DC-Pod', 'POD1'),
                            ('dev2', 'NodeId', '2'),
                            ]),
        'dev1',
        1,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        None
    ],
    [
        "passing validation",
        deviceTagValidationFunc,
        convertMapToStream([('dev1', 'DC', 'DC1'),
                            ('dev1', 'DC-Pod', 'POD1'),
                            ('dev1', 'NodeId', '1'),
                            ('dev2', 'DC', 'DC1'),
                            ('dev2', 'DC-Pod', 'POD1'),
                            ('dev2', 'NodeId', '2'),
                            ]),
        'dev1',
        1,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        None
    ],
    [
        "passing validation where unused devices would fail validation",
        deviceTagValidationFunc,
        convertMapToStream([('dev1', 'DC', 'DC1'),
                            ('dev1', 'DC-Pod', 'POD1'),
                            ('dev1', 'NodeId', '1'),
                            ('dev2', 'DC', 'DC1'),
                            ('dev2', 'DC-Pod', 'POD1'),
                            ('dev2', 'NodeId', 'a'),
                            ]),
        'dev1',
        1,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        None
    ],
    [
        "failing validation",
        deviceTagValidationFunc,
        convertMapToStream([('dev1', 'DC', 'DC1'),
                            ('dev1', 'DC-Pod', 'POD1'),
                            ('dev1', 'NodeId', 'a'),
                            ('dev2', 'DC', 'DC1'),
                            ('dev2', 'DC-Pod', 'POD1'),
                            ('dev2', 'NodeId', '2'),
                            ]),
        'dev1',
        1,
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
        convertMapToStream([('dev1', 'DC', 'DC1'),
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
        1,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'], 'Role':['Spine', 'Core']},
        None
    ],
    [
        "assign replacement Role tag value",
        deviceTagValidationFunc,
        convertMapToStream([('dev1', 'DC', 'DC1'),
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
        1,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'], 'Role':['Core']},
        None
    ],
    [
        "assign additional Node tag value failing validation check",
        deviceTagValidationFunc,
        convertMapToStream([('dev1', 'DC', 'DC1'),
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
        1,
        None,
        "Tag validation error: tag NodeId values ['1', '3'] assigned to dev1 failed Count Check\n"
    ],
    [
        "unassign second Role tag value",
        deviceTagValidationFunc,
        convertMapToStream([('dev1', 'DC', 'DC1'),
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
        1,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1'], 'Role':['Spine']},
        None
    ],
    [
        "unassign last Role tag value",
        deviceTagValidationFunc,
        convertMapToStream([('dev1', 'DC', 'DC1'),
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
        1,
        {'DC': ['DC1'], 'DC-Pod': ['POD1'], 'NodeId':['1']},
        None
    ],
    [
        "unassign tag value that's not assigned",
        deviceTagValidationFunc,
        convertMapToStream([('dev1', 'DC', 'DC1'),
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
        1,
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
