# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from typing import Dict, Optional

from cloudvision.Connector.grpc_client import GRPCClient

from .utils import queryCCStartTime


class ChangeControl:
    '''
    (Deprecated) Please use ctx.action instead for various field information
    Object to store common change control action script arguments:
    - ccId:         ID of the change control, if applicable
    - stageId:      ID of the current stage of the change control, if applicable
    - args:         Dict of user-defined/script defined arguments that are passed in
    '''

    def __init__(self,
                 ccId: Optional[str] = None,
                 stageId: Optional[str] = None,
                 args: Optional[Dict[str, str]] = None):
        self.ccId = ccId
        self.stageId = stageId
        self.args = args
        self.__ccStartTime: Optional[int] = None

    def getStartTime(self, cvClient: GRPCClient):
        '''
        Queries the cloudvision database for the change control start time
        :param cvClient:  context.getCvClient() client
        :return:          nanosecond start timestamp of the change control
        '''
        if self.ccId is None:
            return None

        if self.__ccStartTime:
            return self.__ccStartTime

        ccStartTs = queryCCStartTime(cvClient, self.ccId)
        self.__ccStartTime = int(ccStartTs)
        return self.__ccStartTime
