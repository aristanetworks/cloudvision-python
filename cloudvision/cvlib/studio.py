# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from typing import Dict, List
import json
from fmp import wrappers_pb2 as fmp_wrappers
import google.protobuf.wrappers_pb2 as pb
from grpc import StatusCode, RpcError
from arista.studio.v1 import models, services

from .constants import (
    INPUT_PATH_ARG,
    STUDIO_ID_ARG,
    WORKSPACE_ID_ARG,
)
from .exceptions import (
    InputException,
    InputNotFoundException,
    InputRequestException,
    InputUpdateException
)
from .utils import extractJSONEncodedListArg

MAINLINE_WS_ID = ""


class Studio:
    '''
    Object to store studio context:
    - workspaceId:  Id of the workspace
    - studioId:     Id of the studio
    - inputs:       inputs provided to the studio
    - deviceIds:    Ids of the devices associated with this studio
    - logger:       The logger to be used with this studio
    - execId:       Id of the execution
    - buildId:      Id of the studio build
    '''

    def __init__(self, workspaceId: str, studioId: str, inputs=None,
                 deviceIds=None, logger=None, execId=None, buildId=None):
        self.workspaceId = workspaceId
        self.studioId = studioId
        self.inputs = inputs
        self.deviceIds = deviceIds
        self.logger = logger
        self.execId = execId
        self.buildId = buildId


def getStudioInputs(clientGetter, studioId: str, workspaceId: str, path: List[str] = []):
    '''
    Uses the passed ctx.getApiClient function reference to
    issue a get to the Studio inputs rAPI to get the
    associated studio inputs using the passed path.
    Path MUST be a non-None list, and omitting this argument retrieves the full studio input tree
    '''
    if path is None:
        raise TypeError("Path must be a non-None value")
    client = clientGetter(services.InputsServiceStub)
    wid = pb.StringValue(value=workspaceId)
    sid = pb.StringValue(value=studioId)
    key = models.InputsKey(studio_id=sid, workspace_id=wid,
                           path=fmp_wrappers.RepeatedString(values=path))
    req = services.InputsRequest(key=key)
    try:
        resp = client.GetOne(req)
        inputs = json.loads(resp.value.inputs.value)
        return inputs
    except Exception as e:
        raise InputRequestException(path, e)


def setStudioInput(clientGetter, studioId: str, workspaceId: str, inputPath: List[str], value: str):
    '''
    Uses the passed ctx.getApiClient function reference to
    issue a set to the Studio inputs rAPI with the associated input path and value
    '''
    client = clientGetter(services.InputsConfigServiceStub)
    wid = pb.StringValue(value=workspaceId)
    sid = pb.StringValue(value=studioId)
    key = models.InputsKey(studio_id=sid,
                           workspace_id=wid,
                           path=fmp_wrappers.RepeatedString(values=inputPath))

    req = services.InputsConfigSetRequest(
        value=models.InputsConfig(key=key, inputs=pb.StringValue(value=json.dumps(value)))
    )
    try:
        client.Set(request=req)
    except Exception as e:
        raise InputUpdateException(inputPath, f"Value {value} was not set: {e}")


def extractInputElems(inputs, inputPath: List[str], elems: List[str] = [],
                      tagElems: List[str] = []):
    '''
    Takes lists of elements and tag elements, and traverses through the input tree towards the
    Input path, extracting the most recent matching values for these elements from the inputs.

    Returns these results in a single dict, so overwriting of results will occur if specified
    elements/tag elements have the same name in the inputs tree
    '''
    results = {}
    currInput = inputs
    # Go through the input path to find the associated elements
    # tags are stored in the form "tags":{ "query": "<tag>:<value>" }
    for pthElem in inputPath:

        # Check the current input element for existence of wanted elements
        for elem in elems:
            if elem in currInput:
                results[elem] = currInput[elem]

        # Check the current input element for existence of wanted tag elements
        if "tags" in currInput:
            query = currInput["tags"]["query"]
            for elem in tagElems:
                # Add the colon used to separate value and tag in the query
                tagElem = elem + ":"
                if tagElem in query:
                    results[elem] = query[len(tagElem):]

        try:
            currInput = currInput[pthElem]
        except TypeError:
            # Stringified input path will stringify all elements, even integer values,
            # so there are cases where list elements are attempted to be accessed with
            # stringified indices. Attempt conversion to int and retry
            try:
                idx = int(pthElem)
                currInput = currInput[idx]
            except IndexError as idxE:
                raise InputNotFoundException(inputPath, f"'{pthElem}' {idxE}") from None
            except (TypeError, ValueError):
                raise InputNotFoundException(inputPath) from None
        except (KeyError, IndexError) as e:
            raise InputNotFoundException(inputPath, f"{e} not present in inputs") from None
        # Ensure sane value and allow for current input to be None
        if currInput is None and pthElem != inputPath[-1]:
            raise InputNotFoundException(inputPath)

    return results


