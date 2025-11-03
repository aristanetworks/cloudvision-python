#!/usr/bin/env python
# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

# Iterates the inventory and prints a map of EOS version to the number
# of devices running that version.

import argparse
import asyncio
# import the inventory models and services
from cloudvision.api import client as cv_client
from cloudvision.api.arista.inventory import v1 as inventory

RPC_TIMEOUT = 30  # in seconds


async def get_device_with_filter(stub, serial, hostname):
    """
    Fetch single device from the inventory by hostname (and optionally serial)
    The hostname argument is required in this case. If hostname was not
    provided then the lookup should be done by serial.
    """
    # create a stream request
    get_all_req = inventory.DeviceStreamRequest()

    # create an uninitialized key (nop), but set the serial if given
    device_key = None
    if serial is not None:
        device_key = inventory.DeviceKey(device_id=serial)

    # create the filter model with hostname and optional key set
    filt = inventory.Device(
        key=device_key,
        hostname=hostname
    )

    # add the filter to the request
    get_all_req.partial_eq_filter.append(filt)

    # while we only expect one, we loop over everything streamed
    # this should be only one message, but you may want to do assertions
    async for resp in stub.get_all(get_all_req, timeout=RPC_TIMEOUT):
        print(f"{resp.value.hostname:<25}{resp.value.software_version:<25}")


async def main(args):
    # read the file containing a session token to authenticate with
    token = args.token_file.read().strip()

    client = cv_client.AsyncCVClient.from_token(token=token, host=args.server)

    # create channel settings (auth + TLS)
    get_all_req = inventory.DeviceStreamRequest()

    # filter on actively streaming devices only
    # if not(args.hostname or args.serial):
    get_all_req.partial_eq_filter.append(inventory.Device(
        streaming_status=inventory.StreamingStatus.ACTIVE,
    ))
    devices = []
    # initialize a connection to the server using our connection settings (auth + TLS)
    with client as channel:
        # create the Python stub for the inventory API
        # this is essentially the client, but Python gRPC refers to them as "stubs"
        # because they call into the gRPC C API
        stub = inventory.DeviceServiceStub(channel)
        print(f"{'Hostname':<25}{'EOS Version'}\n")
        # iterate all devices
        if args.hostname or args.serial:
            await get_device_with_filter(stub, args.serial, args.hostname)
        else:
            async for resp in stub.get_all(get_all_req, timeout=RPC_TIMEOUT):
                hostname = resp.value.hostname
                ver = resp.value.software_version
                devices.append({"hostname": hostname, "version": ver})

    for device in devices:
        print(f"{device['hostname']:<25}{device['version']:<25}")


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
    parser.add_argument('--serial', type=str, help=("serial number of device to lookup"))
    parser.add_argument('--hostname', type=str, help=("hostname of device to lookup"))

    args = parser.parse_args()
    asyncio.run(main(args))
