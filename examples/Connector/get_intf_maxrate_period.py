# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
from datetime import datetime, timedelta
from google.protobuf.timestamp_pb2 import Timestamp
from cloudvision.Connector.grpc_client import GRPCClient, create_query
from utils import pretty_print
from parser import base


def main(apiserverAddr, dId, intfId, token=None, cert=None, key=None, ca=None, days=0, hours=1,
         minutes=0):

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

    pathElts = [
        "Devices",
        dId,
        "versioned-data",
        "interfaces",
        "data",
        intfId,
        "aggregate",
        "rates",
        "15m"
    ]

    query = [
        create_query([(pathElts, ["inOctets", "outOctets"])], "analytics")
    ]

    with GRPCClient(apiserverAddr, token=token, certs=cert, key=key,
                    ca=ca) as client:
        maxTx = 0
        maxRx = 0
        for batch in client.get(query, start=start, end=end):
            for notif in batch["notifications"]:
                if maxTx < int(notif["updates"]["outOctets"]["max"]) * 8 / 1000000:
                    maxTx = int(notif["updates"]["outOctets"]["max"]) * 8 / 1000000
                if maxRx < int(notif["updates"]["inOctets"]["max"]) * 8 / 1000000:
                    maxRx = int(notif["updates"]["inOctets"]["max"]) * 8 / 1000000
        print("Max Tx (Mbps) is: ", maxTx)
        print("Max Rx (Mbps) is: ", maxRx)
    return 0


if __name__ == "__main__":
    base.add_argument("--device", type=str, help="device to subscribe to")
    base.add_argument("--interface", type=str, help="interface to subscribe to")
    base.add_argument("--start", required=False,
                      help=("Start time of the lookup in ISO format,"
                            "e.g.: 2021-02-02T21:46:00"))
    base.add_argument("--end", required=False,
                      help=("End time of the lookup in ISO format,"
                            "e.g.: 2021-02-02T21:46:00"))
    args = base.parse_args()
    exit(main(args.apiserver, args.device, args.interface, ca=args.caFile,
              cert=args.certFile, key=args.keyFile, token=args.tokenFile))
