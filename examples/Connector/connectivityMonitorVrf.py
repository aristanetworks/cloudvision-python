# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from utils import pretty_print
from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec import Wildcard
from parser import base

debug = False


def get_conn_mon(client, device=None):
    """Returns a query on a path element"""
    device = device if device else Wildcard()
    path_elts = [
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
    query = [create_query([(path_elts, [])], dataset)]
    for batch in client.get(query):
        for notif in batch["notifications"]:
            # there are some static path pointers at this path so we remove them from the update
            # results
            notif["updates"].pop("aggregate", None)
            notif["updates"].pop("anomaly", None)
            # if the updates only contained the static path pointers then continue as there is no
            # data of interest here
            if not notif["updates"]:
                continue
            path_elts = notif["path_elements"]
            # we need to store the result per device, per host+Vrf and per source interface
            conn_mon_key = (path_elts[1], path_elts[5], path_elts[6])
            # retreive any previous stats for this conn_mon_key for the scenario where the stats do
            # not arrive together
            # update the stats object for this conn_mon_key
            conn_mon_stats_val = result.get(conn_mon_key, {})
            conn_mon_stats_val.update(notif["updates"])
            result[conn_mon_key] = conn_mon_stats_val
    return result


def get(client, dataset, path_elts):
    """Returns a query on a path element"""
    result = {}
    query = [create_query([(path_elts, [])], dataset)]
    for batch in client.get(query):
        for notif in batch["notifications"]:
            if debug:
                pretty_print(notif["updates"])
            result.update(notif["updates"])
    return result


def get_conn_mon_cfg(client, device=None):
    ''' Get connectivity monitor configuration for a device or all devices.
    '''
    device = device if device else Wildcard()
    path_elts = [
        "Devices",
        device,
        "versioned-data",
        "connectivityMonitorVrf",
        "config",
        Wildcard(),
    ]
    dataset = "analytics"
    result = {}
    query = [create_query([(path_elts, [])], dataset)]

    for batch in client.get(query):
        for notif in batch["notifications"]:
            if not notif["updates"]:
                continue
            path_elts = notif["path_elements"]
            # we need to store the result per device and host+Vrf
            conn_mon_key = (path_elts[1], path_elts[5])
            result[conn_mon_key] = notif["updates"]
    return result


def get_switches_info(client):
    ''' Get device information.
    '''
    path_elts = ["DatasetInfo", "Devices"]
    dataset = "analytics"
    return get(client, dataset, path_elts)


def report(client, data, config_data):
    ''' Generate report in a human readable format.
    '''
    dataset_info = get_switches_info(client)
    for k, v in data.items():
        hostname = dataset_info[k[0]]["hostname"]
        vrf = k[1]["vrfName"]
        http_resp = v["httpResponseTime"]
        jitter = v["jitter"]
        latency = v["latency"]
        pktloss = v["packetLoss"]
        host = k[1]["hostName"]
        if "ipAddr" in config_data[(k[0], k[1])]:
            ipaddr = config_data[(k[0], k[1])]["ipAddr"]
        else:
            ipaddr = ""
        intf = k[2]
        hdr_part1 = f"{hostname + ' (' + vrf + '/' + intf + ') to ' + host:<50}"
        hdr_part2 = f"{ipaddr:<30}{str(http_resp) + 'ms':<30}{str(jitter) + 'ms':<30}"
        hdr_part3 = f"{str(latency) + 'ms':<30}{str(pktloss)  + '%':<30}"
        print(hdr_part1 + hdr_part2 + hdr_part3)


def main(apiserver_addr, token=None, certs=None, key=None, ca=None):

    with GRPCClient(apiserver_addr, token=token, key=key, ca=ca, certs=certs) as client:
        col1 = "Connection"
        col2 = "Host IP Address per VRF"
        col3 = "HTTP RESPONSE TIME per VRF"
        col4 = "Jitter per VRF"
        col5 = "Latency per VRF"
        col6 = "Packet Loss Per VRF"
        dashboard_columns = (
            f"{col1:<50}{col2:<30}{col3:<30}{col4:<30}{col5:<30}{col6:<30}"
        )
        if args.device:
            device = args.device
        else:
            device = None
        data = get_conn_mon(client, device)
        config_data = get_conn_mon_cfg(client, device)
        print(dashboard_columns)
        report(client, data, config_data)

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
