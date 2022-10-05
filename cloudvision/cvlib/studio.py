# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from typing import Dict, List
import json
from fmp import wrappers_pb2 as fmp_wrappers
import google.protobuf.wrappers_pb2 as pb
from arista.studio.v1 import models, services

from .exceptions import InputNotFoundException, InputRequestException, InputUpdateException


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


def extractInputElems(inputs, inputPath: List[str], elems: List[str] = [], tagElems: List[str] = []):
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
        # Ensure sane value
        if currInput is None:
            raise InputNotFoundException(inputPath)

    return results


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
    studioId = args.get("StudioID")
    workspaceId = args.get("WorkspaceID")
    inputPath = None
    inputPathArg = args.get("InputPath")  # This is a stringified list
    if inputPathArg:
        inputPath = json.loads(inputPathArg)  # Evaluate this into a list
        if not isinstance(inputPath, list):
            raise ValueError("Studio input path must be a list of strings")
    return studioId, workspaceId, inputPath
