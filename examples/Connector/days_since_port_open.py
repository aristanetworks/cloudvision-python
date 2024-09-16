# Copyright (c) 2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from datetime import datetime
from enum import Enum
from typing import List, Dict
from dataclasses import dataclass, field

from cloudvision.Connector.codec import Wildcard
from cloudvision.Connector.grpc_client import GRPCClient
from cloudvision.Connector.grpc_client import create_query

from parser import base


HEADERS = ["Hostname", "Interface", "Days out of Sync"]


class AdminState(str, Enum):
    SHUTDOWN = "shutdown"
    ENABLED = "enabled"
    UNKNOWN = ""


class OperationalState(str, Enum):
    NOT_PRESNET = "intfOperNotPresent"
    DOWN = "intfOperDown"
    UP = "intfOperUp"


@dataclass
class PortInfo:
    interface: str
    operational_status: str
    operational_status_date: datetime
    admin_status: str = ""
    admin_status_date: datetime | None = None


@dataclass
class DeviceInfo:
    hostname: str
    serial_number: str
    port_info: Dict[str, PortInfo] = field(default_factory=dict)
    line_cards: List[str] = field(default_factory=list)


MIN_DAYS_OF_DIFF = 0


def get_device_line_cards(client: GRPCClient, device) -> None:
    query = [
        create_query(
            [(["Sysdb", "interface", "status", "eth", "phy", "slice"], [])],
            device.serial_number,
        )
    ]

    result = {}
    for batch in client.get(query):
        for notif in batch["notifications"]:
            result.update(notif["updates"])
    device.line_cards = list(result.keys())


def get_operational_state(client: GRPCClient, device: DeviceInfo) -> None:
    for line_card in device.line_cards:
        query = [
            create_query(
                [
                    (
                        [
                            "Sysdb",
                            "interface",
                            "status",
                            "eth",
                            "phy",
                            "slice",
                            line_card,
                            "intfStatus",
                            Wildcard(),
                        ],
                        ["operStatus"],
                    )
                ],
                device.serial_number,
            )
        ]

        for batch in client.get(query):
            for notif in batch["notifications"]:
                interface = str(notif["path_elements"][-1])
                device.port_info[interface] = PortInfo(
                    interface=interface,
                    operational_status=notif["updates"]["operStatus"]["Name"],
                    operational_status_date=notif["timestamp"].ToDatetime(),
                )


def get_update_admin_state(client: GRPCClient, device: DeviceInfo) -> None:
    for line_card in device.line_cards:
        query = [
            create_query(
                [
                    (
                        [
                            "Sysdb",
                            "interface",
                            "config",
                            "eth",
                            "phy",
                            "slice",
                            line_card,
                            "intfConfig",
                            Wildcard(),
                        ],
                        ["enabledStateLocal"],
                    )
                ],
                device.serial_number,
            )
        ]

        for batch in client.get(query):
            for notif in batch["notifications"]:
                interface = str(notif["path_elements"][-1])
                device.port_info[interface].admin_status = notif["updates"][
                    "enabledStateLocal"
                ]["Name"]
                device.port_info[interface].admin_status_date = notif[
                    "timestamp"
                ].ToDatetime()


def get_devices(client) -> List[DeviceInfo]:
    """Retrieves devices from analytics dataset"""
    query = [create_query([(["DatasetInfo", "Devices"], [])], "analytics")]

    devices = []
    for batch in client.get(query):
        for notif in batch["notifications"]:
            serial = list(notif["updates"])[0]
            hostname = notif["updates"][serial]["hostname"]
            devices.append(DeviceInfo(hostname=hostname, serial_number=serial))
    return devices


def print_out_of_sync_ports(devices: List[DeviceInfo]):
    current_date = datetime.now()
    for device in devices:
        print(f"\n{device.hostname}")
        print("Interface           Out Of Sync Days")
        for interface in device.port_info.values():
            if interface.admin_status.lower() == AdminState.SHUTDOWN.lower():
                continue
            out_of_sync_state = (
                interface.operational_status.lower() != OperationalState.UP.lower()
                and interface.admin_status.lower() == AdminState.ENABLED.lower()
            )
            if not out_of_sync_state:
                continue
            if not interface.admin_status_date:
                continue
            operational_state_out_of_sync = (
                current_date - interface.operational_status_date
            ).days
            admin_state_out_of_sync = (current_date - interface.admin_status_date).days
            out_of_sync_days = min(
                operational_state_out_of_sync, admin_state_out_of_sync
            )
            if out_of_sync_days >= MIN_DAYS_OF_DIFF:
                print(f"{interface.interface:<20}{out_of_sync_days:<5}")


def main(cvp_url, token=None, certs=None, ca=None, key=None):
    with GRPCClient(cvp_url, token=token, key=key, ca=ca, certs=certs) as client:
        devices = get_devices(client)
        for device in devices:
            get_device_line_cards(client=client, device=device)
            get_operational_state(client=client, device=device)
            get_update_admin_state(client=client, device=device)
        print_out_of_sync_ports(devices)
    return 0


if __name__ == "__main__":
    args = base.parse_args()
    exit(
        main(
            args.apiserver,
            token=args.tokenFile,
            certs=args.certFile,
            ca=args.caFile,
        )
    )
