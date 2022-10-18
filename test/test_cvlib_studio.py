# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""basic test that converted and encoded types are handled correctly."""

import pytest

from cloudvision.cvlib.studio import extractInputElems
from cloudvision.cvlib.exceptions import InputNotFoundException

exampleStudioInputs = {
    "campusPicker": [
        {
            "inputs": {
                "campus": {
                    "commonVlans": [
                        {
                            "IPHelperAddress": "",
                            "commonVlanID": 1,
                            "commonVlanIsMgmt": True,
                            "commonVlanName": "Management",
                            "commonVlanVIP": "1.1.1.1",
                            "vrf": ""
                        }
                    ],
                    "fabricType": "L2 MLAG",
                    "podPicker": [
                        {
                            "inputs": {
                                "pod": {
                                    "leafs": [
                                        {
                                            "inputs": {
                                                "leaf": {
                                                    "leafInbandMgmtIPSubnet": "1.1.1.1/24",
                                                    "leafRole": "Primary"
                                                }
                                            },
                                            "tags": {
                                                "query": "device:deviceID1"
                                            }
                                        },
                                    ]
                                }
                            },
                            "tags": {
                                "query": "Campus-Pod:1"
                            }
                        }
                    ],
                    "splinePicker": [
                        {
                            "inputs": {
                                "spline": {
                                    "splineInbandMgmtIPSubnet": "",
                                    "splineRole": "Secondary",
                                    "splineVlans": [
                                        {
                                            "primarySecondary": "Primary",
                                            "splineVlanID": 1,
                                            "splineVlanIPSubnet": ""
                                        },
                                    ]
                                }
                            },
                            "tags": {
                                "query": "device:deviceID1"
                            }
                        }
                    ]
                }
            },
            "tags": {
                "query": "Campus:HQ"
            }
        }
    ]
}

cases = [
    # Elements in case are in the following order
    # name
    # inp
    # inputPath
    # elems
    # tags
    # expected
    # err
    [
        "Empty",
        {},
        [],
        {"a"},
        {"b"},
        {},
        None
    ],
    [
        "Non-existent path",
        {
            "path": {"to": "input"}
        },
        ["path", "doesn't", "exist"],
        {"a"},
        {"b"},
        {},
        "Input path does not exist in inputs (['path', \"doesn't\", 'exist']):"
        + " \"doesn't\" not present in inputs"
    ],
    [
        "Normal grabbing of elements: Desired elements in root of inputs",
        {
            "path": {
                "to": {
                    "input": "value"
                },
                "a": "valueA",
            },
            "tags": {"query": "b:valueB"},
        },
        ["path", "to", "input"],
        {"a"},
        {"b"},
        {
            "a": "valueA",
            "b": "valueB",
        },
        None
    ],
    [
        "Normal grabbing of elements: Desired elements in final entry of inputs",
        {
            "path": {
                "to": {
                    "input": "value",
                    "a": "valueA",
                    "tags": {"query": "b:valueB"},
                },
            },
        },
        ["path", "to", "input"],
        {"a"},
        {"b"},
        {
            "a": "valueA",
            "b": "valueB",
        },
        None
    ],
    [
        "Overwriting of elements: Desired element has multiple entries. Gets most recent value",
        {
            "path": {
                "to": {
                    "input": "value",
                    "a": "valueB",
                },
                "a": "valueA",
            },
        },
        ["path", "to", "input"],
        {"a"},
        {},
        {
            "a": "valueB",
        },
        None
    ],
    [
        "Overwriting of elements: Desired elements/tags have same name. Gets most recent value",
        {
            "path": {
                "to": {
                    "input": "value",
                    "tags": {"query": "a:valueB"},
                },
                "a": "valueA",
            },
        },
        ["path", "to", "input"],
        {"a"},
        {"a"},
        {
            "a": "valueB",
        },
        None
    ],
    [
        "Normal grabbing of elements: Stringified list index in path",
        {
            "path": [
                {
                    "input": "value",
                    "a": "valueA",
                    "tags": {"query": "b:valueB"},
                },
            ],
        },
        ["path", "0", "input"],
        {"a"},
        {"b"},
        {
            "a": "valueA",
            "b": "valueB",
        },
        None
    ],
    [
        "Normal grabbing of elements: String element",
        {
            "path": {
                "33": {
                    "input": "value",
                    "a": "valueA",
                    "tags": {"query": "b:valueB"},
                },
            }
        },
        ["path", "33", "input"],
        {"a"},
        {"b"},
        {
            "a": "valueA",
            "b": "valueB",
        },
        None
    ],
    [
        "Stringified list index, doesn't exist",
        {
            "path": [
                {
                    "input": "value",
                    "a": "valueA",
                    "tags": {"query": "b:valueB"},
                },
            ],
        },
        ["path", "33", "input"],
        {"a"},
        {"b"},
        {},
        "Input path does not exist in inputs (['path', '33', 'input']):"
        + " '33' list index out of range"
    ],
    [
        "Extraction from example studio input",
        exampleStudioInputs,
        ["campusPicker", "0", "inputs", "campus", "splinePicker",
            "0", "inputs", "spline", "splineVlans", "0", "splineVlanIPSubnet"],
        {"splineVlanID", "splineRole"},
        {"Campus", "device"},
        {
            "splineVlanID": 1,
            "splineRole": "Secondary",
            "Campus": "HQ",
            "device": "deviceID1",
        },
        None
    ],
    [
        "Extraction from example studio input",
        exampleStudioInputs,
        ["campusPicker", "0", "inputs", "campus", "podPicker",
            "0", "inputs", "pod", "leafs", "0", "inputs", "leaf", "leafInbandMgmtIPSubnet"],
        {"leafRole"},
        {"Campus", "device"},
        {
            "leafRole": "Primary",
            "Campus": "HQ",
            "device": "deviceID1",
        },
        None
    ],
]


@pytest.mark.parametrize('name, inp, inputPath, elems, tags, expected, err', cases)
def test_element_extraction(name, inp, inputPath, elems, tags, expected, err):
    """Test whether values are extracted correctly."""
    try:
        actual = extractInputElems(inp, inputPath, elems, tags)
        assert actual == expected
    except Exception as e:
        assert str(e) == err
