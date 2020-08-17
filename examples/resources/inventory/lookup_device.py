#!/usr/bin/env python
# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

# Lookup a single device by serial or hostname.
# You can optionally provide both arguments which will assert both the
# serial and hostname match.

import argparse
import json
import grpc
import requests
from google.protobuf import wrappers_pb2 as wrappers

# import the inventory models and services
from arista.inventory.v1 import models
from arista.inventory.v1 import services

RPC_TIMEOUT = 30  # in seconds


def get_device_with_filter(stub, serial, hostname):
    """
    Fetch single device from the inventory by hostname (and optionally serial)
    The hostname argument is required in this case. If hostname was not
    provided then the lookup should be done by serial.
    """
    # create a stream request
    get_all_req = services.DeviceStreamRequest()

    # create an uninitialized key (nop), but set the serial if given
    device_key = None
    if serial is not None:
        device_key = models.DeviceKey(device_id=wrappers.StringValue(value=serial))

    # create the filter model with hostname and optional key set
    filt = models.Device(
        key=device_key,
        hostname=wrappers.StringValue(value=hostname)
    )

    # add the filter to the request
    get_all_req.partial_eq_filter.append(filt)

    # while we only expect one, we loop over everything streamed
    # this should be only one message, but you may want to do assertions
    for resp in stub.GetAll(get_all_req, timeout=RPC_TIMEOUT):
        print(resp)


def get_device_by_serial(stub, serial):
    """
    Fetch a single device from the inventory by serial number.
    """
    # create a unary device request, setting the key to the given serial
    req = services.DeviceRequest(
        key={"device_id": wrappers.StringValue(value=serial)}
    )
    # issue the request and print it
    resp = stub.GetOne(req)
    print(resp)


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

        if args.hostname:
            get_device_with_filter(stub, args.serial, args.hostname)
        else:
            get_device_by_serial(stub, args.serial)


if __name__ == '__main__':
    ds = ("Lookup a single device by serial, hostname, or require both.")
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
    parser.add_argument('--serial', type=str, help=("serial number of device to lookup"))
    parser.add_argument('--hostname', type=str, help=("hostname of device to lookup"))

    args = parser.parse_args()
    main(args)
