# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import json
from typing import Any, Dict, List, Tuple, Optional

import google.protobuf.wrappers_pb2 as pb
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import RpcError, StatusCode

from arista.studio.v1 import models, services
from arista.time.time_pb2 import TimeBounds
from cloudvision.Connector.codec import Path
from cloudvision.Connector.grpc_client import create_notification
from fmp import wrappers_pb2 as fmp_wrappers

from .constants import (
    INPUT_PATH_ARG,
    MAINLINE_WS_ID,
    STUDIO_ID_ARG,
    WORKSPACE_ID_ARG,
    TIMEOUT_REQUEST,
)
from .exceptions import (
    InputException,
    InputNotFoundException,
    InputUpdateException,
    InvalidContextException,
    InvalidCredentials,
)
from .utils import extractJSONEncodedListArg
from .workspace import getWorkspaceLastSynced


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


class StudioCustomData:
    '''
    Object to store studio custom data context:
    - context:   stores system and user-defined parameters.
    - chunk_size: chunk size of stored data.
    '''

    def __init__(self, context):
        self.context = context
        self.chunk_size = 1000 * 1024

    def __getBuildPath(self, studioId, path, key) -> List[str]:
        '''
        Builds a path for use in store/retrieve of studio custom data during a build
        using the studioId, path and key provided by the user. All paths contain
        "workspace/<wsId>/build/<buildId>/studio/<studioId>/customData" as the root.
        Raises InvalidContextException if not enough context information is present
        to create a key
        '''
        if (studioId and self.context and self.context.studio
                and self.context.studio.buildId):
            workpaceId = self.context.getWorkspaceId()
            return ["workspace", workpaceId, "status", "build",
                    self.context.studio.buildId, "studio", studioId,
                    "customData"] + path + [key]
        raise InvalidContextException(
            "store/retrieve requires context with studio and"
            + "build associated with it.")

    def __getMainlinePath(self, studioId, path, key) -> List[str]:
        '''
        Builds a path for use in retrieve of studio custom data from mainline
        using studioID, path and key. All paths contain
        "/studio/<studioId>/customData" as the root.
        '''
        return ["studio", studioId, "customData"] + path + [key]

    def store(self, data: str = "", path: List[str] = [], key: str = ""):
        '''
        store puts the passed studio custom data into a path in the Database.
        The data is stored in 1MB chunks.

        Params:
        - data:      The string data to be stored.
        - path:      The path to store the data at, in the form of a list of strings.
                     paths have "workspace/<wsId>/build/<buildId>/studio/<studioId>/customData"
                     as the root.
        - key:       The key to store the data at in the path.
         '''
        if not isinstance(data, str):
            raise TypeError("only string data is allowed.")
        if not self.context or not self.context.studio:
            raise InvalidContextException("store requires a studio in the context.")
        if not data:
            raise ValueError("no data added.")
        if not key:
            raise ValueError("invalid key.")

        ts = Timestamp()
        ts.GetCurrentTime()
        storagePath = self.__getBuildPath(self.context.studio.studioId, path, key)
        # Generate the list of path pointer notifs that lead to the new entry
        notifs = []
        for i, pathElem in enumerate(storagePath):
            # skip creation of workspace and build pointers
            if i <= 4:
                continue
            pathPointerPath = storagePath[:i]
            pathPointerUpdate = [(pathElem, Path(keys=storagePath[:i + 1]))]
            notifs.append(create_notification(ts, pathPointerPath,
                                              updates=pathPointerUpdate))

        try:
            self.context.getCvClient().publish(dId="cvp", notifs=notifs)
            # publish data
            for i in range(0, len(data), self.chunk_size):
                update = [(f"{key}_{i // self.chunk_size}", data[i:i + self.chunk_size])]
                notifs = [create_notification(ts, storagePath, updates=update)]
                self.context.getCvClient().publish(dId="cvp", notifs=notifs)
        except RpcError as exc:
            # If the exception is not a permissions error, reraise the original
            # exception as something went wrong
            if exc.code() != StatusCode.PERMISSION_DENIED:
                raise
            raise InvalidCredentials(
                f"Context user does not have permission to write to path '{storagePath}'")

    def retrieve(self, studioId: str = "", path: List[str] = [], searchKey: str = ""):
        '''
        retrieve gets the custom data from a path and key written by a studio
        in the Database.
        Params:
        - studioId:  The studioId of studio that generates the data to be retrieved.
        - path:      The path to get the data from, path is a list of strings.
        - key:       The key to get the data from in the path.
        '''
        if not studioId:
            raise ValueError("studioId must be provided")
        if not searchKey:
            raise ValueError("invalid key.")
        if not self.context:
            raise InvalidContextException("retrieve requires context to be set")

        try:
            data = dict()
            try:
                storagePath = self.__getBuildPath(studioId, path, searchKey)
                data = self.context.Get(storagePath, [], "cvp")
            except InvalidContextException as e:
                self.context.logger.info(
                    self.context, "custom data not found in build:  {}".format(e.message))
            # get data from mainline if data is not generated during build.
            if not data:
                self.context.logger.info(self.context, "reading custom data from mainline.")
                storagePath = self.__getMainlinePath(studioId, path, searchKey)
                data = self.context.Get(storagePath, [], "cvp")
            return ''.join(data[k] for k in
                           sorted(data.keys(), key=lambda x: int(x.split(f'{searchKey}_')[1]))
                           if isinstance(data[k], str))
        except RpcError as exc:
            if exc.code() != StatusCode.PERMISSION_DENIED:
                raise
            raise InvalidCredentials(
                f"Context user does not have permission to read from path '{storagePath}'")
        except IndexError:
            raise ValueError("Invalid Key format: {}".format(data.keys()))


