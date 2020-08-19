# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from cloudvision.Connector.grpc_client import GRPCClient, create_query
from utils import pretty_print
from parser import base


def main(apiserverAddr, dId, intfId, token=None, cert=None, key=None, ca=None):
    pathElts = [
        "Devices",
        dId,
        "versioned-data",
        "interfaces",
        "data",
        intfId,
        "rates",
    ]
    query = [
        create_query([(pathElts, ["outOctets"])], "analytics")
    ]

    with GRPCClient(apiserverAddr, token=token, certs=cert, key=key,
                    ca=ca) as client:
        for batch in client.subscribe(query):
            for notif in batch["notifications"]:
                pretty_print(notif["updates"])
    return 0


if __name__ == "__main__":
    base.add_argument("--device", type=str, help="device to subscribe to")
    base.add_argument("--interface", type=str, help="interface to subscribe to")
    args = base.parse_args()

    exit(main(args.apiserver, args.device, args.interface, ca=args.caFile,
              cert=args.certFile, key=args.keyFile, token=args.tokenFile))
