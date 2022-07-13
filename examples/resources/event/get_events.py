# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

# Get CVP events
# Acknowledges selected CVP events if the --ack flag is set.
# Acknowledging a CVP event hides the event from the default view.
#
# Examples:
# 1) Get all events:
#   $ python get_events.py --server 10.83.12.79:443 \
#   --token-file token.txt \
#   --cert-file cvp.crt \
# 2) Get all events after date:
#   $ python get_events.py --server 10.83.12.79:443 \
#   --token-file token.txt \
#   --cert-file cvp.crt \
#   --start 2020-02-20T00:00:01.000000001Z
# 3) Get all INSUFFICIENT_PEER_LAG_REDUNDANCY events between two dates:
#   $ python get_events.py --server 10.83.12.79:443 \
#   --token-file token.txt \
#   --cert-file cvp.crt \
#   --event-type INSUFFICIENT_PEER_LAG_REDUNDANCY \
#   --start 2020-02-20T00:00:01.000000001Z \
#   --end 2020-02-21T00:00:01.000000001Z
# 4) Get all INSUFFICIENT_PEER_LAG_REDUNDANCY events between two dates
#   and acknowledge them:
#   $ python get_events.py --server 10.83.12.79:443 \
#   --token-file token.txt \
#   --cert-file cvp.crt \
#   --event-type INSUFFICIENT_PEER_LAG_REDUNDANCY \
#   --start 2020-02-20T00:00:01.000000001Z \
#   --end 2020-02-21T00:00:01.000000001Z \
#   --ack
# 5) Get all events with INFO severity:
#   $ python get_events.py --server 10.83.12.79:443 \
#   --token-file token.txt \
#   --cert-file cvp.crt \
#   --severity INFO
import argparse

import grpc

# import the events models and services
from arista.event.v1 import models
from arista.event.v1 import services

RPC_TIMEOUT = 30  # in seconds
SEVERITIES = ["INFO", "WARNING", "ERROR", "CRITICAL"]


def main(args):
    token = args.token_file.read().strip()
    callCreds = grpc.access_token_call_credentials(token)

    if args.cert_file:
        cert = args.cert_file.read()
        channelCreds = grpc.ssl_channel_credentials(root_certificates=cert)
    else:
        channelCreds = grpc.ssl_channel_credentials()
    connCreds = grpc.composite_channel_credentials(channelCreds, callCreds)

    get_all_req = services.EventStreamRequest()

    if args.end and not args.start:
        raise ValueError("--start must be specified when --end is specified")

    if args.start:
        if args.start.isdigit():
            get_all_req.time.start.FromNanoseconds(int(args.start))
        else:
            get_all_req.time.start.FromJsonString(args.start)
        # set end to current time in case end is not specified
        get_all_req.time.end.GetCurrentTime()

    if args.end:
        if args.end.isdigit():
            get_all_req.time.end.FromNanoseconds(int(args.end))
        else:
            get_all_req.time.end.FromJsonString(args.end)

    event_filter = models.Event()

    if args.event_type:
        event_filter.event_type.value = args.event_type

    if args.severity:
        # enum with val 0 is always unset
        event_filter.severity = SEVERITIES.index(args.severity) + 1

    get_all_req.partial_eq_filter.append(event_filter)
    print(f"selecting events that match the filter {get_all_req}")

    with grpc.secure_channel(args.server, connCreds) as channel:
        event_stub = services.EventServiceStub(channel)
        event_ack_stub = services.EventAnnotationConfigServiceStub(channel)
        for resp in event_stub.GetAll(get_all_req, timeout=RPC_TIMEOUT):
            print(f"{resp}")
            if args.ack and not resp.value.ack.ack.value:
                print("acking event")
                req = services.EventAnnotationConfigSetRequest(
                    value=models.EventAnnotationConfig(
                        key=resp.value.key,
                    )
                )
                req.value.ack.value = True
                event_ack_stub.Set(req, timeout=RPC_TIMEOUT)


if __name__ == '__main__':
    ds = ("Get CVP events. "
          "Acknowledges selected CVP events if the --ack flag is set. "
          "Acknowledging a CVP event hides the event from the default view. "
          "Examples:\n"
          "1) Get all events:\n"
          "\tpython get_events.py --server 10.83.12.79:443 "
          "--token-file token.txt --cert-file cvp.crt\n"
          "2) Get all events after date:\n"
          "\tpython get_events.py --server 10.83.12.79:443 "
          "--token-file token.txt --cert-file cvp.crt "
          "--start 2020-02-20T00:00:01.000000001Z\n"
          "3) Get all INSUFFICIENT_PEER_LAG_REDUNDANCY events between "
          "two dates:\n"
          "\tpython get_events.py --server 10.83.12.79:443 "
          "--token-file token.txt --cert-file cvp.crt --event-type "
          "INSUFFICIENT_PEER_LAG_REDUNDANCY --start 2020-02-20T00:00:01.000000001Z "
          "--end 2020-02-21T00:00:01.000000001Z\n"
          "4) Get all INSUFFICIENT_PEER_LAG_REDUNDANCY events between "
          "two dates and acknowledge them:\n"
          "\tpython get_events.py --server 10.83.12.79:443 "
          "--token-file token.txt --cert-file cvp.crt --event-type "
          "INSUFFICIENT_PEER_LAG_REDUNDANCY --start 2020-02-20T00:00:01.000000001Z "
          "--end 2020-02-21T00:00:01.000000001Z --ack\n"
          "5) Get all events with INFO severity:\n"
          "\tpython get_events.py --server 10.83.12.79:443"
          "--token-file token.txt --cert-file cvp.crt --severity INFO")
    parser = argparse.ArgumentParser(
        description=ds,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--server',
        required=True,
        help="CloudVision server to connect to in <host>:<port> format")
    parser.add_argument('--start',
                        help=("select events after this time. "
                              "RFC3339 date string or Unix nanosecond timestamp."))
    parser.add_argument('--end',
                        help=("select events before this time. "
                              "RFC3339 date string or Unix nanosecond timestamp. "
                              "Must also provide start time argument"))
    parser.add_argument("--event-type", help="select events of this type only")
    parser.add_argument("--severity",
                        help="select events of this severity only",
                        choices=SEVERITIES)
    parser.add_argument("--ack",
                        help="acknowledge selected events",
                        action='store_true',
                        default=False)
    parser.add_argument("--token-file", required=True,
                        type=argparse.FileType('r'), help="file with access token")
    parser.add_argument("--cert-file", type=argparse.FileType('rb'),
                        help="certificate to use as root CA")
    args = parser.parse_args()
    main(args)
