# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from typing import List, Optional


class Workspace:
    '''
    Object to store workspace context:
    - id:           Id of the workspace
    - studioIds:    Ids of the studios edited in the associated workspace
    - buildId:      Id of the workspace build
    '''

    def __init__(self, workspaceId: str, studioIds: List[str] = [], buildId: Optional[str] = None):
        self.id = workspaceId
        self.studioIds = studioIds
        self.buildId = buildId
