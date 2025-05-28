# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from typing import Dict, List, Optional

from .exceptions import (
    TagMissingException,
    TagTooManyValuesException
)
from .tags import Tag


OLD_VEOS_REGEX = r'(v|c)EOS(-)*(Lab)*'
NEW_VEOS_REGEX = r'CloudEOS(-)*(Lab)*'
veos_regex = f"({OLD_VEOS_REGEX})|({NEW_VEOS_REGEX})"
device_capabilities: Dict[str, Dict] = {
    "jericho-fixed-7048T": {
        "regexes": [r'DCS-7048T'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 900,
            "non_mlag": 1020
        },
    },
    "jericho-fixed": {
        "regexes": [r'DCS-7280\w(R|R2)\D*-.+', r'DCS-7020\w(R|RW)\D*-.+'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 900,
            "non_mlag": 1020
        },
        "tcam_profile": "vxlan-routing",
        "full_packet_mirroring": True,
    },
    "jericho-chassis": {
        "regexes": [r'DCS-75\d\d'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 900,
            "non_mlag": 1020
        },
        "tcam_profile": "vxlan-routing",
        "management_interface": "Management0",
        "full_packet_mirroring": True,
    },
    "jericho2-fixed": {
        "regexes": [r'DCS-7280\w(R3)\D*-.+'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 900,
            "non_mlag": 1020
        },
        "tcam_profile": "vxlan-routing",
        "full_packet_mirroring": True,
    },
    "jericho2-chassis": {
        "regexes": [r'DCS-78\d\d'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 900,
            "non_mlag": 1020
        },
        "tcam_profile": "vxlan-routing",
        "full_packet_mirroring": True,
    },
    "trident2-fixed": {
        "regexes": [r'DCS-7050(S|T)X-\d\d'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 300,
            "non_mlag": 330
        },
        "tcam_profile": None,
        "feature_support": {
            "queue_monitor_length_notify": False,
            "phone": True,
        },
        "ip_locking": {
            "support": True
        },
    },
    "trident3x1-fixed-poe": {
        "regexes": [r'CCS-720DP-24S', r'CCS-710P'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 300,
            "non_mlag": 330
        },
        "tcam_profile": None,
        "feature_support": {
            "queue_monitor_length_notify": False,
            "phone": True,
            "poe": True,
        },
        "ip_locking": {
            "support": True
        },
        "per_interface_mtu": False,
    },
    "trident3x1-fixed": {
        "regexes": [r'CCS-720DT-24'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 300,
            "non_mlag": 330
        },
        "tcam_profile": None,
        "feature_support": {
            "queue_monitor_length_notify": False,
            "phone": True,
            "poe": False,
        },
        "ip_locking": {
            "support": True
        },
        "per_interface_mtu": False,
    },
    "trident3x2-fixed-poe": {
        "regexes": [r'CCS-720DP-48S', r'CCS-722XP'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 300,
            "non_mlag": 330
        },
        "tcam_profile": None,
        "feature_support": {
            "queue_monitor_length_notify": False,
            "phone": True,
            "poe": True,
        },
        "ip_locking": {
            "support": True
        },
        "per_interface_mtu": False,
    },
    "trident3x2-fixed": {
        "regexes": [r'CCS-720DT-48', r'DCS-7010TX'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 300,
            "non_mlag": 330
        },
        "tcam_profile": None,
        "feature_support": {
            "queue_monitor_length_notify": False,
            "phone": True,
        },
        "ip_locking": {
            "support": True
        },
        "per_interface_mtu": False,
    },
    "trident3x3-fixed-poe": {
        "regexes": [r'CCS-720XP-\d\d', r'CCS-720DP-\d\dZS'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 300,
            "non_mlag": 330
        },
        "tcam_profile": None,
        "trident_forwarding_table_partition": (
            "flexible exact-match 16000 "
            "l2-shared 18000 l3-shared 22000"),
        "feature_support": {
            "queue_monitor_length_notify": False,
            "phone": True,
            "poe": True,
        },
        "ip_locking": {
            "support": True
        },
    },
    "trident3x3-fixed": {
        "regexes": [r'CCS-720DF-\d\d'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 300,
            "non_mlag": 330
        },
        "tcam_profile": None,
        "trident_forwarding_table_partition": (
            "flexible exact-match 16000 "
            "l2-shared 18000 l3-shared 22000"),
        "feature_support": {
            "queue_monitor_length_notify": False,
            "phone": True,
            "poe": False,
        },
        "ip_locking": {
            "support": True
        },
    },
    "trident3x4-chassis": {
        "regexes": [r'CCS-75\d'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 300,
            "non_mlag": 330
        },
        "tcam_profile": None,
        "trident_forwarding_table_partition": (
            "flexible exact-match 16000 "
            "l2-shared 18000 l3-shared 22000"),
        "feature_support": {
            "queue_monitor_length_notify": False,
            "phone": True,
            "poe": True,
        },
        "ip_locking": {
            "support": True
        },
        "per_interface_mtu": False,
    },
    "trident3x5|7-fixed": {
        "regexes": [r'DCS-7050\w(X3)'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 300,
            "non_mlag": 330
        },
        "tcam_profile": None,
        "trident_forwarding_table_partition": (
            "flexible exact-match 16384 "
            "l2-shared 98304 l3-shared 131072"),
        "feature_support": {
            "queue_monitor_length_notify": False,
            "phone": True,
        },
        "ip_locking": {
            "support": True
        },
    },
    "trident3-chassis": {
        "regexes": [r'DCS-73\d\dX3'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 1200,
            "non_mlag": 1320
        },
        "tcam_profile": None,
        "trident_forwarding_table_partition": (
            "flexible exact-match 16384 "
            "l2-shared 98304 l3-shared 131072"),
        "management_interface": "Management0",
    },
    "trident4-chassis": {
        "regexes": [r'DCS-73\d\dX4'],
        "tcam_profile": None,
        "reload_delay": {
            "mlag": 300,
            "non_mlag": 330,
        },
        "bgp_update_wait_for_convergence": True,
        "bgp_update_wait_install": False,
    },
    "veos": {
        "regexes": [veos_regex],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 300,
            "non_mlag": 330
        },
        "tcam_profile": None,
        "management_interface": "Management0",
        "ip_locking": {
            "support": True
        },
        "bgp_update_wait_for_convergence": False,
        "bgp_update_wait_install": False,
        "feature_support": {
            "queue_monitor_length_notify": False,
            "interface_storm_control": False
        },
    },
    "default": {
        "regexes": [r'.+'],
        "info": "Configured in standard settings",
        "reload_delay": {
            "mlag": 300,
            "non_mlag": 330
        },
        "tcam_profile": None,
        "feature_support": {
            # "queue-monitor length notify" is only valid for R-Series
            # so should be disabled on default platform.
            "queue_monitor_length_notify": False,
        },
    }
}


