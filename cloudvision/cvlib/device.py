# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from typing import Dict, Optional


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

    def getInterfaces(self):
        return self._interfaces.values()

    def getInterface(self, name):
        return self._interfaces.get(name)

    def addInterface(self, name: str):
        intf = self._interfaces.get(name)
        if intf:
            # interface already exists, do a noop
            return
        intf = Interface(name, self)
        self._interfaces[name] = intf


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
