# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest
from http import HTTPStatus
from unittest.mock import Mock, patch

from cloudvision.cvlib import (
    Action,
    ActionContext,
    AuthAndEndpoints,
    Context,
    Device,
    User
)

from cloudvision.cvlib.exceptions import (
    DeviceCommandsFailed,
    InvalidContextException
)


device_no_host = Device(ip="123.456.789", deviceId="JPE123456",
                        deviceMac="00-B0-D0-63-C2-26")

device_no_id = Device(ip="123.456.789",
                      deviceMac="00-B0-D0-63-C2-26")

cases_get_host_name = [
    (
        "no_device",
        None,
        InvalidContextException,
        "getDeviceHostname requires either a device or the"
        " calling context to have a device associated with it",
        None
    ),
    (
        "no_device_host_name",
        device_no_host,
        DeviceCommandsFailed,
        f"'show hostname' failed on device {device_no_host.id} with response:",
        [
            {},
            {'errorCode': '341604', 'errorMessage': 'Invalid request'},
            {}
        ]
    ),
    (
        "no_device_host_name_error",
        device_no_host,
        DeviceCommandsFailed,
        f"'show hostname' failed on device {device_no_host.id} with error:",
        [
            {},
            {'error': '341604'}
        ]
    )
]


@pytest.mark.parametrize('name, device, exception, expected, returnVals', cases_get_host_name)
def test_get_host_name_exception(name, device, exception, expected, returnVals):
    ctx = Context(
        user=User("test_user", "123"),
        device=device,
    )

    ctx.runDeviceCmds = Mock(return_value=returnVals)

    with pytest.raises(exception) as excinfo:
        ctx.getDeviceHostname(ctx.device)
    assert expected in str(excinfo.value)


action = Action(
    name="test_action",
    context=ActionContext.ChangeControl,
    actionId="1234"
)

device = Device(ip="123.456.789", deviceId="JP123456",
                deviceMac="00-B0-D0-63-C2-26")

cases_run_device_cmds_exp = [
    (
        "no action",
        None,
        None,
        "runDeviceCmds is only available in action contexts"
    ),
    (
        "no device",
        None,
        action,
        "runDeviceCmds is only available when a device is set"
    ),
    (
        "no device id",
        device_no_id,
        action,
        "runDeviceCmds requires a device with an id"
    ),
    (
        "no connection",
        device,
        action,
        "runDeviceCmds must have a valid service "
        "address and command endpoint specified"
    )
]


@pytest.mark.parametrize('name, device, action, expected', cases_run_device_cmds_exp)
def test_runDeviceCmds_exception(name, device, action, expected):
    ctx = Context(
        user=User("test_user", "123"),
        device=device,
        action=action
    )

    with pytest.raises(InvalidContextException) as excinfo:
        ctx.runDeviceCmds(["enable", "show hostname"], ctx.device)
    assert expected in str(excinfo.value)


cases_run_device_cmds = [
    (
        "failure in request",
        {'errorCode': '341604', 'errorMessage': 'Invalid request'},
        True,
        f"Commands failed to run on device \"{device.id}\", returned 341604:\"Invalid request\""
    ),
    (
        "Command failed",
        [
            {"response": "", "error": ""},
            {"response": "", "error": "Ambiguous command (at token 1)"},
        ],
        True,
        (f"Command \"testCommand\" failed to run on device \"{device.id}\","
         " returned Ambiguous command (at token 1)")
    ),
    (
        "Command passed",
        [
            {"response": "", "error": ""},
            {"response": "Test command success", "error": ""},
        ],
        False,
        "Test command success"
    ),
]


@pytest.mark.parametrize('name, mockedResp, exception, expected', cases_run_device_cmds)
def test_runDeviceCmds(name, mockedResp, exception, expected):

    conns = AuthAndEndpoints(
        serviceAddr="localhost",
        commandEndpoint="commands",
    )
    ctx = Context(
        user=User("test_user", "123"),
        connections=conns,
        device=device,
        action=action,
    )

    def mocked_request_resp(*args, **kwargs):
        class MockResponse:
            def __init__(self, data, status_code):
                self.json_data = data
                self.status_code = status_code

            def json(self):
                return self.json_data

        return MockResponse(mockedResp, HTTPStatus.OK)

    with patch('cloudvision.cvlib.context.requests.post', side_effect=mocked_request_resp):
        if exception:
            with pytest.raises(DeviceCommandsFailed) as excinfo:
                ctx.runDeviceCmds(["enable", "testCommand"])
            assert expected in str(excinfo.value), "Unexpected exception"
        else:
            resp = ctx.runDeviceCmds(["enable", "testCommand"])
            assert expected == resp[1]["response"], "Response is not expected"
