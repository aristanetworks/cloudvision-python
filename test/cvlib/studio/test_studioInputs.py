# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest
from unittest.mock import MagicMock, PropertyMock, patch
import google.protobuf.wrappers_pb2 as pb
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import StatusCode, RpcError

from cloudvision.cvlib import (
    getStudioInputs,
    setStudioInput,
    setStudioInputs,
    InputException,
    InputNotFoundException,
    InputUpdateException,
)
from cloudvision.cvlib.constants import MAINLINE_WS_ID
from cloudvision.cvlib.studio import mergeStudioInputs

from arista.studio.v1 import models, services
from fmp import wrappers_pb2 as fmp_wrappers


rpcNotFound = RpcError()
rpcNotFound.code = lambda: StatusCode.NOT_FOUND

rpcInternal = RpcError()
rpcInternal.code = lambda: StatusCode.INTERNAL


mockState = MagicMock(name="state")
mockConfig = MagicMock(name="config")

mockStub = MagicMock(name="stub")

cases = [
    # Elements in cases are in the following order
    # name
    # ws for get req
    # input path to issue the request to
    # return values for state get calls (1st for ws, 2nd for mainline, if applicable)
    # expected value for the state.value attr
    # return values for config get call
    # expected value for the config.remove.value attr
    # expected input return value
    # expected exception
    # expected error code (if grpc error)
    [
        "failure, path is None",
        "test-WS-ID",
        None,
        [rpcInternal, None],
        [""],
        [None],
        [False],
        {},
        None,
        StatusCode.INTERNAL,
    ],
    [
        "success, path is root, 1st get ok",
        MAINLINE_WS_ID,
        [],
        [[mockState], [None]],
        [
            models.Inputs(inputs=pb.StringValue(value="{\"apple\":\"banana\"}"))
        ],
        [None],
        [False],
        {"apple": "banana"},
        None,
        None,
    ],
    [
        "failure, path is root, ws is mainline, 1st get empty",
        MAINLINE_WS_ID,
        [],
        [[]],
        [],
        [None],
        [False],
        None,
        InputNotFoundException([], "Mainline inputs for studio test_studio_id do not exist"),
        None,
    ],
    [
        "failure, path is root, ws not mainline, 1st get empty, mainline get empty",
        "test-WS-ID",
        [],
        [[], []],
        [],
        [mockConfig],
        [False],
        None,
        InputNotFoundException([], "Inputs for studio test_studio_id do not exist"),
        None,
    ],
    [
        "success, path is root, ws not mainline, 1st get empty, mainline get ok",
        "test-WS-ID",
        [],
        [[], [mockState]],
        [
            models.Inputs(inputs=pb.StringValue(value="{\"apple\":\"banana\"}"))
        ],
        [mockConfig],
        [False],
        {"apple": "banana"},
        None,
        None,
    ],
    [
        "failure, path is root, ws not mainline, ws get empty, mainline get ok, config remove",
        "test-WS-ID",
        [],
        [[], [mockState]],
        [
            models.Inputs(inputs=pb.StringValue(value="{\"apple\":\"banana\"}"))
        ],
        [mockConfig],
        [True],
        None,
        InputNotFoundException([], (f"Inputs for studio test_studio_id at path {[]} in "
                                    f"workspace test-WS-ID have been deleted")),
        None,
    ],
    [
        "failure, path is not root, ws not mainline, ws get empty, mainline get ok, config remove",
        "test-WS-ID",
        ["a", "b", "c"],
        [[], [mockState]],
        [
            models.Inputs(inputs=pb.StringValue(value="{\"apple\":\"banana\"}"))
        ],
        [mockConfig, mockConfig, mockConfig, mockConfig],
        [False, False, False, True],
        None,
        InputNotFoundException(
            ["a", "b", "c"], (f"Inputs for studio test_studio_id at path {[]} in "
                              f"workspace test-WS-ID have been deleted")),
        None,
    ],
    [

        ("failure, path is root, ws not mainline, ws get empty, mainline get ok,"
         " subpath has config remove"),
        "test-WS-ID",
        ["a", "b", "c"],
        [[], [mockState]],
        [
            models.Inputs(inputs=pb.StringValue(value="{\"apple\":\"banana\"}"))
        ],
        [mockConfig, mockConfig, mockConfig],
        [False, True, False],
        None,
        InputNotFoundException(
            ["a", "b", "c"], (f"Inputs for studio test_studio_id at path {[]} in "
                              f"workspace test-WS-ID have been deleted")),
        None,
    ],
    [
        ("success, path is not root, ws not mainline, 1st get empty, mainline get ok,"
         " will return inputs at that path only"),
        "test-WS-ID",
        ["a", "2", "c"],
        [[], [mockState]],
        [
            models.Inputs(
                key=models.InputsKey(path=fmp_wrappers.RepeatedString(values=["a", "2", "c"])),
                inputs=pb.StringValue(value="{\"apple\":\"banana\"}"),
            )
        ],
        [mockConfig, mockConfig, rpcNotFound, mockConfig],
        [False, False, False],
        {"apple": "banana"},
        None,
        None,
    ],
]


@pytest.mark.parametrize(
    'name, ws, path, stateReturn, stateVal, confReturn, confRm, expInputs, expException, errCode',
    cases)