class Device:
    '''
    Object to store device information
    - ip:           IP address of device
    - deviceId:     ID of the device
    - deviceMac:    Mac address of the device
    - hostName:     Hostname of the device
    - modelName:    Model name of the device
    '''

    def __init__(self, deviceId: Optional[str] = None,
                 ip: Optional[str] = None,
                 deviceMac: Optional[str] = None,
                 hostName: Optional[str] = None,
                 modelName: Optional[str] = None):
        self.id = deviceId
        self.ip = ip
        self.mac = deviceMac
        self.hostName = hostName
        self.modelName = modelName
        # dict of interface name -> interface
        self._interfaces: Dict = {}

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def getInterfaces(self):
        '''
        Returns a dictionary list of the interfaces assigned to the Device object
        '''
        return self._interfaces.values()

    def getInterface(self, name):
        '''
        Returns a particular named interface from the interfaces assigned to the Device
        object
        '''
        return self._interfaces.get(name)

    def addInterface(self, name: str):
        '''
        addInterface assigns an interface to the Device object
        '''
        intf = self._interfaces.get(name)
        if intf:
            # interface already exists, do a noop
            return
        intf = Interface(name, self)
        self._interfaces[name] = intf

    def getSingleTag(self, ctx, label: str, required: bool = True):
        '''
        Returns a Tag of the label assigned to the device.
        Raises TagTooManyValuesException if there are multiple tags of the label assigned.
        Raises TagMissingException if required is True and the tag is missing.
        Returns None if required is False and the tag is missing.
        '''
        devName = str(self.hostName) if self.hostName else str(self.id)
        values = ctx.tags._getDeviceTags(self.id).get(label)
        if values and len(values) > 1:
            raise TagTooManyValuesException(label, devName, values)
        if required and not values:
            raise TagMissingException(label, devName)
        return Tag(label, values[0]) if values else None

    def getTags(self, ctx, label: str = None):
        '''
        Returns a list of Tags matching the specified label assigned to the device.
        If label is unspecified then it returns all Tags assigned to the device.
        '''
        devTags: List[Tag] = []
        if not (ctxDevTags := ctx.tags._getDeviceTags(self.id)):
            return devTags
        # Note use list instead of .items()
        # parallel thread might add/delete tags
        for tagLabel in list(ctxDevTags):
            if label and label != tagLabel:
                continue
            for value in ctxDevTags.get(tagLabel, []):
                devTags.append(Tag(tagLabel, value))
        return devTags

    def _assignTag(self, ctx, tag: Tag, replaceValue: bool = True):
        '''
        Assign a Tag to a device.
        If replaceValue is True ensures only one value of label is assigned to device.
        '''
        ctx.tags._assignDeviceTag(self.id, tag.label, tag.value, replaceValue)

    def _unassignTag(self, ctx, tag: Tag):
        '''
        Unassign a Tag from a device.
        If tag.value is unspecified unassign all tags of label from device.
        '''
        if tag.value:
            ctx.tags._unassignDeviceTag(self.id, tag.label, tag.value)
        else:
            ctx.tags._unassignDeviceTagLabel(self.id, tag.label)

    def getInterfacesByTag(self, ctx, tag: Tag, inTopology: bool = True):
        '''
        Returns list of interfaces that have the user tag assigned to them.
        If tag.value is unspecified then returns interfaces having that label assigned.
        By default only interfaces in the topology are returned.
        '''
        interfaces = []
        # Note use list instead of .items()
        # parallel thread might add/delete tags
        for intfId in list(devIntfTags := ctx.tags._getAllInterfaceTags().get(self.id, {})):
            tags = devIntfTags.get(intfId, {})
            if tags.get(tag.label) and (
                    not tag.value or tag.value in tags.get(tag.label, [])):
                if intf := self.getInterface(intfId):
                    interfaces.append(intf)
                elif not inTopology:
                    interfaces.append(Interface(name=intfId, device=self))
        return interfaces


