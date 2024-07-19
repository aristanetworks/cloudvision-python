# Copyright (c) 2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
#
# Get tags per device per interface or all tags
# Example usage:
# 1) Get all tags:
#    python3 get_tags.py --server 192.0.279:443 --token-file token.txt \
#     --cert-file cvp.crt
#
# 2) Get all tags for a device:
#    python3 get_tags.py --server 192.0.279:443 --token-file token.txt \
#    --cert-file cvp.crt --device-id 99500CA623B639E85FE0E684862C7103
#
# 3) Get all tags for an interface of a device
#    python3 get_tags.py --server 192.0.279:443 --token-file token.txt \
#    --cert-file cvp.crt --device 99500CA623B639E85FE0E684862C7103 \
#    --interface_id Ethernet1
#
# 4) Get all interfaces that have a specific tag assigned:
#    python3 get_tags.py --server 192.0.279:443 --token-file token.txt \
#    --cert-file cvp.crt --device 99500CA623B639E85FE0E684862C7103 \
#    --tag-label 'lldp_chassis' --tag-type 2
#
# 5) Get all interfaces that have a tag with a specific value:
#    python3 get_tags.py --server 192.0.279:443 --token-file token.txt \
#    --cert-file cvp.crt --device 99500CA623B639E85FE0E684862C7103 \
#    --tag-value 'forced' --tag-type 2


import argparse
import grpc
import json
import arista.tag.v2
from google.protobuf.json_format import Parse

RPC_TIMEOUT = 30  # in seconds


def main(args):
    # Read the file containing a session token to authenticate with
    token = args.token_file.read().strip()
    # Create the header object for the token
    callCreds = grpc.access_token_call_credentials(token)

    # If using a self-signed certificate (should be provided as arg)
    if args.cert_file:
        # Create the channel using the self-signed cert
        cert = args.cert_file.read()
        channelCreds = grpc.ssl_channel_credentials(root_certificates=cert)
    else:
        # Otherwise default to checking against CAs
        channelCreds = grpc.ssl_channel_credentials()

    connCreds = grpc.composite_channel_credentials(channelCreds, callCreds)

    # Construct the json_request based on provided arguments
    request_dict = {}
    if any([args.device_id, args.interface_id, args.tag_label, args.tag_value]):
        if args.tag_type:
            filter_dict = {"elementType": int(args.tag_type)}
        else:
            filter_dict = {"elementType": 1}
        if args.tag_label:
            filter_dict["label"] = args.tag_label
        if args.tag_value:
            filter_dict["value"] = args.tag_value
        if args.device_id:
            filter_dict["deviceId"] = args.device_id
        if args.interface_id:
            filter_dict["interfaceId"] = args.interface_id
            filter_dict["elementType"] = 2

        request_dict["partialEqFilter"] = [{"key": filter_dict}]

    json_request = json.dumps(request_dict)

    req = Parse(json_request, arista.tag.v2.services.TagAssignmentStreamRequest(), False)

    # Initialize a connection to the server using our connection settings (auth + TLS)
    with grpc.secure_channel(args.server, connCreds) as channel:
        tag_stub = arista.tag.v2.services.TagAssignmentServiceStub(channel)
        print(list(tag_stub.GetAll(req, timeout=RPC_TIMEOUT)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--server", required=True, help="CloudVision server to connect to in <host>:<port> format"
    )
    parser.add_argument(
        "--token-file", required=True, type=argparse.FileType("r"), help="file with access token"
    )
    parser.add_argument(
        "--cert-file", type=argparse.FileType("rb"), help="certificate to use as root CA"
    )

    # New arguments
    parser.add_argument("--device-id", help="Device ID for the filter")
    parser.add_argument("--interface-id", help="Interface ID for the filter")
    parser.add_argument("--tag-label", help="Tag name (label) for the filter")
    parser.add_argument("--tag-value", help="Tag value for the filter")
    parser.add_argument(
        "--tag-type",
        help="type of tag to filter on, 1 for device, 2 for interface",
        choices=["1", "2"],
    )
    args = parser.parse_args()
    main(args)
