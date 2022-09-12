# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from typing import List


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

    def __init__(self, workspaceId: str, studioId: str, inputs, deviceIds, logger, execId, buildId):
        self.workspaceId = workspaceId
        self.studioId = studioId
        self.inputs = inputs
        self.deviceIds = deviceIds
        self.logger = logger
        self.execId = execId
        self.buildId = buildId


class InputError:
    """
    This is the primary error that Studio Template writers would raise.
    It is raised manually by a template script if the set of inputs violates the script-author's
    assumptions.
    - message:      A user-friendly text message of the error
    - inputPath:    The path to the field that is in error. It is a list of field names
                    (the "name" attribute in the schema) starting from the root.
                    E.g.: ["networkConfig", "0", "config", "monitoredHosts", "1"]
    - fieldId:      The unique ID of the field (the "id" attribute in the schema).
    - members:      A list of all members in a group-type input that are in conflict. inputs easily.
                    In most cases, a script will only specify a single member to show that inputA
                    has a problem that the end user needs to fix. In certain cases, though, you may
                    want to indicate to the end user that either inputA or inputB needs fixing, but
                    both can't coexist in their current form.
    """

    def __init__(self, message: str = "Error in input field",
                 inputPath: List[str] = None, fieldId: str = None, members: List[str] = None):
        self.message = message
        self.inputPath = inputPath
        self.fieldId = fieldId
        self.members = members

    def __str__(self):
        return (
            f"{{"
            f"message: '{self.message}', "
            f"inputPath: {self.inputPath}, "
            f"fieldId: '{self.fieldId}', "
            f"members: {self.members}"
            f"}}"
        )
