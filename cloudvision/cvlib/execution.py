# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

class Execution:
    '''
    Object to store standalone execution context:
    - executionId:  Key of the execution run, used by alog
    '''

    def __init__(self, executionId: str):
        self.executionId = executionId
