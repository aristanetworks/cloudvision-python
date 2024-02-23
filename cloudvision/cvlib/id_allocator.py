# Copyright (c) 2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from typing import Set, Dict, List, Optional


class IdAllocator:
    '''
    Object to generate unique integer ids, eg. used for generating nodeIds.
    Can also be used for checking manually entered ids for duplicates.
    - start:        starting value of id range
    - end:          ending value of id range
    The following are only used if checking duplicate id errors:
    - idNames:      optional name associated with ids
    - idLabel:      name describing id type
    - groupLabel:   name describing what is being id'd
    '''
    def __init__(self, start: int = 1,
                 end: int = 65000,
                 idLabel: str = 'id',
                 groupLabel: str = 'devices'):
        self.rangeStart = start
        self.rangeEnd = end
        self.available = set(range(start, end + 1))
        self.allocated: Set[int] = set()
        self.idNames: Dict[int, Optional[str]] = {}
        self.idLabel = idLabel
        self.groupLabel = groupLabel

    def allocate(self, allocId: int = None, name: str = None) -> int:
        if allocId is not None:
            if self.rangeStart <= allocId <= self.rangeEnd:
                if allocId not in self.allocated:
                    self.allocated.add(allocId)
                    self.idNames[allocId] = name
                    self.available.remove(allocId)
                elif name:
                    assert name == self.getIdNames().get(allocId), (
                        f"The same {self.idLabel}, {allocId}, can not be "
                        f"applied to both of these {self.groupLabel}: "
                        f"{self.getIdNames().get(allocId)}, "
                        f"{name}")
                return allocId
            raise ValueError(f"Id {allocId} is outside the available range")
        if not self.available:
            raise ValueError("no more Ids available")
        allocatedId = min(self.available)
        self.available.remove(allocatedId)
        self.allocated.add(allocatedId)
        self.idNames[allocatedId] = name
        return allocatedId

    def free(self, freeId: int):
        if self.rangeStart <= freeId <= self.rangeEnd:
            self.available.add(freeId)
            if freeId in self.allocated:
                self.allocated.remove(freeId)
                self.idNames.pop(freeId, None)
        else:
            raise ValueError(f"Id {freeId} is outside the available range")

    def getAvailable(self) -> List:
        return list(self.available)

    def getAllocated(self) -> List:
        return list(self.allocated)

    def getIdNames(self) -> Dict:
        return self.idNames
