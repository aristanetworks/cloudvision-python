# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from logging import getLogger, Logger
from typing import Dict, List

from .device import Device

# This is a global due to it being unpickleable and the classes needing to be pickleable
logger = getLogger(__name__)


class Connection:
    def __init__(self, sourceDevice, sourceInterface, destDevice, destInterface):
        self.sourceDevice = sourceDevice
        self.sourceInterface = sourceInterface
        self.destDevice = destDevice
        self.destInterface = destInterface

    def __str__(self):
        return (
            f"{self.sourceDevice}:{self.sourceInterface} --> {self.destDevice}:{self.destInterface}")


class Topology:
    '''
    Topology object that stores devices and their connection to one another in dict form:
    - deviceMap:   Prebuilt topology device dictionary to instantiate the class with
    '''

    def __init__(self, deviceMap: Dict[str, Device]):
        if not deviceMap:
            logger.warning("Topology model was provided an empty device map")
            deviceMap = {}
        self._deviceMap = deviceMap

    @staticmethod
    def setLogger(loggerToUse: Logger):
        global logger
        logger = loggerToUse

    def getDevices(self, deviceIds: List[str] = None):
        if not deviceIds:
            return list(self._deviceMap.values())
        devices = []
        for did in deviceIds:
            if did not in self._deviceMap:
                logger.info(
                    "Requested device was not in topology data, creating a simple device: %s", did)
                # Create a device with no topology information
                newDevice = Device(deviceId=did)
                self._deviceMap[did] = newDevice
            devices.append(self._deviceMap[did])
        return devices