def getStudioInputs(clientGetter, studioId: str, workspaceId: str, path: List[str] = []):
    '''
    Uses the passed ctx.getApiClient function reference to issue get the current input state for
    given combination of studioId, workspaceId and path.
    Path MUST be a non-None list, omitting this argument retrieves the full studio input tree.
    This function falls back to mainline state at workspace creation time (or last rebase time)
    to build up the state should the workspace studio state not be created yet and checks to see
    if any deletes would affect the requested input.

    Raises an InputNotFoundException if the input requested does not exist.
    '''
    if path is None:
        raise TypeError("Path must be a non-None value")

    inputs = __getStudioInputs(clientGetter, studioId, workspaceId)
    if not inputs:
        # If we're searching for inputs on mainline and we receive none from the getAll,
        # raise an exception
        if workspaceId == MAINLINE_WS_ID:
            raise InputNotFoundException(
                path, f"Mainline inputs for studio {studioId} do not exist")

        # Check the config endpoint for the workspace to ensure that
        # the mainline value has not been deleted
        # We need to check each individual subpath for deletes as they will take precedence
        # We don't need to check the timestamps as if they have been overwritten, then
        # state will exist and we will not reach here
        for i in range(len(path) + 1):
            subpath = path[:i]
            try:
                conf = __getStudioInputConfig(clientGetter, studioId, workspaceId, subpath)
            except InputNotFoundException:
                continue
            if conf.remove.value:
                raise InputNotFoundException(
                    path, (f"Inputs for studio {studioId} at path {path} in "
                           f"workspace {workspaceId} have been deleted"))

        # Get the lastRebasedAt timestamp, or if that's null, then the createdAt timestamp
        # of the workspace such that the correct mainline state is retrieved
        wsTs = getWorkspaceLastSynced(clientGetter, workspaceId)
        mainlineInputs = __getStudioInputs(clientGetter, studioId, MAINLINE_WS_ID,
                                           start=wsTs, end=wsTs)
        if not mainlineInputs:
            raise InputNotFoundException(path, f"Inputs for studio {studioId} do not exist")

        inputs = mainlineInputs

    # In the case where a path has been specified, the inputs reflect that subtree from the root
    # input, rather than from the specified path. We need to iterate through the inputs down to
    # the path desired to return only the requested portion

    finalInput = inputs
    for pthElem in path:
        try:
            finalInput = finalInput[pthElem]
        except TypeError:
            # Stringified input path will stringify all elements, even integer values,
            # so there are cases where list elements are attempted to be accessed with
            # stringified indices. Attempt conversion to int and retry
            try:
                idx = int(pthElem)
                finalInput = finalInput[idx]
            except IndexError as idxE:
                raise InputNotFoundException(path, f"'{pthElem}' {idxE}") from None
            except (TypeError, ValueError):
                raise InputNotFoundException(
                    path, f"{pthElem} not present in inputs {finalInput}") from None
        except (KeyError, IndexError) as e:
            raise InputNotFoundException(
                path, f"{pthElem} not present in inputs {finalInput}: {e}") from None

    return finalInput


def __getStudioInputs(clientGetter, studioId: str, workspaceId: str, start=None, end=None):
    client = clientGetter(services.InputsServiceStub)
    wid = pb.StringValue(value=workspaceId)
    sid = pb.StringValue(value=studioId)
    key = models.InputsKey(studio_id=sid, workspace_id=wid)
    p_filter = models.Inputs(key=key)

    startTs = None
    endTs = None
    if start:
        startTs = start
    if end:
        endTs = end
    timeBound = TimeBounds(start=startTs, end=endTs)
    req = services.InputsStreamRequest(time=timeBound)
    req.partial_eq_filter.append(p_filter)

    inputs = None
    # We need to issue the get requests as part of a GetAll to allow for truncated inputs
    for res in client.GetAll(req, timeout=TIMEOUT_REQUEST):
        inpResp = res.value
        if not inpResp.inputs:
            continue
        path = inpResp.key.path.values
        split = json.loads(inpResp.inputs.value)
        inputs = mergeStudioInputs(inputs, path, split)

    return inputs


