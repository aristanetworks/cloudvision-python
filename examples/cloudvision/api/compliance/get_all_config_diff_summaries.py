#!/usr/bin/env python
# Copyright (c) 2026 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Print configuration compliance summaries for inventory devices."""

import argparse
import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit

from cloudvision.api import client as cv_client
from cloudvision.api.arista.inventory import v1 as inventory
from cloudvision.compliance import ComplianceClient

RPC_TIMEOUT = 30


def _server_parts(server):
    parsed = urlsplit(f"//{server}")
    if parsed.hostname is None:
        raise ValueError(f"invalid server: {server}")
    port = parsed.port or 443
    target_host = f"[{parsed.hostname}]" if ":" in parsed.hostname else parsed.hostname
    return parsed.hostname, port, f"{target_host}:{port}"


def _inventory_request(hostname, streaming_status):
    request = inventory.DeviceStreamRequest()
    filter_fields = {}
    if hostname:
        filter_fields["hostname"] = hostname
    if streaming_status:
        filter_fields["streaming_status"] = getattr(
            inventory.StreamingStatus, streaming_status.upper()
        )
    if filter_fields:
        request.partial_eq_filter.append(inventory.Device(**filter_fields))
    return request


async def _get_devices(server, token, cert_file, hostname, streaming_status):
    host, port, _ = _server_parts(server)
    client = cv_client.AsyncCVClient.from_token(
        token=token,
        host=host,
        port=port,
        cacert=cert_file,
    )
    request = _inventory_request(hostname, streaming_status)
    devices = []
    with client as channel:
        stub = inventory.DeviceServiceStub(channel)
        async for response in stub.get_all(request, timeout=RPC_TIMEOUT):
            device_id = response.value.key.device_id
            if device_id:
                devices.append((device_id, response.value.hostname or ""))
    return devices


def _compliance_text(value, error):
    if error:
        return "ERROR"
    if value is None:
        return "UNKNOWN"
    return "yes" if value else "no"


def _positive_int(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return value


def _get_summary(client, serial, hostname):
    return serial, hostname, client.get_config_diff_summary(serial)


async def main(args):
    token = args.token_file.read_text().strip()
    devices = await _get_devices(
        args.server,
        token,
        args.cert_file,
        args.hostname,
        args.streaming_status,
    )
    _, _, compliance_target = _server_parts(args.server)
    cert = args.cert_file.read_bytes() if args.cert_file else None

    print(
        f"{'Hostname':<25} {'Device serial':<32} {'In compliance':<15} "
        f"{'Add':>8} {'Delete':>8} {'Change':>8}"
    )
    with ComplianceClient(compliance_target, token, cert=cert) as client:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            futures = [
                loop.run_in_executor(executor, _get_summary, client, serial, hostname)
                for serial, hostname in devices
            ]
            for future in asyncio.as_completed(futures):
                serial, hostname, summary = await future
                error = summary.get("error", "")
                if error:
                    print(f"{serial}: {error}", file=sys.stderr)
                compliance = _compliance_text(summary.get("config_compliance"), error)
                print(
                    f"{hostname:<25} {serial:<32} {compliance:<15} "
                    f"{summary.get('add', 0):>8} "
                    f"{summary.get('delete', 0):>8} "
                    f"{summary.get('change', 0):>8}"
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=("Get configuration diff summaries for devices in inventory.")
    )
    parser.add_argument(
        "--server",
        required=True,
        help="CloudVision server in <host>[:<port>] format",
    )
    parser.add_argument(
        "--token-file",
        required=True,
        type=Path,
        help="file containing a CloudVision access token",
    )
    parser.add_argument(
        "--cert-file",
        type=Path,
        help="optional CA certificate used to verify the server",
    )
    parser.add_argument(
        "--hostname",
        help="only include the device with this hostname",
    )
    parser.add_argument(
        "--streaming-status",
        type=str.lower,
        choices=("active", "inactive"),
        help="only include devices with this streaming status",
    )
    parser.add_argument(
        "--concurrency",
        type=_positive_int,
        default=10,
        help="number of concurrent compliance requests (default: 10)",
    )
    asyncio.run(main(parser.parse_args()))
