# Copyright (c) 2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest

from cloudvision.cvlib import (
    Context,
    User,
    Logger,
    LoggingLevel
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