def __getStudioInputConfig(clientGetter, studioId: str, workspaceId: str, path: List[str] = []):
    client = clientGetter(services.InputsConfigServiceStub)
    wid = pb.StringValue(value=workspaceId)
    sid = pb.StringValue(value=studioId)
    key = models.InputsKey(studio_id=sid, workspace_id=wid,
                           path=fmp_wrappers.RepeatedString(values=path))
    req = services.InputsConfigRequest(key=key)

    try:
        configResp = client.GetOne(req, timeout=TIMEOUT_REQUEST)
    except RpcError as confExc:
        # If the config does not exist for the workspace, return the mainline state
        if confExc.code() == StatusCode.NOT_FOUND:
            raise InputNotFoundException(
                path, (f"Config not found for input key with studio {studioId}"
                       f"workspace {workspaceId} and path {path}"))
        raise

    return configResp.value


def setStudioInput(clientGetter, studioId: str, workspaceId: str, inputPath: List[str],
                   value: str, remove: bool = False):
    '''
    Uses the passed ctx.getApiClient function reference to
    issue a set to the Studio inputs rAPI with the associated input path and value
    '''
    try:
        serialized = json.dumps(value)
    except TypeError as e:
        raise InputException(
            message=f"Cannot set value as input: {e}", inputPath=inputPath) from None
    client = clientGetter(services.InputsConfigServiceStub)
    wid = pb.StringValue(value=workspaceId)
    sid = pb.StringValue(value=studioId)
    key = models.InputsKey(studio_id=sid,
                           workspace_id=wid,
                           path=fmp_wrappers.RepeatedString(values=inputPath))
    if remove:
        req = services.InputsConfigSetRequest(
            value=models.InputsConfig(key=key, remove=pb.BoolValue(value=remove))
        )
    else:
        req = services.InputsConfigSetRequest(
            value=models.InputsConfig(key=key, inputs=pb.StringValue(value=serialized))
        )
    try:
        client.Set(request=req, timeout=TIMEOUT_REQUEST)
    except RpcError as exc:
        raise InputUpdateException(inputPath, f"Value {value} was not set: {exc}") from None


def setStudioInputs(clientGetter, studioId: str, workspaceId: str,
                    inputs: List[Tuple]):
    '''
    Uses the passed ctx.getApiClient function reference to
    issue a setSome to the Studio inputs rAPI with the associated InputsConfig

    The inputs list should contain tuples of a fixed size, either with a
    length of 2 or a length of 3. Tuple: (Path, Inputs) or (Path, Inputs, Remove)
    a mixed list [(path, value, remove), (path, value),..] is supported

    The value doesn't matter if the remove flag is True
    '''
    client = clientGetter(services.InputsConfigServiceStub)
    wid = pb.StringValue(value=workspaceId)
    sid = pb.StringValue(value=studioId)
    inputsConfigs = []
    for entry in inputs:
        if len(entry) == 2:
            path, value = entry
            key = models.InputsKey(studio_id=sid,
                                   workspace_id=wid,
                                   path=fmp_wrappers.RepeatedString(values=path))
            try:
                serialized = json.dumps(value)
            except TypeError as e:
                raise InputException(
                    message=f"Cannot set value as input: {e}", inputPath=path) from None
            item = models.InputsConfig(key=key, inputs=pb.StringValue(value=serialized))
        elif len(entry) == 3:
            path, value, remove = entry
            key = models.InputsKey(studio_id=sid,
                                   workspace_id=wid,
                                   path=fmp_wrappers.RepeatedString(values=path))
            try:
                serialized = json.dumps(value)
            except TypeError as e:
                raise InputException(
                    message=f"Cannot set value as input: {e}", inputPath=path) from None
            if remove:
                item = models.InputsConfig(key=key, remove=pb.BoolValue(value=remove))
            else:
                item = models.InputsConfig(key=key, inputs=pb.StringValue(value=serialized))
        else:
            raise InputException(
                message=f"Invalid entry length: {len(entry)}", inputPath=entry[0]) from None
        inputsConfigs.append(item)
    req = services.InputsConfigSetSomeRequest(
        values=inputsConfigs
    )
    try:
        for res in client.SetSome(request=req, timeout=TIMEOUT_REQUEST):
            pass
    except RpcError as exc:
        raise InputUpdateException(err=f"Inputs {inputs} was not set: {exc}") from None


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
        result = stateClient.GetOne(stateGetReq, timeout=TIMEOUT_REQUEST)
    except RpcError as exc:
        # If the state does not exist for the workspace, reraise the original
        # exception as something went wrong
        if exc.code() != StatusCode.NOT_FOUND:
            raise

        # In the case where the original get req is for the mainline,
        # nothing further we can do
        if stateGetReq.key.workspace_id.value == MAINLINE_WS_ID:
            raise

        # Get the lastRebasedAt timestamp, or if that's null, then the createdAt timestamp
        # of the workspace such that the correct mainline state is retrieved
        wsTs = getWorkspaceLastSynced(apiClientGetter, stateGetReq.key.workspace_id.value)
        # Try again for the mainline state
        stateGetReq.key.workspace_id.value = MAINLINE_WS_ID
        stateGetReq.time = wsTs
        try:
            result = stateClient.GetOne(stateGetReq, timeout=TIMEOUT_REQUEST)
        except RpcError as mainlineExc:
            # Handle the mainline error as its own exception, such that stack
            # traces don't contain nested exceptions such as "when handling the
            # above exception, another exception occurred"
            raise mainlineExc from None

        # Check the config endpoint for the workspace to ensure that
        # the mainline value has not been deleted
        configClient = apiClientGetter(configStub)
        try:
            configResp = configClient.GetOne(confGetReq, timeout=TIMEOUT_REQUEST)
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


