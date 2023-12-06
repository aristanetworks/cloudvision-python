# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest
import time
from unittest.mock import MagicMock, PropertyMock, patch
from grpc import StatusCode, RpcError
from cloudvision.cvlib import GetOneWithWS
from cloudvision.cvlib.constants import MAINLINE_WS_ID


rpcNotFound = RpcError()
rpcNotFound.code = lambda: StatusCode.NOT_FOUND

rpcInternal = RpcError()
rpcInternal.code = lambda: StatusCode.INTERNAL


mockState = MagicMock()
mockConfig = MagicMock()

mockStub = MagicMock()

cases = [
    # Elements in case are in the following order
    # name
    # ws in get req
    # return values for state get calls (1st for ws, 2nd for mainline)
    # expected value for the state.value attr
    # return values for config get calls (1st for ws)
    # expected value for the config.remove attr
    # expected return value
    # expected error code
    [
        "failure querying WS state",
        "test-WS-ID",
        [rpcInternal, None],
        "",
        [None],
        False,
        StatusCode.INTERNAL,
    ],
    [
        "Not found anywhere",
        "test-WS-ID",
        [rpcNotFound, rpcNotFound],
        "",
        [None],
        False,
        StatusCode.NOT_FOUND,
    ],
    [
        "failure, original query to mainline state, not there",
        MAINLINE_WS_ID,
        [rpcNotFound, None],
        "",
        [None],
        False,
        StatusCode.NOT_FOUND,
    ],
    [
        "failure querying Mainline state",
        "test-WS-ID",
        [rpcNotFound, rpcInternal],
        "",
        [None],
        False,
        StatusCode.INTERNAL,
    ],
    [
        "working case, in mainline",
        "test-WS-ID",
        [rpcNotFound, mockState],
        "testMainlineReturnVal",
        [rpcNotFound],
        False,
        None,
    ],
    [
        "Failure querying WS conf",
        "test-WS-ID",
        [rpcNotFound, mockState],
        "testMainlineReturnVal",
        [rpcInternal],
        True,
        StatusCode.INTERNAL,
    ],
    [
        "Deleted in WS",
        "test-WS-ID",
        [rpcNotFound, mockState],
        "testMainlineReturnVal",
        [mockConfig],
        True,
        None,
    ],
    [
        "working case, in WS",
        "test-WS-ID",
        [mockState, None],
        "testReturnVal",
        [None],
        False,
        None,
    ],
]


@pytest.mark.parametrize('name, ws, stateReturn, stateVal, confReturn, confRm, errCode', cases)
def test_get_one(name, ws, stateReturn, stateVal, confReturn, confRm, errCode):
    mockApiClientGetter = MagicMock()
    mockStateClient = MagicMock()
    mockConfigClient = MagicMock()
    mockApiClientGetter.side_effect = [
        mockStateClient,
        mockConfigClient,
    ]
    mockGetReq = MagicMock()
    type(mockGetReq.key.workspace_id).value = PropertyMock(return_value=ws)

    # Create a mock object returning states on successive calls
    mockStateClient.GetOne = MagicMock(side_effect=stateReturn)
    # Set up the return value of the state, if present
    type(mockState).value = PropertyMock(return_value=stateVal)

    # Create a mock object returning configs
    mockConfigClient.GetOne = MagicMock(side_effect=confReturn)
    # Set up the return value of the state, if present
    type(mockConfig.value).remove = PropertyMock(return_value=confRm)

    with patch('cloudvision.cvlib.studio.getWorkspaceLastSynced',
               return_value=time.time()):
        if errCode:
            with pytest.raises(RpcError) as excInfo:
                GetOneWithWS(mockApiClientGetter, mockStub, mockGetReq, mockStub, mockGetReq)
            assert excInfo.value.code() == errCode
        else:
            val = GetOneWithWS(mockApiClientGetter, mockStub, mockGetReq, mockStub, mockGetReq)
            if confRm:
                assert val is None
            else:
                assert val == stateVal
