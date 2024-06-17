# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from google.protobuf import wrappers_pb2 as pb
from grpc import StatusCode, RpcError
from typing import List, Optional

from arista.workspace.v1 import models, services

from .constants import MAINLINE_WS_ID, TIMEOUT_REQUEST
from .exceptions import CVException


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


def getWorkspaceLastSynced(clientGetter, workspaceId: str):
    """
    Gets the lastRebasedAt timestamp for the given workspace, or if that's null,
    the createdAt timestamp of the workspace. This function allows for workspace-aware
    resource apis to gather accurate data when needing to fall back to mainline for building
    accurate state in a workspace.

    Params:
        clientGetter:   The API client getter, i.e. ctx.getApiClient
        workspaceId:    The ID of the workspace to retrieve the timestamp for

    Returns:
        Timestamp object of the workspace's last rebased time, or created at time

    Raises:
        CVException:    If the workspace does not exist, or is mainline
    """

    if workspaceId == MAINLINE_WS_ID:
        raise CVException("Workspace ID provided is mainline, does not have a sync time")
    # Get the lastRebasedAt timestamp for the given workspace, or if that's null,
    # the createdAt timestamp of the workspace such that accurate mainline state is retrieved
    wsClient = clientGetter(services.WorkspaceServiceStub)
    wid = pb.StringValue(value=workspaceId)
    key = models.WorkspaceKey(workspace_id=wid)
    wsReq = services.WorkspaceRequest(key=key)
    try:
        wsResp = wsClient.GetOne(wsReq, timeout=TIMEOUT_REQUEST)
    except RpcError as wsExec:
        if wsExec.code() == StatusCode.NOT_FOUND:
            raise CVException("Workspace does not exist")
        raise wsExec from None
    # last_rebased_at is truthy even if not set,
    # need to check seconds and nanos to ensure that it exists
    rebased = wsResp.value.last_rebased_at
    rebasedSet = rebased.seconds or rebased.nanos
    # if last_rebased DOES exist, return it, otherwise the workspace creation time
    wsTs = rebased if rebasedSet else wsResp.value.created_at

    return wsTs
