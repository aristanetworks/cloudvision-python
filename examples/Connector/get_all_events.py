# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from datetime import datetime, timedelta
from google.protobuf.timestamp_pb2 import Timestamp
from cloudvision.Connector.grpc_client import GRPCClient, create_query
from utils import pretty_print
from parser import base


def main(apiserverAddr, token=None, cert=None, key=None, ca=None,
         days=0, hours=1, minutes=0):
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
        "events",
        "activeEvents"
    ]
    query = [
        create_query([(pathElts, [])], "analytics")
    ]

    with GRPCClient(apiserverAddr, certs=cert, key=key,
                    token=token, ca=ca) as client:
        for batch in client.get(query, start=start, exact_range=args.exact_range):
            for notif in batch["notifications"]:
                pretty_print(notif["updates"])
    return 0


if __name__ == "__main__":
    base.add_argument("--start", required=False,
                      help=("Start time of the lookup in ISO format,"
                            "e.g.: 2021-02-02T21:46:00"))
    base.add_argument("--end", required=False,
                      help=("End time of the lookup in ISO format,"
                            "e.g.: 2021-02-02T21:46:00"))
    base.add_argument("--exact_range", type=bool, default=False,
                      help=("When exact_range is set in addition to 'start' and "
                            " 'end' time, only events that started after 'start' time "
                            "and ended before 'end' time will be queried, otherwise "
                            "events that started before the 'start' time but "
                            "were still active will be presented as well."))
    args = base.parse_args()
    # Edit time range for events here
    exit(main(args.apiserver, cert=args.certFile,
              key=args.keyFile, token=args.tokenFile, ca=args.caFile))
