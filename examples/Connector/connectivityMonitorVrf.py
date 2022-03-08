# Copyright (c) 2021 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from cloudvision.Connector.grpc_client import GRPCClient, create_query
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


def getConMonKeys(client, dId):
    pathElts = [
        "Devices",
        dId,
        "versioned-data",
        "connectivityMonitorVrf",
        "stats"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def getConnMon(client, dId, key):
    pathElts = [
        "Devices",
        dId,
        "versioned-data",
        "connectivityMonitorVrf",
        "stats",
        key,
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def getConnMonCfg(client, dId, key):
    pathElts = [
        "Devices",
        dId,
        "versioned-data",
        "connectivityMonitorVrf",
        "config",
        key
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def getAllConnMon(client, dId, key, interface):
    pathElts = [
        "Devices",
        dId,
        "versioned-data",
        "connectivityMonitorVrf",
        "stats",
        key,
        interface
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def getSwitchesInfo(client):
    pathElts = [
        "DatasetInfo",
        "Devices"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def report(client, device):
    keys = getConMonKeys(client, device)
    key_list = list(keys.keys())
    datasetInfo = getSwitchesInfo(client)
    hostname = datasetInfo[device]['hostname']

    for i in key_list:
        vrf = i['vrfName']
        host = i['hostName']
        stats = getConnMon(client, device, i)
        interfaces = list(stats.keys())
        for intf in interfaces:
            stats_intf = getAllConnMon(client, device, i, intf)
            httpResp = stats_intf['httpResponseTime']
            jitter = stats_intf['jitter']
            latency = stats_intf['latency']
            pktloss = stats_intf['packetLoss']
            ipaddr = getConnMonCfg(client, device, i)['ipAddr']
            hdr_part1 = f"{hostname + ' (' + vrf + '/' + intf + ') to ' + host:<50}"
            hdr_part2 = f"{ipaddr:<30}{str(httpResp) + 'ms':<30}{str(jitter) + 'ms':<30}"
            hdr_part3 = f"{str(latency) + 'ms':<30}{str(pktloss)  + '%':<30}"
            print(hdr_part1 + hdr_part2 + hdr_part3)


def main(apiserverAddr, token=None, certs=None, key=None, ca=None):

    with GRPCClient(apiserverAddr, token=token, key=key,
                    ca=ca, certs=certs) as client:
        datasetInfo = getSwitchesInfo(client)
        col1 = 'Connection'
        col2 = 'Host IP Address per VRF'
        col3 = 'HTTP RESPONSE TIME per VRF'
        col4 = 'Jitter per VRF'
        col5 = 'Latency per VRF'
        col6 = 'Packet Loss Per VRF'
        dashboardColumns = f"{col1:<50}{col2:<30}{col3:<30}{col4:<30}{col5:<30}{col6:<30}"
        if args.device:
            print(dashboardColumns)
            report(client, args.device)
        else:
            # Detect which devices are running Connectivity Monitor
            print(dashboardColumns)
            for elem in datasetInfo.keys():
                if not (getConMonKeys(client, elem) == {}):
                    report(client, elem)
    return 0


if __name__ == "__main__":
    base.add_argument("--device", type=str, help="device to subscribe to")
    args = base.parse_args()
    exit(main(args.apiserver, certs=args.certFile, key=args.keyFile,
              ca=args.caFile, token=args.tokenFile))
