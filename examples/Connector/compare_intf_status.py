# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
from datetime import datetime, timedelta
from google.protobuf.timestamp_pb2 import Timestamp
from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec import Wildcard, Path
from cloudvision.Connector.codec.custom_types import FrozenDict
from parser import base


def get(client, dataset, pathElts):
    ''' Returns a query on a path element'''
    result = {}
    query = [
        create_query([(pathElts, [])], dataset)
    ]

    for batch in client.get(query):
        for notif in batch["notifications"]:
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


def getInventory(client):
    pathElts = [
        "DatasetInfo",
        "Devices"
    ]
    query = [
        create_query([(pathElts, [])], "analytics")
    ]
    query = unfreeze(query)

    allinventory = []
    for batch in client.get(query):
        for notif in batch["notifications"]:
            for device in notif["updates"]:
                allinventory.append({"serialnumber": device,
                                    "hostname": notif["updates"][device]["hostname"]})
    return (allinventory)


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


def getIntfStatusChassis(client, dId, start, end):
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

        for batch in client.get(query, start=start, end=end):
            for notif in batch["notifications"]:
                try:
                    intfStatusChassis.append({"interface": notif['path_elements'][-1],
                                              "status": notif['updates']['linkStatus']['Name'],
                                              "active": notif['updates']['active']})
                except KeyError:
                    continue
    return (intfStatusChassis)


def getIntfStatusFixed(client, dId, start, end):
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
    for batch in client.get(query, start=start, end=end):
        for notif in batch["notifications"]:
            try:
                intfStatusFixed.append({"interface": notif['path_elements'][-1],
                                        "status": notif['updates']['linkStatus']['Name'],
                                        "active": notif['updates']['active']})
            except KeyError:
                continue
    return (intfStatusFixed)


def main(apiserverAddr, token=None, cert=None, key=None, ca=None, days=0, hours=1, minutes=0):

    startDtime = datetime.now() - timedelta(days=days, hours=hours, minutes=minutes)
    start = Timestamp()
    end = Timestamp()
    if args.start:
        start_ts = datetime.fromisoformat(args.start)
        start.FromDatetime(start_ts)
    else:
        start.FromDatetime(startDtime)  # type: ignore
    if args.end:
        end_ts = datetime.fromisoformat(args.end)
        end.FromDatetime(end_ts)
    if args.deviceId:
        deviceId = args.deviceId
        with GRPCClient(apiserverAddr, token=token, certs=cert, key=key,
                        ca=ca) as client:
            entmibType = deviceType(client, deviceId)
            if entmibType == 'modular':
                firstdata = getIntfStatusChassis(client, deviceId, start, start)
                seconddata = getIntfStatusChassis(client, deviceId, end, end)
            else:
                firstdata = getIntfStatusFixed(client, deviceId, start, start)
                seconddata = getIntfStatusFixed(client, deviceId, end, end)

            change = False
            for interfacesecond in seconddata:
                for interfacefirst in firstdata:
                    if interfacefirst["interface"] == interfacesecond["interface"]:
                        if interfacefirst["status"] != interfacesecond["status"] and \
                                interfacesecond["active"] is True:
                            print(interfacesecond,
                                  interfacefirst["status"], interfacesecond["status"])
                            change = True
            if change is False:
                print(" no change")
    else:
        with GRPCClient(apiserverAddr, token=token, certs=cert, key=key,
                        ca=ca) as client:
            inventory = getInventory(client)

            for device in inventory:
                deviceId = device["serialnumber"]
                hostname = device["hostname"]
                with GRPCClient(apiserverAddr, token=token, certs=cert, key=key,
                                ca=ca) as client:
                    entmibType = deviceType(client, deviceId)
                    if entmibType == 'modular':
                        firstdata = getIntfStatusChassis(client, deviceId, start, start)
                        seconddata = getIntfStatusChassis(client, deviceId, end, end)
                    else:
                        firstdata = getIntfStatusFixed(client, deviceId, start, start)
                        seconddata = getIntfStatusFixed(client, deviceId, end, end)

                    change = False
                    print(hostname)
                    for interfacesecond in seconddata:
                        for interfacefirst in firstdata:
                            if interfacefirst["interface"] == interfacesecond["interface"]:
                                if interfacefirst["status"] != interfacesecond["status"] and \
                                        interfacesecond["active"] is True:
                                    print(interfacesecond,
                                          interfacefirst["status"], interfacesecond["status"])
                                    change = True
                    if change is False:
                        print(" no change")
    return 0


if __name__ == "__main__":
    base.add_argument("--start", required=True,
                      help=("Start time of the lookup in ISO format,"
                            "e.g.: 2021-02-02T21:46:00"))
    base.add_argument("--end", required=True,
                      help=("End time of the lookup in ISO format,"
                            "e.g.: 2021-02-02T21:46:00"))
    base.add_argument("--deviceId", required=False,
                      help=("Serial number of the device, if not supplied it will go "
                            "through all the devices in the inventory"))
    args = base.parse_args()
    exit(main(args.apiserver, ca=args.caFile,
              cert=args.certFile, key=args.keyFile, token=args.tokenFile))
