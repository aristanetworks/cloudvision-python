# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from grpc import RpcError
from typing import Dict, List, Tuple

from arista.tag.v2.services import (
    TagAssignmentServiceStub,
    TagAssignmentStreamRequest,
    TagConfigServiceStub,
    TagConfigSetRequest,
    TagConfigSetSomeRequest,
    TagAssignmentConfigStreamRequest,
    TagAssignmentConfigServiceStub,
    TagAssignmentConfigSetRequest,
    TagAssignmentConfigSetSomeRequest
)
from arista.tag.v2.tag_pb2 import (
    TagAssignment,
    TagAssignmentConfig,
    TagConfig,
    ElementType,
    ELEMENT_TYPE_DEVICE,
    ELEMENT_TYPE_INTERFACE,
    CREATOR_TYPE_USER,
)
from arista.time.time_pb2 import TimeBounds
from .constants import (
    TIMEOUT_REQUEST,
    MAINLINE_WS_ID,
)
from .exceptions import (
    TagOperationException
)
from .workspace import (
    getWorkspaceLastSynced
)


class Tag:
    '''
    Object that represents a tag
    '''

    def __init__(self, label: str, value: str):
        self._label = label if label else ''
        self._value = value if value else ''

    @property
    def value(self):
        return self._value

    @property
    def label(self):
        return self._label

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __lt__(self, other):
        if self.label != other.label:
            return self.label < other.label
        else:
            return self.value < other.value


