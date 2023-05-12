# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec.custom_types import FrozenDict
from cloudvision.Connector.codec import Wildcard, Path
from utils import pretty_print
from parser import base
import json


def get_lldp_neighbors(client, device_id):
    """Returns the interfaces report"""

    path_elts = [
        "Sysdb",
        "l2discovery",
        "lldp",
        "status",
        "local",
        Wildcard(),
        "portStatus",
        Wildcard(),
        "remoteSystem",
        Wildcard(),
    ]
    dataset = device_id
    query = [create_query([(path_elts, [])], dataset)]
    result = {}
    for batch in client.get(query):
        for notif in batch["notifications"]:
            if not notif["updates"]:
                continue
            path_elts = notif["path_elements"]
            lldp_key = path_elts[7]
            neighbors = result.get(lldp_key, {})
            neighbors.update(notif["updates"])
            result[lldp_key] = neighbors
    return result


def report(data):
    """Generate report in a human readable format."""
    col1 = "Port"
    col2 = "Neighbor Device ID"
    col3 = "Neighbor Port ID"
    col4 = "TTL"
    print(f"{col1:<30}{col2:<30}{col3:<30}{col4:<30}")
    for k, v in data.items():
        port = k
        nei_dev_id = v["sysName"]["value"]["value"]
        nei_port_id = v["msap"]["portIdentifier"]["portId"]
        ttl = v["ttl"]
        print(f"{port:<30} {nei_dev_id:<30} {nei_port_id:<30} {ttl:<30}")


def main(apiserver_addr, token=None, certs=None, ca=None, key=None):
    """Connecting to CV and invoking the functions."""
    with GRPCClient(apiserver_addr, token=token, key=key, ca=ca, certs=certs) as client:
        if args.device:
            device = args.device
        else:
            device = None
        data = get_lldp_neighbors(client, device)
        report(data)

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