def mergeStudioInputs(rootInputs: Any, path: List[Any], inputsToInsert: Any):
    '''
    Due to grpc messaging limits, large inputs may be sent out to get requests
    in chunks, and should be retrieved with a GetAll to ensure all inputs
    for a given studio are received.

    In the case where a studio resource returns inputs in multiple responses, they need to
    be spliced together to form a cohesive input object.

    Params:
    - rootInputs:       The root object to insert the new inputs into
    - path:             The path in the rootInputs to insert the inputs into
    - inputsToInsert:   The inputs to insert into the root inputs

    Returns:
    - The updated root inputs
    '''
    prevElem: Any | None = None
    prev = rootInputs
    currElem = None
    curr = rootInputs

    # Walk down the path from the root to the value at the final element, creating any sub-objects
    # or sub-lists along the way if they don't exist.
    for currElem in path:
        # This element is a list index...
        if currElem.isnumeric():
            # If the current value is not a list, set it to one.
            if not isinstance(curr, list):
                if prevElem is None:
                    rootInputs = []
                    curr = rootInputs
                elif prevElem.isnumeric():
                    prevElemInt = int(prevElem)
                    prev[prevElemInt] = []
                    curr = prev[prevElemInt]
                else:
                    prev[prevElem] = []
                    curr = prev[prevElem]
            # If this index is past the last index of the current list, extend the list until
            # it is big enough for it.
            currElemInt = int(currElem)
            if currElemInt >= len(curr):
                while len(curr) < currElemInt + 1:
                    curr.append(None)
            # Move to the value at the index.
            prevElem = currElem
            prev = curr
            curr = curr[currElemInt]
        # Otherwise this element is an object key...
        else:
            # If the current value is not an object, set it to one.
            if not isinstance(curr, dict):
                if prevElem is None:
                    rootInputs = {}
                    curr = rootInputs
                elif prevElem.isnumeric():
                    prevElemInt = int(prevElem)
                    prev[prevElemInt] = {}
                    curr = prev[prevElemInt]
                else:
                    prev[prevElem] = {}
                    curr = prev[prevElem]
            # If the current value does not contain this
            # key, add it.
            if currElem not in curr:
                curr[currElem] = None
            # Move to the value at the key.
            prevElem = currElem
            prev = curr
            curr = curr[currElem]
    # If the path leads to an object, then merge it with the previous object.
    if isinstance(curr, dict):
        curr.update(inputsToInsert)

    # If it leads to any other type, then  simply set it to the inputsToInsert.
    else:
        if currElem is None:
            rootInputs = inputsToInsert
        elif currElem.isnumeric():
            prev[int(currElem)] = inputsToInsert
        else:
            prev[currElem] = inputsToInsert
    return rootInputs


# The following functions are input validation helpers for autofill scripts.
# Note that while the studio template scripts operate on post build validated inputs,
# the autofill scripts operate on the raw studio inputs.

def get_tag_value_from_resolver(resolver: Dict) -> str:
    """
    Return the value in single-tag resolver
    """
    tags = resolver.get('tags', {}) if resolver and isinstance(resolver, dict) else {}
    return tags.get('query').split(':')[1] if tags.get('query') else ""


def validate_resolver(resolver: Dict) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Validates a resolver entry containing a group.
    Consider no inputs as an invalid (ie. irrelevant) case.
    Return the resolver inputs, tag value if valid, else None, None.
    """
    if (not resolver
       or not isinstance(resolver, dict)
       or not (res_inputs := resolver.get('inputs'))
       or not isinstance(res_inputs, dict)
       or not (res_tag_value := get_tag_value_from_resolver(resolver))):
        return None, None
    return res_inputs, res_tag_value