class Tags:
    '''
    Object to store tags data relevant to a studio build context.
    Note, this class and the methods in context and device classes which use it,
    are meant to be used from studio workspace builds and will operate on
    tags within workspaces using the workspace and studio in the context.
    Implemented so only one access is made to retreive tags from the remote tags service.
    (two accesses until the tags service provided merged mainline-workspace state apis)
    Note that a tag is of the form label:value, where the same label may be associated
    with many values.
    Device tags are assigned to devices.
    Interface tags are assigned to devices' interfaces.
    - ctx:                     Context in which the studio build is run
    - relevantTagAssigns:      Dictionary of relevant device tags, of the form:
                               {deviceId: {label: [value1,value2,..]}},
                               works like a cache
    - relevantIntfTagAssigns:  Dictionary of relevant interface tags, of the form:
                               {deviceId: {intfId: {label: [value1,value2,..]}}},
                               works like a cache
    '''

    def __init__(self, context):
        self.ctx = context
        self.relevantTagAssigns: Dict = None
        self.relevantIntfTagAssigns: Dict = None

    def _getTagUpdatesFromWorkspace(self, etype=ELEMENT_TYPE_DEVICE):
        '''
        _getTagUpdatesFromWorkspace returns a list of tags updates,
        of the specified ElementType, in the workspace.
        The returned list is of the form:
            list[(deviceId, interfaceId, label, value, remove)]
        '''
        workspaceTagUpdates = []
        tagClient = self.ctx.getApiClient(TagAssignmentConfigServiceStub)
        tagRequest = TagAssignmentConfigStreamRequest()
        tagFilter = TagAssignmentConfig()
        tagFilter.key.element_type = etype
        tagFilter.key.workspace_id.value = self.ctx.getWorkspaceId()
        tagRequest.partial_eq_filter.append(tagFilter)
        for resp in tagClient.GetAll(tagRequest, timeout=TIMEOUT_REQUEST):
            workspaceTagUpdates.append((resp.value.key.device_id.value,
                                        resp.value.key.interface_id.value,
                                        resp.value.key.label.value,
                                        resp.value.key.value.value,
                                        resp.value.remove.value))
        return workspaceTagUpdates

    def _createTag(self, etype: int, label: str, value: str):
        '''
        _createTag creates a tag if it doesn't already exist,
        of the specified ElementType, in the workspace.
        '''
        if not label or not value:
            raise TagOperationException(label, value, 'create')
        # check if the tag exists
        if etype == ELEMENT_TYPE_DEVICE and self._deviceTagExists(label, value):
            return
        if etype == ELEMENT_TYPE_INTERFACE and self._interfaceTagExists(label, value):
            return
        # create the tag
        setRequest = TagConfigSetRequest()
        wsID = self.ctx.getWorkspaceId()
        setRequest.value.key.workspace_id.value = wsID
        # Mypy complains about this not being an int, with
        # (expression has type "int", variable has type "ValueType")
        # but ValueType = typing.NewType('ValueType', builtins.int), so just ignore it
        setRequest.value.key.element_type = etype  # type: ignore
        setRequest.value.key.label.value = label
        setRequest.value.key.value.value = value
        tagClient = self.ctx.getApiClient(TagConfigServiceStub)
        tagClient.Set(setRequest, timeout=TIMEOUT_REQUEST)

    def _createTags(self, etype: int, tags: List[Tuple], configsPerReq=1000):
        '''
        _createTags creates multiple tags if they don't already exist,
        of the specified ElementType, in the workspace.
        The input tags is a List of Tuples of (label, value)
        '''
        # remove from the list if the tag already exists
        for (label, value) in tags[:]:
            if not label or not value:
                raise TagOperationException(label, value, 'create')
            if etype == ELEMENT_TYPE_DEVICE and self._deviceTagExists(label, value):
                tags.remove((label, value))
            if etype == ELEMENT_TYPE_INTERFACE and self._interfaceTagExists(label, value):
                tags.remove((label, value))
        if not tags:
            return
        # create the tags
        tagConfigs = []
        wsID = self.ctx.getWorkspaceId()
        for (label, value) in tags:
            tagConfig = TagConfig()
            tagConfig.key.workspace_id.value = wsID
            # Mypy complains about this not being an int, with
            # (expression has type "int", variable has type "ValueType")
            # but ValueType = typing.NewType('ValueType', builtins.int), so just ignore it
            tagConfig.key.element_type = etype  # type: ignore
            tagConfig.key.label.value = label
            tagConfig.key.value.value = value
            tagConfigs.append(tagConfig)
        res = []
        # chunk each SetSome request to a maximum of configsPerReq
        for start in range(0, len(tagConfigs), configsPerReq):
            setSomeRequest = TagConfigSetSomeRequest(
                values=tagConfigs[start:start + configsPerReq]
            )
            tagClient = self.ctx.getApiClient(TagConfigServiceStub)
            try:
                for res in tagClient.SetSome(setSomeRequest, timeout=TIMEOUT_REQUEST):
                    pass
            except RpcError:
                raise TagOperationException('', '', 'create')

    def _assignTagSet(self, etype: int, tagAssign: Tuple, remove: bool = False):
        '''
        _assignTagSet assigns a tag.
        The input tagAssign is a tuple of the form:
            (deviceId, interfaceId, label, value)
        If remove is True, then unassigns the tag.
        '''
        (deviceId, interfaceId, label, value) = tagAssign
        setRequest = TagAssignmentConfigSetRequest()
        wsID = self.ctx.getWorkspaceId()
        setRequest.value.key.workspace_id.value = wsID
        # Mypy complains about this not being an int, with
        # (expression has type "int", variable has type "ValueType")
        # but ValueType = typing.NewType('ValueType', builtins.int), so just ignore it
        setRequest.value.key.element_type = etype  # type: ignore
        setRequest.value.key.label.value = label
        setRequest.value.key.value.value = value
        setRequest.value.key.device_id.value = deviceId
        setRequest.value.key.interface_id.value = interfaceId
        setRequest.value.remove.value = remove
        tagClient = self.ctx.getApiClient(TagAssignmentConfigServiceStub)
        tagClient.Set(setRequest, timeout=TIMEOUT_REQUEST)

    def _assignTagsSets(self, etype: int, tagAssigns: List[Tuple],
                        remove: bool = False, configsPerReq: int = 1000):
        '''
        _assignTagsSets assigns/unassigns multiple tags.
        The input tagAssigns is a List of Tuples of the form:
            (deviceId, interfaceId, label, value)
        If remove is True, then unassigns the tags.
        '''
        tagAssConfigs = []
        wsID = self.ctx.getWorkspaceId()
        for (deviceId, interfaceId, label, value) in tagAssigns:
            tagAssConfig = TagAssignmentConfig()
            tagAssConfig.key.workspace_id.value = wsID
            # Mypy complains about this not being an int, with
            # (expression has type "int", variable has type "ValueType")
            # but ValueType = typing.NewType('ValueType', builtins.int), so just ignore it
            tagAssConfig.key.element_type = etype  # type: ignore
            tagAssConfig.key.label.value = label
            tagAssConfig.key.value.value = value
            tagAssConfig.key.device_id.value = deviceId
            tagAssConfig.key.interface_id.value = interfaceId
            tagAssConfig.remove.value = remove
            tagAssConfigs.append(tagAssConfig)
        res = []
        # chunk each SetSome request to a maximum of configsPerReq
        for start in range(0, len(tagAssConfigs), configsPerReq):
            setSomeRequest = TagAssignmentConfigSetSomeRequest(
                values=tagAssConfigs[start:start + configsPerReq]
            )
            tagClient = self.ctx.getApiClient(TagAssignmentConfigServiceStub)
            try:
                for res in tagClient.SetSome(setSomeRequest, timeout=TIMEOUT_REQUEST):
                    pass
            except RpcError:
                raise TagOperationException('', '', 'assign')

    # The following are methods for device Tags

    def _deviceTagExists(self, label: str, value: str):
        # Note use list instead of .items()
        # parallel thread might add/delete tags
        for dev in list(allTags := self._getAllDeviceTags()):
            tags = allTags.get(dev, {})
            if value in tags.get(label, []):
                return True
        return False

    def _deviceTagAssigned(self, deviceId: str, label: str, value: str):
        if value in self._getDeviceTags(deviceId).get(label, []):
            return True
        return False

    def _assignDevTagInCache(self, deviceId: str, label: str, value: str):
        '''
        _assignDevTagInCache modifies relevantTagAssigns for the device tag
        ensuring the tag is assigned to the device in the local cache
        '''
        if deviceId not in self.relevantTagAssigns:
            self.relevantTagAssigns[deviceId] = {}
        if label not in self.relevantTagAssigns[deviceId]:
            self.relevantTagAssigns[deviceId][label] = []
        if value not in self.relevantTagAssigns[deviceId][label]:
            self.relevantTagAssigns[deviceId][label].append(value)

    def _unassignDevTagInCache(self, deviceId: str, label: str, value: str):
        '''
        _unassignDevTagInCache modifies relevantTagAssigns for the device tag
        ensuring the tag is not assigned to the device in the local cache
        '''
        if deviceId not in self.relevantTagAssigns:
            return
        if label not in self.relevantTagAssigns[deviceId]:
            return
        if value not in self.relevantTagAssigns[deviceId][label]:
            return
        self.relevantTagAssigns[deviceId][label].remove(value)
        if not self.relevantTagAssigns[deviceId][label]:
            self.relevantTagAssigns[deviceId].pop(label, None)
            if not self.relevantTagAssigns[deviceId]:
                self.relevantTagAssigns.pop(deviceId, None)

    def _getAllDeviceTagsFromMainline(self):
        '''
        _getAllDeviceTagsFromMainline returns a map of all assigned device tags available
        in the mainline.  Also sets the local cache to this map.
        The returned map is of the form: map[deviceId]map[label]=[value1,value2,..]
        '''
        wsTs = getWorkspaceLastSynced(self.ctx.getApiClient,
                                      self.ctx.getWorkspaceId())
        timeBound = TimeBounds(end=wsTs)
        self.relevantTagAssigns = {}
        tagClient = self.ctx.getApiClient(TagAssignmentServiceStub)
        tagRequest = TagAssignmentStreamRequest(time=timeBound)
        tagFilter = TagAssignment()
        tagFilter.tag_creator_type = CREATOR_TYPE_USER
        tagFilter.key.element_type = ELEMENT_TYPE_DEVICE
        tagFilter.key.workspace_id.value = MAINLINE_WS_ID
        tagRequest.partial_eq_filter.append(tagFilter)
        for resp in tagClient.GetAll(tagRequest, timeout=TIMEOUT_REQUEST):
            label = resp.value.key.label.value
            value = resp.value.key.value.value
            deviceId = resp.value.key.device_id.value
            if deviceId not in self.relevantTagAssigns:
                self.relevantTagAssigns[deviceId] = {}
            if label not in self.relevantTagAssigns[deviceId]:
                self.relevantTagAssigns[deviceId][label] = []
            if value not in self.relevantTagAssigns[deviceId][label]:
                self.relevantTagAssigns[deviceId][label].append(value)
        return self.relevantTagAssigns

    def _setRelevantTagAssigns(self, tags: Dict):
        '''
        Sets the relevantTagAssigns of the context.
        Called during context initialisation during script execution as optimization
        Does not need to be called by the script writers
        '''
        self.relevantTagAssigns = tags

    def _getDeviceTags(self, deviceId: str):
        '''
        _getDeviceTags returns the relevant assigned tags for the device.
        The returned map is of the form: map[label]=[value1,value2,..]
        '''
        return self._getAllDeviceTags().get(deviceId, {})

    def _getAllDeviceTags(self):
        '''
        _getAllDeviceTags returns a map of all assigned device tags available
        in the workspace.
        The returned map is of the form: map[deviceId]map[label]=[value1,value2,..]
        '''
        if self.relevantTagAssigns is not None:
            return self.relevantTagAssigns
        self._getAllDeviceTagsFromMainline()
        workspaceUpdates = self._getTagUpdatesFromWorkspace()
        for (deviceId, _, label, value, remove) in workspaceUpdates:
            if remove:
                self._unassignDevTagInCache(deviceId, label, value)
            else:
                self._assignDevTagInCache(deviceId, label, value)
        return self.relevantTagAssigns

    def _assignDeviceTag(self, deviceId: str, label: str, value: str,
                         replaceValue: bool = True):
        '''
        _assignDeviceTag assigns a device tag if it isn't already assigned.
        If replaceValue is True ensures one value of tag is assigned to device.
        If replaceValue is False multiple values of tag can be assigned to device.
        '''
        # first make sure this device's tags have been loaded in cache
        self._getDeviceTags(deviceId)
        # identify unassigns for replace cases
        if not label or not value or not deviceId:
            raise TagOperationException(label, value, 'assign', deviceId)
        if replaceValue:
            current_values = list(self._getDeviceTags(deviceId).get(label, []))
            for cvalue in current_values:
                if cvalue != value:
                    self._unassignDeviceTag(deviceId, label, cvalue)
        # check if the tag is already assigned to this device
        if self._deviceTagAssigned(deviceId, label, value):
            return
        # create the tag
        self._createTag(ELEMENT_TYPE_DEVICE, label, value)
        # assign the tag
        self._assignTagSet(ELEMENT_TYPE_DEVICE, (deviceId, '', label, value))
        # assign the tag in cache
        self._assignDevTagInCache(deviceId, label, value)

    def _unassignDeviceTag(self, deviceId: str, label: str, value: str):
        '''
        _unassignDeviceTag unassigns a device tag if it is assigned
        '''
        # first make sure this device's tags have been loaded in cache
        self._getDeviceTags(deviceId)
        if not label or not value or not deviceId:
            raise TagOperationException(label, value, 'unassign', deviceId)
        # check if the tag is assigned to this device
        if not self._deviceTagAssigned(deviceId, label, value):
            return
        # unassign the tag
        self._assignTagSet(ELEMENT_TYPE_DEVICE,
                           (deviceId, '', label, value), remove=True)
        # unassign the tag in cache
        self._unassignDevTagInCache(deviceId, label, value)

    def _unassignDeviceTagLabel(self, deviceId: str, label: str):
        '''
        _unassignDeviceTagLabel unassigns all device tags of a label
        '''
        if not label or not deviceId:
            raise TagOperationException(label, '', 'unassign', deviceId)
        current_values = list(self._getDeviceTags(deviceId).get(label, []))
        for cvalue in current_values:
            self._unassignDeviceTag(deviceId, label, cvalue)

    def _assignDeviceTags(self, tagAssignReplaces: List[Tuple]):
        '''
        _assignDeviceTags assigns multiple device tags if not already assigned.
        The input tagAssignReplaces is a List of Tuple of the form:
            (deviceId, label, value, replaceValue)
        If replaceValue is True ensures one value of tag is assigned to device.
        If replaceValue is False multiple values of tag can be assigned to device.
        '''
        if not tagAssignReplaces:
            return
        tagUnAssigns: List[Tuple] = []
        tagAssigns: List[Tuple] = []
        tagAssignsDict: Dict = {}
        # first make sure device tags have been loaded in cache
        self._getAllDeviceTags()
        # identify unassigns for replace cases
        for (deviceId, label, value, replaceValue) in tagAssignReplaces:
            if not label or not value or not deviceId:
                raise TagOperationException(label, value, 'assign', deviceId)
            if replaceValue:
                current_values = list(self._getDeviceTags(deviceId).get(label, []))
                for cvalue in current_values:
                    if cvalue != value:
                        tagUnAssigns.append((deviceId, label, cvalue))
                if (cvalues := tagAssignsDict.get(deviceId, {}).get(label)):
                    for cvalue in cvalues:
                        tagAssigns.remove((deviceId, '', label, cvalue))
                    tagAssignsDict[deviceId].pop(label)
            tagAssignsDict.setdefault(deviceId, {}).setdefault(label, []).append(value)
            tagAssigns.append((deviceId, '', label, value))
        self._unassignDeviceTags(tagUnAssigns)
        # remove from the list if the tag assignmnet already exists
        uniqueTags: List[Tuple] = []
        for (deviceId, _, label, value) in tagAssigns[:]:
            if self._deviceTagAssigned(deviceId, label, value):
                tagAssigns.remove((deviceId, '', label, value))
            elif (label, value) not in uniqueTags:
                uniqueTags.append((label, value))
        if not tagAssigns:
            return
        # create the tags
        self._createTags(ELEMENT_TYPE_DEVICE, uniqueTags)
        # assign the tags
        self._assignTagsSets(ELEMENT_TYPE_DEVICE, tagAssigns)
        # assign the tags in cache
        for (deviceId, _, label, value) in tagAssigns:
            self._assignDevTagInCache(deviceId, label, value)

    def _unassignDeviceTags(self, tagUnAssignsIn: List[Tuple]):
        '''
        _unassignDeviceTags unassigns multiple device tags if currently assigned.
        The input tagUnAssigns is a List of Tuples of the form:
            (deviceId, label, value)
        If value is None then unassigns all values of that label
        '''
        if not tagUnAssignsIn:
            return
        # first make sure device tags have been loaded in cache
        self._getAllDeviceTags()
        tagUnAssigns: List[Tuple] = []
        # remove from the list if the tag assignment doesn't exist
        for (deviceId, label, value) in tagUnAssignsIn:
            if not label or not deviceId:
                raise TagOperationException(label, '', 'unassign', deviceId)
            # check if the tag is assigned to this device
            if not value:
                current_values = list(self._getDeviceTags(deviceId).get(label, []))
                for cvalue in current_values:
                    tagUnAssigns.append((deviceId, '', label, cvalue))
            elif self._deviceTagAssigned(deviceId, label, value):
                tagUnAssigns.append((deviceId, '', label, value))
        if not tagUnAssigns:
            return
        # unassign the tags
        self._assignTagsSets(ELEMENT_TYPE_DEVICE, tagUnAssigns, remove=True)
        # unassign the tags in cache
        for (deviceId, _, label, value) in tagUnAssigns:
            self._unassignDevTagInCache(deviceId, label, value)

    # The following are methods for interface Tags

    def _interfaceTagExists(self, label: str, value: str):
        # Note use list instead of .items()
        # parallel thread might add/delete tags
        for dev in list(allTags := self._getAllInterfaceTags()):
            for intf in list(devIntfTags := allTags.get(dev, {})):
                tags = devIntfTags.get(intf, {})
                if value in tags.get(label, []):
                    return True
        return False

    def _interfaceTagAssigned(self, deviceId: str, interfaceId: str, label: str, value: str):
        if value in self._getInterfaceTags(deviceId, interfaceId).get(label, []):
            return True
        return False

    def _assignIntfTagInCache(self, deviceId: str, interfaceId: str, label: str, value: str):
        '''
        _assignIntfTagInCache modifies relevantIntfAssigns for the device tag
        ensuring the tag is assigned to the interface in the local cache
        '''
        if deviceId not in self.relevantIntfTagAssigns:
            self.relevantIntfTagAssigns[deviceId] = {}
        if interfaceId not in self.relevantIntfTagAssigns[deviceId]:
            self.relevantIntfTagAssigns[deviceId][interfaceId] = {}
        if label not in self.relevantIntfTagAssigns[deviceId][interfaceId]:
            self.relevantIntfTagAssigns[deviceId][interfaceId][label] = []
        if value not in self.relevantIntfTagAssigns[deviceId][interfaceId][label]:
            self.relevantIntfTagAssigns[deviceId][interfaceId][label].append(value)

    def _unassignIntfTagInCache(self, deviceId: str, interfaceId: str, label: str, value: str):
        '''
        _unassignIntfTagInCache modifies relevantIntfTagAssigns for the interface tag
        ensuring the tag is not assigned to the interface in the local cache
        '''
        if deviceId not in self.relevantIntfTagAssigns:
            return
        if interfaceId not in self.relevantIntfTagAssigns[deviceId]:
            return
        if label not in self.relevantIntfTagAssigns[deviceId][interfaceId]:
            return
        if value not in self.relevantIntfTagAssigns[deviceId][interfaceId][label]:
            return
        self.relevantIntfTagAssigns[deviceId][interfaceId][label].remove(value)
        if not self.relevantIntfTagAssigns[deviceId][interfaceId][label]:
            self.relevantIntfTagAssigns[deviceId][interfaceId].pop(label, None)
            if not self.relevantIntfTagAssigns[deviceId][interfaceId]:
                self.relevantIntfTagAssigns[deviceId].pop(interfaceId, None)
                if not self.relevantIntfTagAssigns[deviceId]:
                    self.relevantIntfTagAssigns.pop(deviceId, None)

    def _getAllInterfaceTagsFromMainline(self):
        '''
        _getAllInterfaceTagsFromMainline returns a map of all assigned interface tags
        available in the mainline.  Also sets the local cache to this map.
        The returned map is of the form:
            map[deviceId]map[interfaceId]map[label]=[value1,value2,..]
        '''
        wsTs = getWorkspaceLastSynced(self.ctx.getApiClient,
                                      self.ctx.getWorkspaceId())
        timeBound = TimeBounds(end=wsTs)
        self.relevantIntfTagAssigns = {}
        tagClient = self.ctx.getApiClient(TagAssignmentServiceStub)
        tagRequest = TagAssignmentStreamRequest(time=timeBound)
        tagFilter = TagAssignment()
        tagFilter.tag_creator_type = CREATOR_TYPE_USER
        tagFilter.key.element_type = ELEMENT_TYPE_INTERFACE
        tagFilter.key.workspace_id.value = MAINLINE_WS_ID
        tagRequest.partial_eq_filter.append(tagFilter)
        for resp in tagClient.GetAll(tagRequest, timeout=TIMEOUT_REQUEST):
            label = resp.value.key.label.value
            value = resp.value.key.value.value
            deviceId = resp.value.key.device_id.value
            interfaceId = resp.value.key.interface_id.value
            if deviceId not in self.relevantIntfTagAssigns:
                self.relevantIntfTagAssigns[deviceId] = {}
            if interfaceId not in self.relevantIntfTagAssigns[deviceId]:
                self.relevantIntfTagAssigns[deviceId][interfaceId] = {}
            if label not in self.relevantIntfTagAssigns[deviceId][interfaceId]:
                self.relevantIntfTagAssigns[deviceId][interfaceId][label] = []
            if value not in self.relevantIntfTagAssigns[deviceId][interfaceId][label]:
                self.relevantIntfTagAssigns[deviceId][interfaceId][label].append(value)
        return self.relevantIntfTagAssigns

    def _setRelevantInterfaceTagAssigns(self, tags: Dict):
        '''
        Sets the relevantIntfTagAssigns of the context.
        Called during context initialisation during script execution as optimization
        Does not need to be called by the script writers
        '''
        self.relevantIntfTagAssigns = tags

    def _getInterfaceTags(self, deviceId: str, interfaceId: str):
        '''
        _getInterfaceTags returns the relevant assigned tags for the interface.
        The returned map is of the form: map[label]=[value1,value2,..]
        '''
        return self._getAllInterfaceTags().get(deviceId, {}).get(interfaceId, {})

    def _getAllInterfaceTags(self):
        '''
        _getAllInterfaceTags returns a map of all assigned device tags available
        in the workspace.  The returned map is of the form:
            map[deviceId]map[interfaceId]map[label]=[value1,value2,..]
        '''
        if self.relevantIntfTagAssigns is not None:
            return self.relevantIntfTagAssigns
        self._getAllInterfaceTagsFromMainline()
        workspaceUpdates = self._getTagUpdatesFromWorkspace(ELEMENT_TYPE_INTERFACE)
        for (deviceId, interfaceId, label, value, remove) in workspaceUpdates:
            if remove:
                self._unassignIntfTagInCache(deviceId, interfaceId, label, value)
            else:
                self._assignIntfTagInCache(deviceId, interfaceId, label, value)
        return self.relevantIntfTagAssigns

    def _assignInterfaceTag(self, deviceId: str, interfaceId: str, label: str,
                            value: str, replaceValue: bool = True):
        '''
        _assignInterfaceTag assigns aninterface tag if it isn't already assigned.
        If replaceValue is True ensures one value of tag is assigned to interface.
        If replaceValue is False multiple values of tag can be assigned to interface.
        '''
        # first make sure this device's tags have been loaded in cache
        self._getInterfaceTags(deviceId, interfaceId)
        if not label or not value or not deviceId or not interfaceId:
            raise TagOperationException(label, value, 'assign', deviceId, interfaceId)
        if replaceValue:
            current_values = list(self._getInterfaceTags(deviceId, interfaceId).get(label, []))
            for cvalue in current_values:
                if cvalue != value:
                    self._unassignInterfaceTag(deviceId, interfaceId, label, cvalue)
        # check if the tag is already assigned to this device
        if self._interfaceTagAssigned(deviceId, interfaceId, label, value):
            return
        # create the tag
        self._createTag(ELEMENT_TYPE_INTERFACE, label, value)
        # assign the tag
        self._assignTagSet(ELEMENT_TYPE_INTERFACE,
                           (deviceId, interfaceId, label, value))
        # assign the tag in cache
        self._assignIntfTagInCache(deviceId, interfaceId, label, value)

    def _unassignInterfaceTag(self, deviceId: str, interfaceId: str, label: str, value: str):
        '''
        _unassignInterfaceTag unassigns a interface tag if it is assigned
        '''
        # first make sure this device's tags have been loaded in cache
        self._getInterfaceTags(deviceId, interfaceId)
        if not label or not value or not deviceId or not interfaceId:
            raise TagOperationException(label, value, 'unassign', deviceId, interfaceId)
        # check if the tag is assigned to this interface
        if not self._interfaceTagAssigned(deviceId, interfaceId, label, value):
            return
        # unassign the tag
        self._assignTagSet(ELEMENT_TYPE_INTERFACE,
                           (deviceId, interfaceId, label, value), remove=True)
        # unassign the tag in cache
        self._unassignIntfTagInCache(deviceId, interfaceId, label, value)

    def _unassignInterfaceTagLabel(self, deviceId: str, interfaceId: str, label: str):
        '''
        _unassignInterfaceTagLabel unassigns all interface tags of a label
        '''
        if not label or not deviceId or not interfaceId:
            raise TagOperationException(label, '', 'unassign', deviceId, interfaceId)
        current_values = list(self._getInterfaceTags(deviceId, interfaceId).get(label, []))
        for cvalue in current_values:
            self._unassignInterfaceTag(deviceId, interfaceId, label, cvalue)

    def _assignInterfaceTags(self, tagAssignReplaces: List[Tuple]):
        '''
        _assignInterfaceTags assigns multiple interface tags if not already assigned.
        The input tagAssignReplaces is a List of Tuple of the form:
            (deviceId, interfaceId, label, value, replaceValue)
        If replaceValue is True ensures one value of tag is assigned to interface.
        If replaceValue is False multiple values of tag can be assigned to interface.
        '''
        if not tagAssignReplaces:
            return
        tagUnAssigns: List[Tuple] = []
        tagAssigns: List[Tuple] = []
        tagAssignsDict: Dict = {}
        # first make sure interface tags have been loaded in cache
        self._getAllInterfaceTags()
        # identify unassigns for replace cases
        for (deviceId, interfaceId, label, value, replaceValue) in tagAssignReplaces:
            if not label or not value or not deviceId or not interfaceId:
                raise TagOperationException(label, value, 'assign',
                                            deviceId, interfaceId)
            if replaceValue:
                current_values = list(self._getInterfaceTags(deviceId,
                                      interfaceId).get(label, []))
                for cvalue in current_values:
                    if cvalue != value:
                        tagUnAssigns.append((deviceId, interfaceId, label, cvalue))
                if (cvalues := tagAssignsDict.get(deviceId, {}).get(
                        interfaceId, {}).get(label)):
                    for cvalue in cvalues:
                        tagAssigns.remove((deviceId, interfaceId, label, cvalue))
                    tagAssignsDict[deviceId][interfaceId].pop(label)
            tagAssignsDict.setdefault(deviceId, {}).setdefault(
                interfaceId, {}).setdefault(label, []).append(value)
            tagAssigns.append((deviceId, interfaceId, label, value))
        self._unassignInterfaceTags(tagUnAssigns)
        # remove from the list if the tag assignmnet already exists
        uniqueTags: List[Tuple] = []
        for (deviceId, interfaceId, label, value) in tagAssigns[:]:
            if self._interfaceTagAssigned(deviceId, interfaceId, label, value):
                tagAssigns.remove((deviceId, interfaceId, label, value))
            elif (label, value) not in uniqueTags:
                uniqueTags.append((label, value))
        if not tagAssigns:
            return
        # create the tags
        self._createTags(ELEMENT_TYPE_INTERFACE, uniqueTags)
        # assign the tags
        self._assignTagsSets(ELEMENT_TYPE_INTERFACE, tagAssigns)
        # assign the tags in cache
        for (deviceId, interfaceId, label, value) in tagAssigns:
            self._assignIntfTagInCache(deviceId, interfaceId, label, value)

    def _unassignInterfaceTags(self, tagUnAssignsIn: List[Tuple]):
        '''
        _unassignInterfaceTags unassigns multiple interface tags if currently assigned.
        The input tagUnAssigns is a List of Tuples of the form:
            (deviceId, interfaceId, label, value)
        If value is None then unassigns all values of that label
        '''
        if not tagUnAssignsIn:
            return
        # first make sure interface tags have been loaded in cache
        self._getAllInterfaceTags()
        tagUnAssigns: List[Tuple] = []
        # remove from the list if the tag assignment doesn't exist
        for (deviceId, interfaceId, label, value) in tagUnAssignsIn:
            if not label or not deviceId or not interfaceId:
                raise TagOperationException(label, '', 'unassign',
                                            deviceId, interfaceId)
            # check if the tag is assigned to this interface
            if not value:
                current_values = list(self._getInterfaceTags(deviceId,
                                      interfaceId).get(label, []))
                for cvalue in current_values:
                    tagUnAssigns.append((deviceId, interfaceId, label, cvalue))
            elif self._interfaceTagAssigned(deviceId, interfaceId, label, value):
                tagUnAssigns.append((deviceId, interfaceId, label, value))
        if not tagUnAssigns:
            return
        # unassign the tags
        self._assignTagsSets(ELEMENT_TYPE_INTERFACE, tagUnAssigns, remove=True)
        # unassign the tags in cache
        for (deviceId, interfaceId, label, value) in tagUnAssigns:
            self._unassignIntfTagInCache(deviceId, interfaceId, label, value)
