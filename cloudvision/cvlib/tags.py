# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from collections.abc import Callable
from typing import Dict, List, Optional

from arista.tag.v2.services import (
    TagAssignmentServiceStub,
    TagAssignmentStreamRequest,
    TagConfigServiceStub,
    TagConfigSetRequest,
    TagAssignmentConfigServiceStub,
    TagAssignmentConfigSetRequest
)
from arista.tag.v2.tag_pb2 import (
    TagAssignment,
    ELEMENT_TYPE_DEVICE,
    CREATOR_TYPE_USER
)


class Tags:
    '''
    Object to store tags data relevant to a studio build context.
    Implemented so only one access is made to retreive tags from the remote tags service.
    Note that a tag is of the form label:value, where the same label may be associated
    with many values.
    Device tags are assigned to devices.
    - ctx:                     Context in which the studio build is run
    - tagLabelFilter:          List of tag labels relevant to the studio build,
                               e.g. ['DC', 'Role', 'NodeId'],
                               if unspecified implies all tags will be available
    - relevantTagAssigns:      Dictionary of relevant tags,
                               of the form map[deviceId]map[label]=[value1,value2,..],
                               works like a cache
    - deviceTagValidationFunc: Used to validate the device tags before returning them,
                               if not set then no validation occurs,
                               if set the function must have parameters of deviceId, deviceTags
    - validatedTagAssigns:     Dictionary of per device validated tags,
                               used if there is a deviceTagValidationFunc set,
                               of the form map[deviceId]map[label]=[value1,value2,..],
                               works like a cache
    An example use in a studio template would be calls as follows:
        studiosTagLabels = ['DC', 'Role', 'NodeId']
        ctx.tags.setFilter(studiosTagLabels)
        ctx.tags.setDeviceTagValidationFunc(deviceTagValidationFunc)
        device_tags = ctx.tags.getDeviceTags(device_id)
        ctx.tags.assignDeviceTagLabel(device_id, "Vtep")
    '''

    def __init__(self,
                 context,
                 tagLabelFilter: Optional[List[str]] = [],
                 deviceTagValidationFunc: Optional[Callable[[str, Dict], Dict]] = None):
        self.ctx = context
        self.tagLabelFilter = tagLabelFilter
        self.relevantTagAssigns: Dict = {}
        self.deviceTagValidationFunc = deviceTagValidationFunc
        self.validatedTagAssigns: Dict = {}

    def getFilter(self):
        '''
        getFilter returns the list of relevant tag labels
        '''
        return self.tagLabelFilter

    def _trimTagsFromLocalCache(self):
        '''
        _trimTagsFromLocalCache removes tags not of interest
        from the cache
        '''
        if not self.tagLabelFilter:
            return
        for device, tags in self.relevantTagAssigns.items():
            for tag in list(tags.keys()):
                if tag not in self.tagLabelFilter:
                    del tags[tag]
                    self.validatedTagAssigns[device] = {}

    def setFilter(self, tagLabels: List[str]):
        '''
        setFilter sets the list of relevant tag labels
        also clears the caches as necessary
        '''
        if self.tagLabelFilter and not tagLabels:
            moreTags = True
        elif self.tagLabelFilter and list(set(tagLabels) - set(self.tagLabelFilter)):
            moreTags = True
        else:
            moreTags = False
        self.tagLabelFilter = tagLabels
        # if we need to get more tags clear the cache and get again from tags resource
        if moreTags:
            self.relevantTagAssigns = {}
            self.validatedTagAssigns = {}
            return
        # if we are removing tags of interest, remove from local cache
        self._trimTagsFromLocalCache()

    def setRelevantTagAssigns(self, tags: Dict):
        '''
        Sets the relevantTagAssigns of the context.
        Called during context initialisation during script execution as optimization
        Does not need to be called by the script writers
        '''
        self.relevantTagAssigns = tags

    def setDeviceTagValidationFunc(self, validationFunc: Callable[[str, Dict], Dict]):
        '''
        setDeviceTagValidationFunc sets the device tag validation function
        also clears the validated cache
        '''
        self.deviceTagValidationFunc = validationFunc
        self.validatedTagAssigns = {}

    def _tagExists(self, label: str, value: str):
        for dev, tags in self.getAllDeviceTags().items():
            if tags.get(label) and value in tags[label]:
                return True
        return False

    def _tagAssigned(self, deviceId: str, label: str, value: str):
        if value in self.getDeviceTags(deviceId).get(label, []):
            return True
        return False

    def _assignDevTagInLocalCaches(self, deviceId: str, label: str, value: str):
        # modify relevantTagAssigns for device tag
        if not self.getDeviceTags(deviceId):
            self.relevantTagAssigns[deviceId] = {}
        if label not in self.relevantTagAssigns[deviceId]:
            self.relevantTagAssigns[deviceId][label] = []
        if value not in self.relevantTagAssigns[deviceId][label]:
            self.relevantTagAssigns[deviceId][label].append(value)
        # repopulate validatedTagAssigns for device tag
        self.validatedTagAssigns.pop(deviceId)
        self.getDeviceTags(deviceId)

    def _unassignDevTagInLocalCaches(self, deviceId: str, label: str, value: str):
        # modify relevantTagAssigns for device tag
        if not self.getDeviceTags(deviceId):
            return
        if label not in self.relevantTagAssigns[deviceId]:
            return
        if value not in self.relevantTagAssigns[deviceId][label]:
            return
        self.relevantTagAssigns[deviceId][label].remove(value)
        if not self.relevantTagAssigns[deviceId][label]:
            self.relevantTagAssigns[deviceId].pop(label)
            if not self.relevantTagAssigns[deviceId]:
                self.relevantTagAssigns.pop(deviceId)
        # repopulate validatedTagAssigns for device tag
        self.validatedTagAssigns.pop(deviceId)
        self.getDeviceTags(deviceId)

    def getDeviceTags(self, deviceId: str):
        '''
        getDeviceTags returns the relevant assigned tags for the device.
        If a validation function was set, then it returns validated tags.
        The returned map is of the form: map[label]=[value1,value2,..]
        '''
        if self.getAllDeviceTags().get(deviceId) and self.deviceTagValidationFunc:
            if not self.validatedTagAssigns.get(deviceId):
                deviceTags = self.deviceTagValidationFunc(
                    deviceId,
                    self.relevantTagAssigns.get(deviceId, {}))
                self.validatedTagAssigns[deviceId] = deviceTags
            else:
                deviceTags = self.validatedTagAssigns.get(deviceId, {})
        else:
            deviceTags = self.relevantTagAssigns.get(deviceId, {})
        return deviceTags

    def getAllDeviceTags(self):
        '''
        getAllDeviceTags Returns a map of all assigned device tags available in the workspace,
        limited to the labels of tagLabelFilter, if set via setFilter.
        The returned map is of the form: map[deviceId]map[label]=[value1,value2,..]
        '''
        if self.relevantTagAssigns:
            return self.relevantTagAssigns
        self.relevantTagAssigns = {}
        tagClient = self.ctx.getApiClient(TagAssignmentServiceStub)
        tagRequest = TagAssignmentStreamRequest()
        tagFilter = TagAssignment()
        tagFilter.tag_creator_type = CREATOR_TYPE_USER
        tagFilter.key.element_type = ELEMENT_TYPE_DEVICE
        tagFilter.key.workspace_id.value = self.ctx.studio.workspaceId
        if not self.tagLabelFilter:
            tagRequest.partial_eq_filter.append(tagFilter)
        else:
            for tag in self.tagLabelFilter:
                tagFilter.key.label.value = tag
                tagRequest.partial_eq_filter.append(tagFilter)
        for resp in tagClient.GetAll(tagRequest):
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

    def createTag(self, etype: int, label: str, value: str):
        '''
        createTag creates a tag if it doesn't already exist
        etype is a tags ElementType
        '''
        # check if the tag exists
        if self._tagExists(label, value):
            return
        # create the tag
        setRequest = TagConfigSetRequest()
        setRequest.value.key.workspace_id.value = self.ctx.studio.workspaceId
        setRequest.value.key.element_type = etype
        setRequest.value.key.label.value = label
        setRequest.value.key.value.value = value
        tagClient = self.ctx.getApiClient(TagConfigServiceStub)
        tagClient.Set(setRequest)

    def assignDeviceTag(self, deviceId: str, label: str, value: str, multiValue: bool = False):
        '''
        assignDeviceTag assigns a device tag if it isn't already assigned,
        enforcing that only one value of the tag is assigned to the device,
        unless the multiValue argument is set to True
        '''
        if not multiValue:
            current_values = list(self.getDeviceTags(deviceId).get(label, []))
            for cvalue in current_values:
                if cvalue != value:
                    self.unassignDeviceTag(deviceId, label, cvalue)
        self.assignDeviceTagMultiValue(deviceId, label, value)

    def assignDeviceTagMultiValue(self, deviceId: str, label: str, value: str):
        '''
        assignDeviceTagMultiValue assigns a device tag if it isn't already assigned
        not enforcing that only one value of the tag is assigned to the device
        '''
        # check if the tag is already assigned to this device
        if self._tagAssigned(deviceId, label, value):
            return
        # create the tag
        self.createTag(ELEMENT_TYPE_DEVICE, label, value)
        # assign the tag
        setRequest = TagAssignmentConfigSetRequest()
        setRequest.value.key.workspace_id.value = self.ctx.studio.workspaceId
        setRequest.value.key.element_type = ELEMENT_TYPE_DEVICE
        setRequest.value.key.label.value = label
        setRequest.value.key.value.value = value
        setRequest.value.key.device_id.value = deviceId
        setRequest.value.remove.value = False
        tagClient = self.ctx.getApiClient(TagAssignmentConfigServiceStub)
        tagClient.Set(setRequest)
        # assign the tag in local cache
        self._assignDevTagInLocalCaches(deviceId, label, value)

    def unassignDeviceTag(self, deviceId: str, label: str, value: str):
        '''
        unassignDeviceTag unassigns a device tag if it is assigned
        '''
        # check if the tag is assigned to this device
        if not self._tagAssigned(deviceId, label, value):
            return
        # unassign the tag
        setRequest = TagAssignmentConfigSetRequest()
        setRequest.value.key.workspace_id.value = self.ctx.studio.workspaceId
        setRequest.value.key.element_type = ELEMENT_TYPE_DEVICE
        setRequest.value.key.label.value = label
        setRequest.value.key.value.value = value
        setRequest.value.key.device_id.value = deviceId
        setRequest.value.remove.value = True
        tagClient = self.ctx.getApiClient(TagAssignmentConfigServiceStub)
        tagClient.Set(setRequest)
        # unassign the tag in local cache
        self._unassignDevTagInLocalCaches(deviceId, label, value)

    def unassignDeviceTagLabel(self, deviceId: str, label: str):
        '''
        unassignDeviceTagLabel unassigns all device tags of a label
        '''
        current_values = list(self.getDeviceTags(deviceId).get(label, []))
        for cvalue in current_values:
            self.unassignDeviceTag(deviceId, label, cvalue)