# Interfaces and devices are defined together to avoid circular imports
class Interface:
    '''
    Object to store interface related information
    - name:     The name of the interface
    - device:   The device that the interface is on
    '''

    def __init__(self, name: str, device: Device):
        self.name = name
        self._device = device
        self._peerInterface = None
        self._peerDevice: Optional[Device] = None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def getPeerInterface(self):
        return self._peerInterface

    def getPeerDevice(self):
        return self._peerDevice

    def getDevice(self):
        return self._device

    def setPeerInfo(self, device: Device, interface):
        self._peerInterface = interface
        self._peerDevice = device

    def getPeerInfo(self):
        return self._peerDevice, self._peerInterface

    def getSingleTag(self, ctx, label: str, required: bool = True):
        '''
        Returns a Tag of the label assigned to the interface.
        Raises TagTooManyValuesException if there are multiple tags of the label assigned.
        Raises TagMissingException if required is True and the tag is missing.
        Returns None if required is False and the tag is missing.
        '''
        devName = str(self._device.hostName) if self._device.hostName else str(self._device.id)
        values = ctx.tags._getInterfaceTags(self._device.id, self.name).get(label)
        if values and len(values) > 1:
            raise TagTooManyValuesException(label, devName, values, self.name)
        if required and not values:
            raise TagMissingException(label, devName, self.name)
        return Tag(label, values[0]) if values else None

    def getTags(self, ctx, label: str = None):
        '''
        Returns a list of Tags matching the specified label assigned to the interface.
        If label is unspecified then it returns all Tags assigned to the interface.
        '''
        tags: List[Tag] = []
        if not (ctxTags := ctx.tags._getInterfaceTags(self._device.id, self.name)):
            return tags
        # Note use list instead of .items()
        # parallel thread might add/delete tags
        for tagLabel in list(ctxTags):
            if label and label != tagLabel:
                continue
            for value in ctxTags.get(tagLabel, []):
                tags.append(Tag(tagLabel, value))
        return tags

    def _assignTag(self, ctx, tag: Tag, replaceValue: bool = True):
        '''
        Assign a Tag to an interface.
        If replaceValue is True ensures only one value of label is assigned.
        '''
        ctx.tags._assignInterfaceTag(self._device.id, self.name, tag.label, tag.value, replaceValue)

    def _unassignTag(self, ctx, tag: Tag):
        '''
        Unassign a Tag from an interface.
        If tag.value is unspecified unassign all tags of label.
        '''
        if tag.value:
            ctx.tags._unassignInterfaceTag(self._device.id, self.name, tag.label, tag.value)
        else:
            ctx.tags._unassignInterfaceTagLabel(self._device.id, self.name, tag.label)
