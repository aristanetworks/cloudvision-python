# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec import Wildcard
from utils import pretty_print
from parser import base


def main(apiserverAddr, dId, token=None, certs=None, ca=None, key=None):
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
        create_query([(pathElts, ["linkStatus"])], dId)
    ]

    intfStat = []

    with GRPCClient(apiserverAddr, token=token, key=key, ca=ca, certs=certs) as client:
        for batch in client.get(query):
            for notif in batch["notifications"]:
                intfStat.append({"interface": notif['path_elements'][-1],
                                 "Status": notif['updates']['linkStatus']['Name']})
    print(f"{'Interface Name':<25}{'Status'}\n")
    for interface in intfStat:
        print(f"{interface['interface']:<25}{interface['Status']}")

    return 0


if __name__ == "__main__":
    base.add_argument("--deviceId",
                      help="device id/serial number to query intfStatus for")
    args = base.parse_args()

    exit(main(args.apiserver, args.deviceId, token=args.tokenFile,
              certs=args.certFile, ca=args.caFile))
