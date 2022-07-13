# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
#
# Get tags per device per interface or all tags
# Example usage:
# 1) Get all tags:
#    python3 get_tags.py --server 10.83.12.79:443 --token-file token.txt \
#     --cert-file cvp.crt
#
# 2) Get all tags for a device:
#    python3 get_tags.py --server 10.83.12.79:443 --token-file token.txt \
#    --cert-file cvp.crt --device_id 99500CA623B639E85FE0E684862C7103
#
# 3) Get all tags for an interface of a device
#    python3 get_tags.py --server 10.83.12.79:443 --token-file token.txt \
#    --cert-file cvp.crt --device_id 99500CA623B639E85FE0E684862C7103 \
#    --interface_id Ethernet1
#
# 4) Get all interfaces that have a specific tag assigned:
#    python3 get_tags.py --server 10.83.12.79:443 --token-file token.txt \
#    --cert-file cvp.crt --device_id 99500CA623B639E85FE0E684862C7103 \
#    --tag_name 'lldp_chassis'
#
# 5) Get all interfaces that have a tag with a specific value:
#    python3 get_tags.py --server 10.83.12.79:443 --token-file token.txt \
#    --cert-file cvp.crt --device_id 99500CA623B639E85FE0E684862C7103 \
#    --tag_value 'forced'


import argparse

import grpc

# import the tags models and services
from arista.tag.v1 import models
from arista.tag.v1 import services

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

    # create a stream request
    get_all_req = services.InterfaceTagAssignmentConfigStreamRequest()

    tag_filter = models.InterfaceTagAssignmentConfig()

    if args.device_id:
        tag_filter.key.device_id.value = args.device_id

    if args.interface_id:
        tag_filter.key.interface_id.value = args.interface_id

    if args.tag_name:
        tag_filter.key.label.value = args.tag_name
    if args.tag_value:
        tag_filter.key.value.value = args.tag_value
    get_all_req.partial_eq_filter.append(tag_filter)

    # initialize a connection to the server using our connection settings (auth + TLS)
    with grpc.secure_channel(args.server, connCreds) as channel:
        tag_stub = services.InterfaceTagAssignmentConfigServiceStub(channel)
        print("Printing all tag assignments based on the filters:")
        for resp in tag_stub.GetAll(get_all_req, timeout=RPC_TIMEOUT):
            print(resp.value)


if __name__ == '__main__':
    ds = ("Get all interface tags matching a single filter.")
    parser = argparse.ArgumentParser(
        description=ds,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--server',
        required=True,
        help="CloudVision server to connect to in <host>:<port> format")
    parser.add_argument("--device_id", help="Device SN")
    parser.add_argument("--interface_id", help="Interface ID")
    parser.add_argument("--tag_name", help="Name of the tag, e.g.: lldp_chassis")
    parser.add_argument("--tag_value", help="Value of the tag, e.g:"
                        "Chassis MAC of neighbor in xx:xx:xx:xx:xx format")
    parser.add_argument("--token-file", required=True,
                        type=argparse.FileType('r'), help="file with access token")
    parser.add_argument("--cert-file", type=argparse.FileType('rb'),
                        help="certificate to use as root CA")
    args = parser.parse_args()
    main(args)
