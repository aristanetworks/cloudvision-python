# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest

from cloudvision.cvlib.studio import getSimpleResolverQueryValue
from cloudvision.cvlib import InputException


cases = [
    # Elements in case are in the following order
    # name
    # input query
    # expected return value
    # expected error message
    [
        "Not a query input",
        "Management",
        None,
        "Passed 'query' \"Management\" does not appear to be a query",
    ],
    [
        "Complex Query",
        "device:deviceID1 OR device:deviceID2",
        None,
        "Passed query \"device:deviceID1 OR device:deviceID2\" is a complex query",
    ],
    [
        "Simple Query with empty value",
        "device:",
        None,
        "Passed query \"device:\" is missing a value",
    ],
    [
        "Simple Query",
        "device:deviceID1",
        "deviceID1",
        None,
    ],
    [
        "Another simple Query",
        "Campus:HQ",
        "HQ",
        None,
    ],
]


@pytest.mark.parametrize('name, inp, expected, expectedErrMsg', cases)
def test_element_extraction(name, inp, expected, expectedErrMsg):
    """Test whether values are extracted correctly."""
    if expectedErrMsg is not None:
        with pytest.raises(InputException) as excInfo:
            getSimpleResolverQueryValue(inp)
        assert expectedErrMsg in str(excInfo.value)
    else:
        actual = getSimpleResolverQueryValue(inp)
        assert actual == expected
