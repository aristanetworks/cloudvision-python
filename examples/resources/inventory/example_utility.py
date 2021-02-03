#!/usr/bin/env python
# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

# Example utility to read from the inventory.
# Allows reading all devices, only active devices, only inactive devices,
# or looking up a single device by serial.
#
# Active filter takes priority over inactive, and the GetAll takes priority
# over the single-device path.

import argparse
import json
import grpc
import requests
from google.protobuf import wrappers_pb2 as wrappers

# import the inventory models and services
from arista.inventory.v1 import models
from arista.inventory.v1 import services

RPC_TIMEOUT = 30  # in seconds


def get_all(stub, only_active, only_inactive):
    """
    Prints the hostname of all devices known to the system.
    Optionally filters based on the only_active and only_inactive arguments.
    When filtering, only_active takes priority to only_inactive if both are set.
    """
    # create a stream request
    get_all_req = services.DeviceStreamRequest()

    # add filter to the request if needed
    if only_active:
        # must match a Device where streaming_status = ACTIVE
        get_all_req.partial_eq_filter.append(models.Device(
            streaming_status=models.STREAMING_STATUS_ACTIVE,
        ))
    elif only_inactive:
        # must match a Device where streaming_status = INACTIVE
        get_all_req.partial_eq_filter.append(models.Device(
            streaming_status=models.STREAMING_STATUS_INACTIVE,
        ))

    total_devices = 0
    # make the GetAll request and loop over the streamed responses
    for resp in stub.GetAll(get_all_req, timeout=RPC_TIMEOUT):
        # print {hostname}: {serial}
        print(f"{resp.value.hostname.value:<25}{resp.value.key.device_id.value:<25}")
        total_devices += 1
    print("{} matching devices in inventory".format(total_devices))


def get_one(stub, serial):
    """
    Fetch a single device from the inventory by serial number.
    """
    # create a unary device request, setting the key to the given serial
    req = services.DeviceRequest(
        key={"device_id": wrappers.StringValue(value=serial)}
    )
    # issue the request and print it
    resp = stub.GetOne(req)
    print("{}:{}".format(args.device, resp))


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

    # create channel settings (auth + TLS)
    connCreds = grpc.composite_channel_credentials(channelCreds, callCreds)

    # initialize a connection to the server using our connection settings (auth + TLS)
    with grpc.secure_channel(args.server, connCreds) as channel:
        # create the Python stub for the inventory API
        # this is essentially the client, but Python gRPC refers to them as "stubs"
        # because they call into the gRPC C API
        stub = services.DeviceServiceStub(channel)

        # call the method based on args -- giving a serial overrides active/inactive
        if args.device is None:
            get_all(stub, args.active, args.inactive)
        else:
            get_one(stub, args.device)


if __name__ == '__main__':
    ds = ("Get devices in inventory.")
    parser = argparse.ArgumentParser(
        description=ds,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--server',
        required=True,
        help="CloudVision server to connect to in <host>:<port> format")
    parser.add_argument("--token-file", required=True,
                        type=argparse.FileType('r'), help="file with access token")
    parser.add_argument("--cert-file", type=argparse.FileType('rb'),
                        help="certificate to use as root CA")
    parser.add_argument('--device', type=str, help=("get a single device by serial number"))
    parser.add_argument('--active', action='store_true',
                        help=("get only actively streaming devices"))
    parser.add_argument('--inactive', action='store_true',
                        help=("get only non-actively streaming devices"))

    args = parser.parse_args()
    main(args)
