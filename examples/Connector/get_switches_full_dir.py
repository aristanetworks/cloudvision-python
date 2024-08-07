# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec import Wildcard

from utils import pretty_print
from parser import base

DIR_SIZE = 90

def add_hostnames(client, hostname_dict):

    pathElts = [
        "DatasetInfo",
        "Devices"
    ]

    dataset = "analytics"
    query = [create_query([(pathElts, [])], dataset)]

    for batch in client.get(query):
        for notif in batch["notifications"]:
            updates = notif["updates"]
            for k, v in updates.items():
                serial = k
                hostname = v["hostname"]
                if serial in hostname_dict: 
                    hostname_dict[serial]["hostname"] = hostname    

    return hostname_dict


def get_dir_usage(client):

    pathElts = [
        "Devices",
        Wildcard(),
        "versioned-data",
        "hardware",
        "disk",
        Wildcard(),
    ]
    query = [
        create_query([(pathElts, [])], "analytics")
    ]

    host_name_dict = {}
    for batch in client.get(query):
        for notif in batch["notifications"]:

            updates = notif["updates"]
            path_elts = notif["path_elements"]
            serial, dir = path_elts[1], path_elts[5]

            for key, perc in updates.items():
                if isinstance(perc, float):
                    if key == 'usedPartitionPercent':
                        if perc > DIR_SIZE:
                            if serial in host_name_dict:
                                host_name_dict[serial][dir] = perc
                            else:
                                host_name_dict[serial] = {}
                                host_name_dict[serial][dir] = perc

    return host_name_dict


def main(apiserverAddr, token=None, certs=None, key=None, ca=None):
    pathElts = [
        "Devices",
        Wildcard(),
        "versioned-data",
        "hardware",
        "disk",
        Wildcard(),
    ]
    query = [
        create_query([(pathElts, [])], "analytics")
    ]

    with GRPCClient(apiserverAddr, token=token, key=key,
                    ca=ca, certs=certs) as client:
        
        results = get_dir_usage(client)
        hostname_dict= add_hostnames(client, results)

        #pretty_print(hostname_dict)

        for swi, val in hostname_dict.items():
            h_name = hostname_dict[swi]['hostname']
            print(f'Switch {h_name} ({swi}),')

            for dir, perc in sorted(val.items()):
                if isinstance(perc, float):
                    h_name = hostname_dict[swi]['hostname']
                    print(f'  {dir} is {perc:.2f}% utilised')
            print()

    return 0


if __name__ == "__main__":
    args = base.parse_args()
    exit(main(args.apiserver, certs=args.certFile, key=args.keyFile,
              ca=args.caFile, token=args.tokenFile))
