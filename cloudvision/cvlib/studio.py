# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

class Studio:
    '''
    Object to store studio context:
    - workspaceId:  Id of the workspace
    - studioId:     Id of the studio
    - inputs:       inputs provided to the studio
    - deviceIds:    Ids of the devices associated with this studio
    - logger:       The logger to be used with this studio
    '''

    def __init__(self, workspaceId: str, studioId: str, inputs, deviceIds, logger, execId):
        self.workspaceId = workspaceId
        self.studioId = studioId
        self.inputs = inputs
        self.deviceIds = deviceIds
        self.logger = logger
        self.execId = execId
