# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from typing import Any, Callable, Optional


class Logger:
    '''
    Logger object that stores a number of user-defined logging functions
    Due to context being pickled at certain execution stages of actions/studios, a normal python
    logger cannot be used.
    Minimum required call signatures are described by the init function, where 'Any' denotes the
    context being passed to avoid cyclical imports
    - alog:     Function to be used for audit log insertion
    - trace:    Function to be used for trace level logging
    - debug:    Function to be used for debug level logging
    - info:     Function to be used for info level logging
    - warning:  Function to be used for warning level logging
    - error:    Function to be used for error level logging
    - critical: Function to be used for critical level logging
    '''

    def __init__(self,
                 alog: Optional[Callable[[Any, str, Optional[str], Optional[str]], None]] = None,
                 trace: Optional[Callable[[Any, str], None]] = None,
                 debug: Optional[Callable[[Any, str], None]] = None,
                 info: Optional[Callable[[Any, str], None]] = None,
                 warning: Optional[Callable[[Any, str], None]] = None,
                 error: Optional[Callable[[Any, str], None]] = None,
                 critical: Optional[Callable[[Any, str], None]] = None):
        self.alog = alog
        self.trace = trace
        self.debug = debug
        self.info = info
        self.warning = warning
        self.error = error
        self.critical = critical
