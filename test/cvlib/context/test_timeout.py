# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest

from cloudvision.cvlib import Context, InvalidContextException, User


def test_do_with_timeout():
    ctx = Context(user=User("test_user", "123"))

    # Function that is ok to use in a doWithTimeout
    def okFunc():
        print("ok")

    # Function that is not ok to use in a doWithTimeout
    def exceptionFunc():
        ctx.doWithTimeout(okFunc, 5)

    # Run a function that will pass, though will have set up the
    # necessary alarms and then unset them
    ctx.doWithTimeout(okFunc, 5)

    # Run a function that will fail as it is recursively calling doWithTimeout
    with pytest.raises(InvalidContextException) as exc_info:
        ctx.doWithTimeout(exceptionFunc, 5)
    assert "Cannot recursively call doWithTimeout" in str(exc_info.value)

    # Run ok function once again to make sure that previous exception still unset the handler
    ctx.doWithTimeout(okFunc, 5)
