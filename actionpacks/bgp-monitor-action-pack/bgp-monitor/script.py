# Copyright (c) 2021 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from time import sleep
from google.protobuf.timestamp_pb2 import Timestamp
from cloudvision.Connector.grpc_client import create_query
from cloudvision.Connector.codec import Path, Wildcard


def extractBGPStats(batch, statsDict, useVrfs=False):
    for notif in batch["notifications"]:
        for stat in notif["updates"]:
            count = notif["updates"][stat]
            # Skip over any path pointers, such as to the vrf counts
            if isinstance(count, Path):
                continue
            # If using vrfs, append the vrf name to the stat to stop overlap
            # The vrf name is the last path element of the notification
            if useVrfs:
                stat = notif['path_elements'][-1] + "_" + stat
            statsDict[stat] = count


def IsStatsDiffExpected(prevStats, currentStats, expectedDiff: int):
    # Check to see if there is a difference in the stats, as expected by the user args
    # This allows for the user to add 2 spines to their network or retire a spine
    actualDiff = 0
    for stat, count in prevStats.items():
        actualDiff = actualDiff + currentStats[stat] - count

    return expectedDiff == actualDiff


# Count the vrf specific BGP peers rather than just the device's BGP peers
# args are always in string format
useVrfCounts = ctx.changeControl.args.get("vrfs") == "True"
expectedStatsDiff = ctx.changeControl.args.get("expected_difference")
# If not set by the user, the arg will be the empty string, so we need to parse
expectedStatsDiff = int(expectedStatsDiff) if expectedStatsDiff else 0
checkWait = ctx.changeControl.args.get("check_wait")
checkWait = int(checkWait) if checkWait else 60

with ctx.getCvClient() as client:
    ccStartTs = ctx.changeControl.getStartTime(client)
    if not ccStartTs:
        raise UserWarning("No change control ID present")
    ccStart = Timestamp()
    ccStart.FromNanoseconds(int(ccStartTs))

    device = ctx.getDevice()
    if device is None or device.id is None:
        err = ("Missing change control device" if device is None
               else "device {} is missing 'id'".format(device))
        raise UserWarning(err)
    pathElts = [
        "Devices", device.id, "versioned-data", "counts", "bgpState",
    ]
    query = [
        create_query([(pathElts, [])], "analytics")
    ]
    # Create a query for the vrfs
    vrfPathElts = pathElts + ["vrf", Wildcard()]
    vrfQuery = [
        create_query([(vrfPathElts, [])], "analytics")
    ]

    prevBGPStats = {}
    # Do a point in time get to get counts from before the CC
    for batch in client.get(query, start=ccStart, end=ccStart):
        extractBGPStats(batch, prevBGPStats)
    # Get the vrf counts if parameter set
    if useVrfCounts:
        for batch in client.get(vrfQuery, start=ccStart, end=ccStart):
            extractBGPStats(batch, prevBGPStats, useVrfCounts)

    # Wait the timeout before checking again, to allow for # of BGP peers to settle
    sleep(checkWait)

    # Get current bgp stats counts
    currBGPStats = {}
    for batch in client.get(query):
        extractBGPStats(batch, currBGPStats)
    # Get the vrf counts if parameter set
    if useVrfCounts:
        for batch in client.get(vrfQuery):
            extractBGPStats(batch, currBGPStats, useVrfCounts)

    if not IsStatsDiffExpected(prevBGPStats, currBGPStats, expectedStatsDiff):
        err = ("Inconsistent BGP counts for Device {} were not within expected difference of {}.\n"
               "Before CC: {}\n"
               "After CC: {}").format(device.id, expectedStatsDiff, prevBGPStats, currBGPStats)
        ctx.alog(err)
        raise UserWarning("BGP_check: Failed")

ctx.alog("BGP stats were stable accross change control")
