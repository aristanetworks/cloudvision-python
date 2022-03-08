# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec.custom_types import FrozenDict
from cloudvision.Connector.codec import Wildcard, Path
from utils import pretty_print
from parser import base
import json

debug = False


def get(client, dataset, pathElts):
    ''' Returns a query on a path element'''
    result = {}
    query = [
        create_query([(pathElts, [])], dataset)
    ]

    for batch in client.get(query):
        for notif in batch["notifications"]:
            if debug:
                pretty_print(notif["updates"])
            result.update(notif["updates"])
    return result


def unfreeze(o):
    ''' Used to unfreeze Frozen dictionaries'''
    if isinstance(o, (dict, FrozenDict)):
        return dict({k: unfreeze(v) for k, v in o.items()})

    if isinstance(o, (str)):
        return o

    try:
        return [unfreeze(i) for i in o]
    except TypeError:
        pass

    return o


def deviceType(client, dId):
    ''' Returns the type of the device: modular/fixed'''
    pathElts = [
        "Sysdb",
        "hardware",
        "entmib"
    ]
    dataset = dId
    query = get(client, dataset, pathElts)
    query = unfreeze(query)
    if query['fixedSystem'] is None:
        dType = 'modular'
    else:
        dType = 'fixedSystem'
    return dType


def printIntfStatus(intfStatus):
    ''' Helper function to print the interface statuses.'''
    print(f"{'Interface Name':<25}{'status'}\n")
    connected = 0
    down = 0
    for interface in intfStatus:
        print(f"{interface['interface']:<25}{interface['status']}")
        if interface['active'] is True:
            if interface['status'] == "linkUp":
                connected += 1
            else:
                down += 1
    print(f"\nEthernet Status on {args.deviceId}:")
    print(f"{connected:>10} interfaces connected (including Management)")
    print(f"{down:>10} interfaces down")


def getIntfStatusChassis(client, dId):
    ''' Returns the interfaces report for a modular device.'''
    # Fetch the list of slices/linecards
    pathElts = [
        "Sysdb",
        "interface",
        "status",
        "eth",
        "phy",
        "slice"
    ]
    dataset = dId
    query = get(client, dataset, pathElts)
    queryLC = unfreeze(query).keys()
    intfStatusChassis = []

    # Go through each linecard and get the state of all interfaces
    for lc in queryLC:
        pathElts = [
            "Sysdb",
            "interface",
            "status",
            "eth",
            "phy",
            "slice",
            lc,
            "intfStatus",
            Wildcard()
        ]

        query = [
            create_query([(pathElts, [])], dataset)
        ]

        for batch in client.get(query):
            for notif in batch["notifications"]:
                intfStatusChassis.append({"interface": notif['path_elements'][-1],
                                          "status": notif['updates']['linkStatus']['Name'],
                                          "active": notif['updates']['active']})
    printIntfStatus(intfStatusChassis)


def getIntfStatusFixed(client, dId):
    ''' Returns the interfaces report for a fixed system device.'''
    pathElts = [
        "Sysdb",
        "interface",
        "status",
        "eth",
        "phy",
        "slice",
        "1",
        "intfStatus",
        Wildcard()
    ]
    query = [
        create_query([(pathElts, [])], dId)
    ]
    query = unfreeze(query)

    intfStatusFixed = []
    for batch in client.get(query):
        for notif in batch["notifications"]:
            try:
                intfStatusFixed.append({"interface": notif['path_elements'][-1],
                                        "status": notif['updates']['linkStatus']['Name'],
                                        "active": notif['updates']['active']})
            except KeyError as e:
                print(e)
                continue
    printIntfStatus(intfStatusFixed)


def main(apiserverAddr, dId, token=None, certs=None, ca=None, key=None):

    with GRPCClient(apiserverAddr, token=token, key=key, ca=ca, certs=certs) as client:
        entmibType = deviceType(client, args.deviceId)
        if entmibType == 'modular':
            getIntfStatusChassis(client, args.deviceId)
        else:
            getIntfStatusFixed(client, args.deviceId)

    return 0


if __name__ == "__main__":
    base.add_argument("--deviceId",
                      help="device id/serial number to query intfStatus for")
    args = base.parse_args()

    exit(main(args.apiserver, args.deviceId, token=args.tokenFile,
              certs=args.certFile, ca=args.caFile))
