# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec import Wildcard, Path
from cloudvision.Connector.codec.custom_types import FrozenDict
from utils import pretty_print
from parser import base

debug = False


def getConnMon(client, device=None):
    """Returns a query on a path element"""
    device = device if device else Wildcard()
    pathElts = [
        "Devices",
        device,
        "versioned-data",
        "connectivityMonitorVrf",
        "stats",
        Wildcard(),
        Wildcard(),
    ]
    dataset = "analytics"
    result = {}
    query = [create_query([(pathElts, [])], dataset)]

    for batch in client.get(query):
        for notif in batch["notifications"]:
            # there are some static path pointers at this path so we remove them from the update results
            notif["updates"].pop("aggregate", None)
            notif["updates"].pop("anomaly", None)
            # if the updates only contained the static path pointers then continue as there is no data of interest here
            if not notif["updates"]:
                continue
            pathElts = notif["path_elements"]
            connMonKey = (pathElts[1], pathElts[5], pathElts[6])
            result[connMonKey] = notif["updates"]

    return result


def get(client, dataset, pathElts):
    """Returns a query on a path element"""
    result = {}
    query = [create_query([(pathElts, [])], dataset)]

    for batch in client.get(query):
        for notif in batch["notifications"]:
            if debug:
                pretty_print(notif["updates"])
            result.update(notif["updates"])
    return result


def getConnMonCfg(client, device=None):
    device = device if device else Wildcard()
    pathElts = [
        "Devices",
        device,
        "versioned-data",
        "connectivityMonitorVrf",
        "config",
        Wildcard(),
    ]
    dataset = "analytics"
    result = {}
    query = [create_query([(pathElts, [])], dataset)]

    for batch in client.get(query):
        for notif in batch["notifications"]:
            if not notif["updates"]:
                continue
            pathElts = notif["path_elements"]
            connMonKey = (pathElts[1], pathElts[5])
            result[connMonKey] = notif["updates"]
    return result


def getSwitchesInfo(client):
    pathElts = ["DatasetInfo", "Devices"]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def report(client, data, configData):
    datasetInfo = getSwitchesInfo(client)
    for k, v in data.items():
        hostname = datasetInfo[k[0]]["hostname"]
        vrf = k[1]["vrfName"]
        httpResp = v["httpResponseTime"]
        jitter = v["jitter"]
        latency = v["latency"]
        pktloss = v["packetLoss"]
        host = k[1]["hostName"]
        ipaddr = configData[(k[0], k[1])]["ipAddr"]
        intf = k[2]
        hdr_part1 = f"{hostname + ' (' + vrf + '/' + intf + ') to ' + host:<50}"
        hdr_part2 = f"{ipaddr:<30}{str(httpResp) + 'ms':<30}{str(jitter) + 'ms':<30}"
        hdr_part3 = f"{str(latency) + 'ms':<30}{str(pktloss)  + '%':<30}"
        print(hdr_part1 + hdr_part2 + hdr_part3)


def main(apiserverAddr, token=None, certs=None, key=None, ca=None):

    with GRPCClient(apiserverAddr, token=token, key=key, ca=ca, certs=certs) as client:
        col1 = "Connection"
        col2 = "Host IP Address per VRF"
        col3 = "HTTP RESPONSE TIME per VRF"
        col4 = "Jitter per VRF"
        col5 = "Latency per VRF"
        col6 = "Packet Loss Per VRF"
        dashboardColumns = (
            f"{col1:<50}{col2:<30}{col3:<30}{col4:<30}{col5:<30}{col6:<30}"
        )
        if args.device:
            device = args.device
        else:
            device = None
        data = getConnMon(client, device)
        configData = getConnMonCfg(client, device)
        print(dashboardColumns)
        report(client, data, configData)

    return 0


if __name__ == "__main__":
    base.add_argument(
        "--device", type=str, help="device (by SerialNumber) to subscribe to"
    )
    args = base.parse_args()
    exit(
        main(
            args.apiserver,
            certs=args.certFile,
            key=args.keyFile,
            ca=args.caFile,
            token=args.tokenFile,
        )
    )
