# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest

from unittest import mock

from cloudvision.cvlib import (
    Action,
    ActionContext,
    Context,
    Device,
    User,
    Logger,
    LoggingLevel
)

from cloudvision.cvlib.exceptions import (
    DeviceCommandsFailed,
    InvalidContextException
)

loggingTestCases = [
    ("critical_logging", LoggingLevel.Critical, 1),
    ("trace_logging", LoggingLevel.Trace, 6)
]


@pytest.mark.parametrize('name, logLevel, expectedLogCalls', loggingTestCases)
def test_logging(name, logLevel, expectedLogCalls):

    def alog(a, b, c, d):
        pass

    logCalls = 0

    def log(a, b):
        nonlocal logCalls
        logCalls += 1

    logger = Logger(alog, log, log, log, log, log, log)
    ctx = Context(
        user=User("test_user", "123"),
        logger=logger
    )
    ctx.setLoggingLevel(logLevel)
    ctx.trace("logTrace")
    ctx.debug("logDebug")
    ctx.info("logInfo")
    ctx.warning("logWarning")
    ctx.error("logError")
    ctx.critical("logCritical")
    assert logCalls == expectedLogCalls


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

    ctx.runDeviceCmds = mock.Mock(return_value=returnVals)

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

cases_run_device_cmds = [
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


@pytest.mark.parametrize('name, device, action, expected', cases_run_device_cmds)
def test_runDeviceCmds_exception(name, device, action, expected):
    ctx = Context(
        user=User("test_user", "123"),
        device=device,
        action=action
    )

    with pytest.raises(InvalidContextException) as excinfo:
        ctx.runDeviceCmds(["enable", "show hostname"], ctx.device)
    assert expected in str(excinfo.value)
