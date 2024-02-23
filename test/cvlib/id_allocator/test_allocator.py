# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest
import re

from cloudvision.cvlib import (
    IdAllocator
)

checkNodeIdCases = [
    # name
    # allocations
    # spine ids
    # leaf ids
    # mleaf ids
    # expected error
    [
        'L3 valid',
        'L3',
        [
            ('spine1', 1), ('spine2', 2),
            ('leaf1', 1), ('leaf2', 2), ('leaf3', 3),
            ('memberleaf1', 1), ('memberleaf2', 2), ('memberleaf3', 3),
            ('memberleaf4', 4),
        ],
        [1, 2],
        [1, 2, 3],
        [1, 2, 3, 4],
        None
    ],
    [
        'L2 valid',
        'L2',
        [
            ('spine1', 1), ('spine2', 2),
            ('leaf1', 1), ('leaf2', 2), ('leaf3', 3),
            ('memberleaf1', 4), ('memberleaf2', 5), ('memberleaf3', 6),
            ('memberleaf4', 7),
        ],
        [1, 2],
        [1, 2, 3, 4, 5, 6, 7],
        [1, 2, 3, 4, 5, 6, 7],
        None
    ],
    [
        'L3 invalid spine duplicate id',
        'L3',
        [
            ('spine1', 2), ('spine2', 2),
            ('leaf1', 1), ('leaf2', 2), ('leaf3', 3),
            ('memberleaf1', 1), ('memberleaf2', 2), ('memberleaf3', 3),
            ('memberleaf4', 4),
        ],
        [1, 2],
        [1, 2, 3],
        [1, 2, 3, 4],
        AssertionError("The same nodeID, 2, can not be applied to both "
                       "of these spines: spine1, spine2")
    ],
    [
        'L3 invalid leaf duplicate id',
        'L3',
        [
            ('spine1', 1), ('spine2', 2),
            ('leaf1', 1), ('leaf2', 1), ('leaf3', 3),
            ('memberleaf1', 1), ('memberleaf2', 2), ('memberleaf3', 3),
            ('memberleaf4', 4),
        ],
        [1, 2],
        [1, 2, 3],
        [1, 2, 3, 4],
        AssertionError("The same nodeID, 1, can not be applied to both "
                       "of these leafs: leaf1, leaf2")
    ],
    [
        'L2 invalid leaf duplicate id',
        'L2',
        [
            ('spine1', 1), ('spine2', 2),
            ('leaf1', 1), ('leaf2', 2), ('leaf3', 3),
            ('memberleaf1', 4), ('memberleaf2', 3), ('memberleaf3', 6),
            ('memberleaf4', 7),
        ],
        [1, 2],
        [1, 2, 3, 4, 5, 6, 7],
        [1, 2, 3, 4, 5, 6, 7],
        AssertionError("The same nodeID, 3, can not be applied to both "
                       "of these leafs: leaf3, memberleaf2")
    ],
]


@pytest.mark.parametrize('name, campusType, allocations, exp_spines, exp_leafs, '
                         + 'exp_memberleafs, expectedError',
                         checkNodeIdCases)
def test_getAllDeviceTags(name, campusType, allocations, exp_spines, exp_leafs,
                          exp_memberleafs, expectedError):
    error = None
    id_checkers = {}
    id_checkers['spine'] = IdAllocator(idLabel='nodeID', groupLabel='spines')
    if campusType.lower() == "l2":
        id_checkers['leaf'] = IdAllocator(idLabel='nodeID', groupLabel='leafs')
        id_checkers['memberleaf'] = id_checkers['leaf']
    else:
        id_checkers['leaf'] = IdAllocator(idLabel='nodeID', groupLabel='leafs')
        id_checkers['memberleaf'] = IdAllocator(idLabel='nodeID', groupLabel='leafs')
    try:
        for (deviceId, nodeId) in allocations:
            devtype = re.findall(r'(\D+)', deviceId)[0]
            id_checkers[devtype].allocate(nodeId, deviceId)
    except Exception as e:
        error = e
    if error or expectedError:
        assert str(error) == str(expectedError)
    else:
        assert exp_spines == id_checkers['spine'].getAllocated()
        assert exp_leafs == id_checkers['leaf'].getAllocated()
        assert exp_memberleafs == id_checkers['memberleaf'].getAllocated()
