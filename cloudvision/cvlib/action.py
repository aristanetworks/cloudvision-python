# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from enum import Enum
from typing import Dict, Optional

from cloudvision.Connector.grpc_client import GRPCClient

from .utils import queryCCStartTime


class ActionContext(Enum):
    '''
    Enum class used to store the various contexts in which actions are executed in
    '''
    Unknown = 0
    ChangeControl = 1
    StudioAutofill = 2


class Action:
    '''
    Object to store common change control action script arguments:
    - name:     Name of the action currently running
    - context:  Enum for the context in which the action is running,
                e.g. Action that is running is a change control action
    - actionId: ID of the action currently running
    - args:     String -> String dictionary of the args associated with the action
    - ccId:     ID of the change control, if applicable
    - stageId:  ID of the current stage of the change control, if applicable
    '''

    def __init__(self, name: str,
                 actionId: str,
                 context: ActionContext = ActionContext.Unknown,
                 args: Optional[Dict[str, str]] = None,
                 ccId: Optional[str] = None,
                 stageId: Optional[str] = None):
        self.name = name
        self.id = actionId
        self.context = context
        self.args = args
        self.ccId = ccId
        self.stageId = stageId

        # Fields used in some execution contexts
        self.__ccStartTime: Optional[int] = None

    def getCCStartTime(self, cvClient: GRPCClient):
        '''
        Queries the cloudvision database for the change control start time
        :param cvClient:  context.getCvClient() client
        :return:          nanosecond start timestamp of the change control
        '''
        if self.context != ActionContext.ChangeControl or not self.ccId:
            return None

        if self.__ccStartTime:
            return self.__ccStartTime

        ccStartTs = queryCCStartTime(cvClient, self.ccId)
        self.__ccStartTime = int(ccStartTs)
        return self.__ccStartTime