def getSimpleResolverQueryValue(query: str):
    '''
    Autofill action arguments may be resolver queries. In these cases the string
    argument is in the form of "<tag>:<Value>" or more complex queries such as
    "<tag>:<ValueA> OR <tag>:<ValueB>". This function is designed to extract the
    query values from a simple query.

    Params:
    - query:   The simple query string, e.g. "<tag>:<Value>"

    Returns:
    - The query value, e.g. "<Value>" from the above example.

    Raises an InputException in the case where the passed query is not parsable as a simple query
    '''
    queryElems = query.split(":")
    if len(queryElems) == 1:
        raise InputException(f"Passed 'query' \"{query}\" does not appear to be a query")
    if len(queryElems) > 2:
        raise InputException(f"Passed query \"{query}\" is a complex query")
    queryValue = queryElems[1]
    if len(queryValue) == 0:
        raise InputException(f"Passed query \"{query}\" is missing a value")
    return queryValue


def extractStudioInfoFromArgs(args: Dict):
    '''
    Studio Autofill actions contains studio related information in their arguments, but a studio
    is not instantiated and associated with the context. As these actions require interfacing with
    studio APIs, this function extracts the studio info (verifies this info is valid if needed)
    and returns it to the user in the order below.

    These are (All return values may be None in the case the field is not present);
    - StudioID:     The ID of the studio associated with the action
    - WorkspaceID:  The ID of the workspace associated with the
    - InputPath:    The string path elements leading to the input element in the action

    NOTE: Input paths containing array/list indices will be stringified, so use caution when
    iterating through the input tree using this. These are not converted to integer values
    as they could clash with elements containing only numbers.
    The `extractInputElems` method accounts for this and is suggested over manually traversing
    the tree looking for elements
    '''
    studioId = args.get(STUDIO_ID_ARG)
    workspaceId = args.get(WORKSPACE_ID_ARG)
    inputPath = None
    inputPathArg = args.get(INPUT_PATH_ARG)  # This is a stringified list
    if inputPathArg:
        try:
            inputPath = extractJSONEncodedListArg(inputPathArg)
        except ValueError as e:
            raise ValueError("Studio input path must be a list of strings") from e
    return studioId, workspaceId, inputPath


def GetOneWithWS(apiClientGetter, stateStub, stateGetReq, configStub, confGetReq):
    '''
    For Studio APIs, the state for a particular workspace can be difficult to determine.
    A state for a particular workspace only exists if an update has occurred for that workspace.
    State may exist in mainline, or the configuration change in the workspace may have explicitly
    deleted the state.

    GetOneWithWS does the following to try and provide state for the get request:
        - Do a get on the X state endpoint in the particular workspace for the desired state
        - If the state does NOT exist, issue another get on the X state endpoint for the
          mainline state.
        - If the state DOES exist there, check the X configuration endpoint of the workspace to
          see if the state has been explicitly deleted there.

    Params:
    - apiClientGetter:  The API client getter, i.e. ctx.getApiClient
    - stateStub:        The stub for the state endpoint
    - stateGetReq:      A workspace-aware get request to be made to the state client for the
                        desired workspace. It is assumed that the get request has a key field
                        "workspace_id", such that mainline can be queried in the case that the
                        workspace query does not return anything.
    - configStub:       The stub for the config endpoint
    - confGetReq:       A workspace-aware get request to be made to the config client for the
                        desired workspace.

    Returns:
    - The request's value, or None if the resource has been deleted
    '''

    if not hasattr(stateGetReq.key, 'workspace_id'):
        raise ValueError("Passed request to GetOneWithWS has no key attribute 'workspace_id'")

    stateClient = apiClientGetter(stateStub)
    # Issue a get to the state endpoint for the workspace
    try:
        result = stateClient.GetOne(stateGetReq)
    except RpcError as exc:
        # If the state does not exist for the workspace, reraise the original
        # exception as something went wrong
        if exc.code() != StatusCode.NOT_FOUND:
            raise

        # In the case where the original get req is for the mainline,
        # nothing further we can do
        if stateGetReq.key.workspace_id.value == MAINLINE_WS_ID:
            raise

        # Try again for the mainline state
        stateGetReq.key.workspace_id.value = MAINLINE_WS_ID
        try:
            result = stateClient.GetOne(stateGetReq)
        except RpcError as mainlineExc:
            # Handle the mainline error as its own exception, such that stack
            # traces don't contain nested exceptions such as "when handling the
            # above exception, another exception occurred"
            raise mainlineExc from None

        # Check the config endpoint for the workspace to ensure that
        # the mainline value has not been deleted
        configClient = apiClientGetter(configStub)
        try:
            configResp = configClient.GetOne(confGetReq)
        except RpcError as confExc:
            # If the config does not exist for the workspace, return the mainline state
            if confExc.code() == StatusCode.NOT_FOUND:
                return result.value
            # Handle the config error as its own exception, such that stack
            # traces don't contain nested exceptions such as "when handling the
            # above exception, another exception occurred"
            raise confExc from None

        # Remove is a config field for workspace-aware configuration apis
        # If it is set it means that configuration has been explicitly
        # deleted for this ws
        if configResp.value.remove:
            # Config has been explicitly removed, return nothing
            return None

    return result.value
