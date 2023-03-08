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
    Execution,
    User,
    Logger,
    LoggingLevel
)

from cloudvision.cvlib.exceptions import (
    DeviceCommandsFailed,
    InvalidContextException
)


user = User("test_user", "123")

device = Device(ip="123.456.789", deviceId="JP123456",
                deviceMac="00-B0-D0-63-C2-26")

action = Action(
    name="test_action",
    context=ActionContext.ChangeControl,
    actionId="1234"
)

execution = Execution(executionId="2")

ctx_high_logging = Context(
    user=user,
    device=device,
    action=action,
    execution=execution
)

logsCalls = 0


def alog(a, b, c, d):
    pass


def log_high(a, b):
    global logsCalls
    logsCalls += 1


logger_high = Logger(
    alog=alog,
    trace=log_high,
    debug=log_high,
    info=log_high,
    warning=log_high,
    error=log_high,
    critical=log_high
)

ctx_high_logging.logger = logger_high

ctx_high_logging.setLoggingLevel(LoggingLevel.Critical)

ctx_low_logging = Context(
    user=user,
    device=device,
    action=action,
    execution=execution
)


def log_low(a, b):
    global logsCalls
    logsCalls += 1


logger_low = Logger(
    alog=alog,
    trace=log_low,
    debug=log_low,
    info=log_low,
    warning=log_low,
    error=log_low,
    critical=log_low
)

ctx_low_logging.logger = logger_low

ctx_low_logging.setLoggingLevel(LoggingLevel.Trace)

logging_cases = [
    ("critical_logging", ctx_high_logging, 1),
    ("trace_logging", ctx_low_logging, 7)
]


@pytest.mark.parametrize('name, inp, expected', logging_cases)
def test_logging(name, inp, expected):
    inp.trace("logTrace")
    inp.debug("logDebug")
    inp.info("logInfo")
    inp.warning("logWarning")
    inp.error("logError")
    inp.critical("logCritical")
    assert logsCalls == expected


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
