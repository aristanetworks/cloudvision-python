# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

# Subscribing to CVP events
#
# Examples:
# 1) Subscribe to all events
#    python sub_events.py --server 10.83.12.79:443 --token-file token.txt \
#    --cert-file cvp.crt
# 2) Subscribe to only DEVICE_INTF_ERR_SMART events
#    python sub_events.py --server 10.83.12.79:443 --token-file token.txt \
#    --cert-file cvp.crt --event-type DEVICE_INTF_ERR_SMART
# 3) Subscribe to events with INFO severity
#    python sub_events.py --server 10.83.12.79:443 --token-file token.txt \
#    --cert-file cvp.crt --severity INFO

import argparse

import grpc

# import the events models and services
from arista.event.v1 import models
from arista.event.v1 import services

RPC_TIMEOUT = 300  # in seconds
SEVERITIES = ["INFO", "WARNING", "ERROR", "CRITICAL"]


def main(args):
    # read the file containing a session token to authenticate with
    token = args.token_file.read().strip()
    # create the header object for the token
    callCreds = grpc.access_token_call_credentials(token)

    # if using a self-signed certificate (should be provided as arg)
    if args.cert_file:
        cert = args.cert_file.read()
        channelCreds = grpc.ssl_channel_credentials(root_certificates=cert)
    else:
        # otherwise default to checking against CAs
        channelCreds = grpc.ssl_channel_credentials()
    connCreds = grpc.composite_channel_credentials(channelCreds, callCreds)
    # create a stream request
    subscribe = services.EventStreamRequest()

    # create a filter model
    event_filter = models.Event()

    if args.event_type:
        event_filter.event_type.value = args.event_type

    if args.severity:
        # enum with val 0 is always unset
        event_filter.severity = SEVERITIES.index(args.severity) + 1
    subscribe.partial_eq_filter.append(event_filter)
    # initialize a connection to the server using our connection settings (auth + TLS)
    with grpc.secure_channel(args.server, connCreds) as channel:
        event_stub = services.EventServiceStub(channel)
        for resp in event_stub.Subscribe(subscribe, timeout=RPC_TIMEOUT):
            print(resp.value)
            print("\n")


if __name__ == '__main__':
    ds = ("Subscribe to CVP events. "
          "Examples:\n"
          "1) Subscribe to all events:\n"
          "\tpython sub_events.py --server 10.83.12.79:443 --token-file token.txt"
          "--cert-file cvp.crt\n"
          "2) Subscribe to only DEVICE_INTF_ERR_SMART events\n"
          "\tpython sub_events.py --server 10.83.12.79:443 --token-file token.txt"
          "--cert-file cvp.crt --event-type DEVICE_INTF_ERR_SMART\n"
          "3) Subscribe to events with INFO severity:\n"
          "\tpython sub_events.py --server 10.83.12.79:443 --token-file token.txt"
          "--cert-file cvp.crt --severity INFO")
    parser = argparse.ArgumentParser(
        description=ds,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--server',
        required=True,
        help="CloudVision server to connect to in <host>:<port> format")
    parser.add_argument("--event-type", help="get events of this type only")
    parser.add_argument("--severity",
                        help="get events of this severity only",
                        choices=SEVERITIES)
    parser.add_argument("--token-file", required=True,
                        type=argparse.FileType('r'), help="file with access token")
    parser.add_argument("--cert-file", type=argparse.FileType('rb'),
                        help="certificate to use as root CA")
    args = parser.parse_args()
    main(args)