def test_getStudioInputs(name, ws, path, stateReturn, stateVal, confReturn, confRm, expInputs,
                         expException, errCode):
    mockApiClientGetter = MagicMock(name="clientGetter")
    mockStateClient = MagicMock(name="stateClient")
    mockConfigClient = MagicMock(name="configClient")

    def mocked_client_getter(*args, **kwargs):
        if args[0] == services.InputsServiceStub:
            return mockStateClient
        else:
            return mockConfigClient
    mockApiClientGetter.side_effect = mocked_client_getter

    # Create a mock object returning states on successive calls
    mockStateClient.GetAll = MagicMock(name="stateGetAll", side_effect=stateReturn)
    # Set up the return value of the state, if present
    type(mockState).value = PropertyMock(name="stateVal", side_effect=stateVal)

    # Create a mock object returning configs
    mockConfigClient.GetOne = MagicMock(name="confGetOne", side_effect=confReturn)
    # Set up the return values of what the config remove flag being set is, if present
    type(mockConfig.value.remove).value = PropertyMock(name="confRemoveVal", side_effect=confRm)

    with patch('cloudvision.cvlib.studio.getWorkspaceLastSynced',
               return_value=Timestamp(seconds=123456)):
        if path is None:
            with pytest.raises(TypeError) as excInfo:
                getStudioInputs(mockApiClientGetter, "test_studio_id", ws, path)
            assert str(excInfo.value) == "Path must be a non-None value"
        elif expException:
            # Create a mock object raising exception
            mockStateClient.GetOne = MagicMock(side_effect=stateReturn)
            with pytest.raises(InputNotFoundException) as excInfo:
                getStudioInputs(mockApiClientGetter, "test_studio_id", ws, path)
            assert excInfo.value.message == expException.message
        elif errCode:
            with pytest.raises(RpcError) as excInfo:
                getStudioInputs(mockApiClientGetter, "test_studio_id", ws, path)
                assert excInfo.value.code() == errCode
        else:
            inputs = getStudioInputs(mockApiClientGetter, "test_studio_id", ws, path)

            assert expInputs == inputs


mergeCases = [
    # Elements in cases are in the following order
    # name
    # Tuple list of paths and their inputs to merge
    # Expected final inputs
    [
        "single input obj at root path",
        [
            ([], {"apple": "banana"})
        ],
        {
            "apple": "banana"
        }
    ],
    [
        "single input obj at random path",
        [
            (["a", "b", "c"], {"apple": "banana"})
        ],
        {
            "a": {
                "b": {
                    "c": {
                        "apple": "banana"
                    }
                }
            }
        }
    ],
    [
        "multiple input obj and lists at multiple paths",
        [
            ([], {"apple": "banana"}),
            (["a"], {"pineapple": "watermelon"}),
            (["a", "b"], {"orange": "pear"}),
            (["a", "b", "c"], {"apple": "banana"}),
            (["a", "b", "d", "0"], "a"),
            (["a", "b", "d", "2"], "c"),
            (["a", "b", "d", "1"], "b"),
            (["a", "b", "e"], ["d", "e", "f"]),
            (["a", "b", "e", "5"], ["x", "y", "z"]),
            (["a", "b", "e", "4"], {"cherry", "melon"}),
        ],
        {
            "apple": "banana",
            "a": {
                "pineapple": "watermelon",
                "b": {
                    "orange": "pear",
                    "c": {
                        "apple": "banana",
                    },
                    "d": ["a", "b", "c"],
                    "e": ["d", "e", "f", None, {"cherry", "melon"}, ["x", "y", "z"]]
                }
            }
        }
    ],
]


@pytest.mark.parametrize('name, inputTupleList, expectedInputs', mergeCases)
def test_mergeStudioInputs(name, inputTupleList, expectedInputs):
    inputs = None
    for path, inputToInsert in inputTupleList:
        inputs = mergeStudioInputs(inputs, path, inputToInsert)
    assert inputs == expectedInputs


setCases = [
    # Elements in cases are in the following order
    # name
    # value to set
    # return value/exception for config set call
    # expected exception
    # expected exception type (for handler)
    [
        "success, value is None",
        None,
        None,
        None,
        None,
    ],
    [
        "failure, value is not json serializable",
        bytes([1, 2, 3, 4]),
        None,
        InputException(
            "Cannot set value as input: Object of type bytes is not JSON serializable"),
        InputException,
    ],
    [
        "success, value to set is string",
        "test string",
        None,
        None,
        None,
    ],
    [
        "failure, value to set is string, but set failure",
        "test string",
        rpcInternal,
        InputUpdateException(["a", "b", "c"], "Value test string was not set: "),
        InputUpdateException,
    ],
]


@pytest.mark.parametrize('name, value, setReturn, expException, expExceptionType', setCases)
def test_setStudioInputs(name, value, setReturn, expException, expExceptionType):
    mockApiClientGetter = MagicMock(name="clientGetter")
    mockConfigClient = MagicMock(name="configClient")

    mockApiClientGetter.return_value = mockConfigClient
    mockConfigClient.Set = MagicMock(name="confSet", side_effect=setReturn)
    mockConfigClient.SetSome = MagicMock(name="confSetSome", side_effect=setReturn)

    if expException:
        with pytest.raises(expExceptionType) as excInfo:
            setStudioInput(
                mockApiClientGetter, "test_studio_id", "test-WS-ID", ["a", "b", "c"], value)
        assert excInfo.value.message == expException.message
        with pytest.raises(expExceptionType) as excInfoSetSome:
            setStudioInputs(
                mockApiClientGetter, "test_studio_id", "test-WS-ID", [(["a", "b", "c"], value)])
        assert excInfoSetSome.value.message == expException.message
    else:
        setStudioInput(mockApiClientGetter, "test_studio_id", "test-WS-ID", ["a", "b", "c"], value)
        setStudioInputs(
            mockApiClientGetter, "test_studio_id", "test-WS-ID", [(["a", "b", "c"], value)])
