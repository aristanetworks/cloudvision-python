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
import asyncio

# import the inventory models and services
from cloudvision.api.arista.inventory import v1 as inventory
from cloudvision.api import client as cv_client

RPC_TIMEOUT = 30  # in seconds


async def get_all(stub, only_active, only_inactive):
    """
    Prints the hostname of all devices known to the system.
    Optionally filters based on the only_active and only_inactive arguments.
    When filtering, only_active takes priority to only_inactive if both are set.
    """
    # create a stream request
    get_all_req = inventory.DeviceStreamRequest()

    # add filter to the request if needed
    if only_active:
        # must match a Device where streaming_status = ACTIVE
        get_all_req.partial_eq_filter.append(inventory.Device(
            streaming_status=inventory.StreamingStatus.ACTIVE,
        ))
    elif only_inactive:
        # must match a Device where streaming_status = INACTIVE
        get_all_req.partial_eq_filter.append(inventory.Device(
            streaming_status=inventory.StreamingStatus.INACTIVE,
        ))

    total_devices = 0
    # make the GetAll request and loop over the streamed responses
    async for resp in stub.get_all(get_all_req, timeout=RPC_TIMEOUT):
        # print {hostname}: {serial}
        print(f"{resp.value.hostname:<25}{resp.value.key.device_id:<25}")
        total_devices += 1
    print("{} matching devices in inventory".format(total_devices))


async def get_one(stub, serial):
    """
    Fetch a single device from the inventory by serial number.
    """
    # create a unary device request, setting the key to the given serial
    req = inventory.DeviceRequest(
        key={"device_id": serial}
    )
    # issue the request and print it
    resp = await stub.get_one(req)
    print("{}:{}".format(args.device, resp))


async def main(args):
    # read the file containing a session token to authenticate with
    token = args.token_file.read().strip()
    client = cv_client.AsyncCVClient.from_token(token, host=args.server)
    # initialize a connection to the server using our connection settings (auth + TLS)
    with client as channel:
        # create the Python stub for the inventory API
        # this is essentially the client, but Python gRPC refers to them as "stubs"
        # because they call into the gRPC C API
        stub = inventory.DeviceServiceStub(channel)

        # call the method based on args -- giving a serial overrides active/inactive
        if args.device is None:
            await get_all(stub, args.active, args.inactive)
        else:
            await get_one(stub, args.device)


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

    parser.add_argument('--device', type=str, help=("get a single device by serial number"))
    parser.add_argument('--active', action='store_true',
                        help=("get only actively streaming devices"))
    parser.add_argument('--inactive', action='store_true',
                        help=("get only non-actively streaming devices"))

    args = parser.parse_args()
    asyncio.run(main(args))
