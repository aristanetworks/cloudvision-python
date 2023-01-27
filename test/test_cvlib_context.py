# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest

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

cases = [
    ("critical_logging", ctx_high_logging, 1),
    ("trace_logging", ctx_low_logging, 7)
]


@pytest.mark.parametrize('name, inp, expected', cases)
def test_logging(name, inp, expected):
    inp.trace("logTrace")
    inp.debug("logDebug")
    inp.info("logInfo")
    inp.warning("logWarning")
    inp.error("logError")
    inp.critical("logCritical")
    assert logsCalls == expected
