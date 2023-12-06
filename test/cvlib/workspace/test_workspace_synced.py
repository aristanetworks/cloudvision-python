# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest
from unittest.mock import MagicMock
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import StatusCode, RpcError
from cloudvision.cvlib import CVException
from cloudvision.cvlib.constants import MAINLINE_WS_ID
from cloudvision.cvlib.workspace import getWorkspaceLastSynced


rpcNotFound = RpcError()
rpcNotFound.code = lambda: StatusCode.NOT_FOUND

rpcInternal = RpcError()
rpcInternal.code = lambda: StatusCode.INTERNAL


mockStateRebased = MagicMock(name="rebased state")
mockStateRebasedVal = MagicMock(name="rebased state val")
mockStateRebasedVal.last_rebased_at = Timestamp(seconds=789012)
mockStateRebasedVal.created_at = Timestamp(seconds=123456)
mockStateRebased.value = mockStateRebasedVal

mockState = MagicMock(name="state")
mockedStateVal = MagicMock(name="state val")
mockedStateVal.last_rebased_at = Timestamp()
mockedStateVal.created_at = Timestamp(seconds=123456)
mockState.value = mockedStateVal

mockStub = MagicMock()

cases = [
    # Elements in case are in the following order
    # name
    # ws in get req
    # return values for state get calls (1st for ws, 2nd for mainline)
    # expected value for the state.value attr
    # expected return value
    # expected exception  (if cvlib exception expected)
    # expected error code (if RPC Error expected)
    [
        "failure WS state, is mainline",
        MAINLINE_WS_ID,
        None,
        0,
        CVException("Workspace ID provided is mainline, does not have a sync time"),
        None,
    ],
    [
        "failure querying WS state, rpc error",
        "test-WS-ID",
        rpcInternal,
        0,
        None,
        StatusCode.INTERNAL,
    ],
    [
        "failure querying ws, not found",
        "test-WS-ID",
        rpcNotFound,
        0,
        CVException("Workspace does not exist"),
        None,
    ],
    [
        "success, has rebased value",
        "test-WS-ID",
        mockStateRebased,
        Timestamp(seconds=789012),
        None,
        None,
    ],
    [
        "success, no rebase value, uses created_at WS",
        "test-WS-ID",
        mockState,
        Timestamp(seconds=123456),
        None,
        None,
    ],
]


@pytest.mark.parametrize('name, ws, stateReturn, stateVal, expException, errCode', cases)
def test_get_one(name, ws, stateReturn, stateVal, expException, errCode):
    mockApiClientGetter = MagicMock(name="client getter")
    mockStateClient = MagicMock(name="client")
    mockApiClientGetter.return_value = mockStateClient

    if expException:
        # Create a mock object raising exception
        mockStateClient.GetOne = MagicMock(side_effect=stateReturn)
        with pytest.raises(CVException) as excInfo:
            getWorkspaceLastSynced(mockApiClientGetter, ws)
        assert excInfo.value.message == expException.message
    elif errCode:
        # Create a mock object raising exception
        mockStateClient.GetOne = MagicMock(side_effect=stateReturn)
        with pytest.raises(RpcError) as excInfo:
            getWorkspaceLastSynced(mockApiClientGetter, ws)
        assert excInfo.value.code() == errCode
    else:
        mockStateClient.GetOne.return_value = stateReturn
        val = getWorkspaceLastSynced(mockApiClientGetter, ws)
        assert val == stateVal
