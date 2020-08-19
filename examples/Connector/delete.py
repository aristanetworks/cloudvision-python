# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from google.protobuf.timestamp_pb2 import Timestamp
from cloudvision.Connector.grpc_client import GRPCClient, create_notification
from parser import base


def main(apiserverAddr, dType, dId, path, dKey, token=None, cert=None,
         key=None, ca=None):
    ts = Timestamp()
    ts.GetCurrentTime()

    # Boilerplate values for dtype, sync, and compare
    sync = True
    compare = None

    pathElts = path.split("/")
    notifs = [create_notification(ts, pathElts, deletes=[dKey])]
    with GRPCClient(apiserverAddr, token=token, key=key,
                    certs=cert, ca=ca) as client:
        client.publish(dType, dId, sync, compare, notifs)
    return 0


if __name__ == "__main__":
    base.add_argument("--delKey", help="key to issue a delete for")
    base.add_argument("--path", help="path to issue a delete at", type=str)
    base.add_argument("--dType", help="dataset type to issue a delete for",
                      default="device", type=str)
    base.add_argument("--dId", help="dataset id to issue a delete for",
                      default="analytics", type=str)
    args = base.parse_args()

    exit(main(args.apiserver, args.dType, args.dId, args.path,
              args.delKey, cert=args.certFile, ca=args.caFile,
              key=args.keyFile, token=args.tokenFile))
