# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
#
# Assign device tags on a device
#
# Example usage:
#  python itag.py --server 10.83.12.79:8443 --token-file token.txt \
#  --cert-file cvp.crt --device_id 99500CA623B639E85FE0E684862C7103 \
#  --tag_name "topology_hint_rack" \
# --tag_value "IE_Rack1"
#  python itag.py --server 10.83.12.79:8443 --token-file token.txt \
# --cert-file cvp.crt --device_id 99500CA623B639E85FE0E684862C7103 \
#  --tag_name "topology_hint_pod" --tag_value "IE_Pod1"


import argparse

import grpc

# import the tags models and services
from arista.tag.v1 import models
from arista.tag.v1 import services
from google.protobuf import wrappers_pb2 as wrappers

RPC_TIMEOUT = 30  # in seconds


def main(args):
    # read the file containing a session token to authenticate with
    token = args.token_file.read().strip()
    # create the header object for the token
    callCreds = grpc.access_token_call_credentials(token)

    # if using a self-signed certificate (should be provided as arg)
    if args.cert_file:
        # create the channel using the self-signed cert
        cert = args.cert_file.read()
        channelCreds = grpc.ssl_channel_credentials(root_certificates=cert)
    else:
        # otherwise default to checking against CAs
        channelCreds = grpc.ssl_channel_credentials()
    connCreds = grpc.composite_channel_credentials(channelCreds, callCreds)

    if args.device_id:
        device_id = args.device_id
    if args.tag_value:
        tag_value = args.tag_value
    if args.tag_name:
        tag_name = args.tag_name

    # initialize a connection to the server using our connection settings (auth + TLS)
    with grpc.secure_channel(args.server, connCreds) as channel:
        tag_stub = services.DeviceTagAssignmentConfigServiceStub(channel)
        req = services.DeviceTagAssignmentConfigSetRequest(
            value=models.DeviceTagAssignmentConfig(
                key=models.DeviceTagAssignmentKey(
                    label=wrappers.StringValue(value=tag_name),
                    value=wrappers.StringValue(value=tag_value),
                    device_id=wrappers.StringValue(value=device_id),
                )
            )
        )
        tag_stub.Set(req, timeout=RPC_TIMEOUT)


if __name__ == '__main__':
    ds = ("Assign a tag to an device."
          "Example:"
          "python3 itag.py --server 10.83.12.79:8443 --token-file token.txt \
            --cert-file cvp.crt --device_id 99500CA623B639E85FE0E684862C7103 \
            --tag_name \"topology_hint_pod\" \
            --tag_value \"IE_Pod1\""
          "python3 itag.py --server 10.83.12.79:8443 --token-file token.txt \
            --cert-file cvp.crt --device_id 99500CA623B639E85FE0E684862C7103 \
            --tag_name \"topology_hint_rach\" \
            --tag_value \"IE_Rack1\""
          )
    parser = argparse.ArgumentParser(
        description=ds,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--server',
        required=True,
        help="CloudVision server to connect to in <host>:<port> format")
    parser.add_argument("--device_id", required=True, help="Device SN")
    parser.add_argument("--tag_value", required=True, help="Value of the tag")
    parser.add_argument("--tag_name", required=True, help="Name of the tag"
                                                          "e.g.: topology_hint_pod")
    parser.add_argument("--token-file", required=True,
                        type=argparse.FileType('r'), help="file with access token")
    parser.add_argument("--cert-file", type=argparse.FileType('rb'),
                        help="certificate to use as root CA")
    args = parser.parse_args()
    main(args)
