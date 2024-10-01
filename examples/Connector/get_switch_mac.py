# Copyright (c) 2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from cloudvision.Connector.grpc_client import GRPCClient, create_query

from parser import base
import time


def last_move_time(epoch_time):

    if epoch_time == 0.0:
        return '-'

    return int(time.time() - epoch_time)


def get_macs(client, device):

    pathElts = [
        "Smash",
        "bridging",
        "status",
        "smashFdbStatus"
    ]
    query = [
        create_query([(pathElts, [])], device)
    ]

    print(f'{"vlan":<6} {"macAddress":<20} {"type":<22} {"intf":<15} '
          f'{"moves":<6} {"lastMoveTime (seconds)"}')

    for batch in client.get(query):
        for notif in batch["notifications"]:
            updates = notif["updates"]

            for k, v in updates.items():
                mac_add = v["key"]["addr"]
                vlan = v["key"]["fid"]["value"]
                intf = v["intf"]
                moves = v["moves"]
                last_move = v["lastMoveTime"]
                mac_type = v["entryType"]["Name"]

                print(f'{vlan:<6} {mac_add:<20} {mac_type:<22} {intf:<15} {moves:<6} '
                      f'{last_move_time(last_move)}')

    return


def main(apiserverAddr, token=None, certs=None, key=None, ca=None):

    with GRPCClient(apiserverAddr, token=token, key=key,
                    ca=ca, certs=certs) as client:

        get_macs(client, args.device)

    return 0


if __name__ == "__main__":

    base.add_argument(
        "--device", type=str, help="device (by SerialNumber) to subscribe to"
    )
    args = base.parse_args()

    exit(main(args.apiserver, certs=args.certFile, key=args.keyFile,
              ca=args.caFile, token=args.tokenFile))
