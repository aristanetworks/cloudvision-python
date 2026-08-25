# Copyright (c) 2026 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Synchronous client wrapper for the CloudVision Compliance service."""

import os
from datetime import datetime, timezone

import grpc
from google.protobuf.timestamp_pb2 import Timestamp

from cloudvision.compliance.gen import compliancecheck_pb2 as pb2
from cloudvision.compliance.gen import compliancecheck_pb2_grpc as pb2_grpc

RPC_TIMEOUT = 120

DIFF_OP_NAMES = {
    pb2.DIFFOP_UNSPECIFIED: "UNSPECIFIED",
    pb2.NOP: "NOP",
    pb2.IGNORE: "IGNORE",
    pb2.ADD: "ADD",
    pb2.DELETE: "DELETE",
    pb2.CHANGE: "CHANGE",
}


def _parse_timestamp(value):
    """Convert an ISO-8601 string to a protobuf timestamp."""
    if value is None:
        return None
    if isinstance(value, Timestamp):
        return value
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    timestamp = Timestamp()
    timestamp.FromDatetime(parsed)
    return timestamp


def _create_channel(server, token, cert=None):
    """Create an authenticated, TLS-protected gRPC channel."""
    # Prefer the native resolver when a connection is created. This avoids
    # c-ares resolver issues seen on macOS without mutating the environment
    # merely by importing the library.
    os.environ.setdefault("GRPC_DNS_RESOLVER", "native")
    call_creds = grpc.access_token_call_credentials(token)
    if cert:
        channel_creds = grpc.ssl_channel_credentials(root_certificates=cert)
    else:
        channel_creds = grpc.ssl_channel_credentials()
    conn_creds = grpc.composite_channel_credentials(channel_creds, call_creds)
    return grpc.secure_channel(server, conn_creds)


class ComplianceClient:
    """Wrapper around the synchronous Compliance gRPC service."""

    def __init__(self, server, token, cert=None, timeout=RPC_TIMEOUT):
        self.channel = _create_channel(server, token, cert)
        self.stub = pb2_grpc.ComplianceStub(self.channel)
        self.timeout = timeout

    def close(self):
        """Close the underlying gRPC channel."""
        self.channel.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def get_config(self, device_id, config_type=pb2.RUNNING_CONFIG, timestamp=None):
        """Retrieve the running configuration for a device."""
        config_request = pb2.ConfigRequest(type=config_type, device_id=device_id)
        parsed_timestamp = _parse_timestamp(timestamp)
        if parsed_timestamp:
            config_request.timestamp.CopyFrom(parsed_timestamp)
        request = pb2.GetConfigRequest(request=config_request)

        result = {
            "config": "",
            "errors": [],
            "filter_codes": [],
            "sources": [],
        }
        try:
            for response in self.stub.GetConfig(request, timeout=self.timeout):
                response_type = response.WhichOneof("response")
                if response_type == "config":
                    result["config"] += response.config
                elif response_type == "error":
                    result["errors"].append(response.error.error_msg)
                elif response_type == "configFilterCodes":
                    for filter_code in response.configFilterCodes.inLineFilterCode:
                        result["filter_codes"].append(
                            {
                                "line_no": filter_code.lineNo,
                                "filter_code": filter_code.filterCode,
                            }
                        )
                elif response_type == "sources":
                    for source in response.sources.source:
                        result["sources"].append(
                            {
                                "source_type": source.source_type,
                                "key": source.key,
                            }
                        )
        except grpc.RpcError as error:
            result["errors"].append(f"gRPC error: {error.details()}")
        return result

    def get_config_diff(
        self,
        device_id,
        timestamp=None,
        lhs_type=pb2.DESIGNED_CONFIG,
        rhs_type=pb2.RUNNING_CONFIG,
    ):
        """Compare two configurations for a device."""
        lhs = pb2.ConfigRequest(type=lhs_type, device_id=device_id)
        rhs = pb2.ConfigRequest(type=rhs_type, device_id=device_id)
        parsed_timestamp = _parse_timestamp(timestamp)
        if parsed_timestamp:
            lhs.timestamp.CopyFrom(parsed_timestamp)
            rhs.timestamp.CopyFrom(parsed_timestamp)
        request = pb2.GetConfigDiffRequest(lhs=lhs, rhs=rhs)

        diff_entries = []
        errors = []
        try:
            for response in self.stub.GetConfigDiff(request, timeout=self.timeout):
                response_type = response.WhichOneof("response")
                if response_type == "diff":
                    diff_entries.extend(response.diff.entries)
                elif response_type == "lhs":
                    errors.append(response.lhs.error_msg)
                elif response_type == "rhs":
                    errors.append(response.rhs.error_msg)
        except grpc.RpcError as error:
            errors.append(f"gRPC error: {error.details()}")

        adds = sum(entry.op == pb2.ADD for entry in diff_entries)
        deletes = sum(entry.op == pb2.DELETE for entry in diff_entries)
        changes = sum(entry.op == pb2.CHANGE for entry in diff_entries)
        return {
            "adds": adds,
            "deletes": deletes,
            "changes": changes,
            "in_compliance": adds == 0 and deletes == 0 and changes == 0,
            "diff_entries": diff_entries,
            "errors": errors,
        }

    def get_config_diff_for_task(self, task_id):
        """Get the configuration diff for a CloudVision task."""
        request = pb2.GetConfigDiffForTaskRequest(task_id=task_id)
        diff_entries = []
        errors = []
        try:
            for response in self.stub.GetConfigDiffForTask(
                request, timeout=self.timeout
            ):
                response_type = response.WhichOneof("response")
                if response_type == "diff":
                    diff_entries.extend(response.diff.entries)
                elif response_type == "error":
                    errors.append(response.error.error_msg)
        except grpc.RpcError as error:
            errors.append(f"gRPC error: {error.details()}")

        adds = sum(entry.op == pb2.ADD for entry in diff_entries)
        deletes = sum(entry.op == pb2.DELETE for entry in diff_entries)
        changes = sum(entry.op == pb2.CHANGE for entry in diff_entries)
        return {
            "adds": adds,
            "deletes": deletes,
            "changes": changes,
            "in_compliance": adds == 0 and deletes == 0 and changes == 0,
            "diff_entries": diff_entries,
            "errors": errors,
        }

    def get_config_diff_summary(
        self,
        device_id,
        timestamp=None,
        lhs_type=pb2.DESIGNED_CONFIG,
        rhs_type=pb2.RUNNING_CONFIG,
    ):
        """Get summary counts for a configuration comparison."""
        lhs = pb2.ConfigRequest(type=lhs_type, device_id=device_id)
        rhs = pb2.ConfigRequest(type=rhs_type, device_id=device_id)
        parsed_timestamp = _parse_timestamp(timestamp)
        if parsed_timestamp:
            lhs.timestamp.CopyFrom(parsed_timestamp)
            rhs.timestamp.CopyFrom(parsed_timestamp)
        request = pb2.GetConfigDiffSummaryRequest(lhs=lhs, rhs=rhs)

        result = {}
        try:
            for response in self.stub.GetConfigDiffSummary(
                request, timeout=self.timeout
            ):
                summary = response.summary
                result = {
                    "config_compliance": summary.config_compliance,
                    "nop": summary.nop,
                    "ignore": summary.ignore,
                    "add": summary.add,
                    "delete": summary.delete,
                    "change": summary.change,
                    "digest": summary.digest,
                    "error": summary.error,
                }
        except grpc.RpcError as error:
            result["error"] = f"gRPC error: {error.details()}"
        return result

    def get_config_diff_summary_for_task(self, task_id):
        """Get configuration diff summary counts for a task."""
        request = pb2.GetConfigDiffSummaryForTaskRequest(task_id=task_id)
        result = {}
        try:
            for response in self.stub.GetConfigDiffSummaryForTask(
                request, timeout=self.timeout
            ):
                summary = response.summary
                result = {
                    "config_compliance": summary.config_compliance,
                    "nop": summary.nop,
                    "ignore": summary.ignore,
                    "add": summary.add,
                    "delete": summary.delete,
                    "change": summary.change,
                    "digest": summary.digest,
                    "error": summary.error,
                }
        except grpc.RpcError as error:
            result["error"] = f"gRPC error: {error.details()}"
        return result

    def config_diff_raw(
        self,
        lhs_config,
        rhs_config,
        device_id="",
        reconcile_all=False,
        exclude_reconciled_managed_config=False,
    ):
        """Diff two raw configuration strings directly."""

        def request_iterator():
            yield pb2.ConfigDiffRawRequest(lhs=lhs_config)
            yield pb2.ConfigDiffRawRequest(rhs=rhs_config)
            if device_id:
                yield pb2.ConfigDiffRawRequest(device_id=device_id)
            if reconcile_all:
                yield pb2.ConfigDiffRawRequest(reconcile_all=True)
            if exclude_reconciled_managed_config:
                yield pb2.ConfigDiffRawRequest(exclude_reconciled_managed_config=True)

        result = {
            "diff_entries": [],
            "reconciled_config": "",
            "errors": [],
        }
        try:
            for response in self.stub.ConfigDiffRaw(
                request_iterator(), timeout=self.timeout
            ):
                response_type = response.WhichOneof("response")
                if response_type == "diff_entries":
                    result["diff_entries"].extend(response.diff_entries.entries)
                elif response_type == "reconciled_config":
                    result["reconciled_config"] += response.reconciled_config
                elif response_type == "error":
                    result["errors"].append(response.error.error_msg)
        except grpc.RpcError as error:
            result["errors"].append(f"gRPC error: {error.details()}")
        return result

    def get_proposed_config(self, device_id, configlet_ids):
        """Generate a proposed configuration from a set of configlets."""
        request = pb2.GetProposedConfigRequest(
            device_id=device_id, configlet_ids=configlet_ids
        )
        result = {"config": "", "partial_config": "", "errors": []}
        try:
            for response in self.stub.GetProposedConfig(request, timeout=self.timeout):
                response_type = response.WhichOneof("response")
                if response_type == "config":
                    result["config"] += response.config
                elif response_type == "partial_config":
                    result["partial_config"] += response.partial_config
                elif response_type == "error":
                    result["errors"].append(response.error.error_msg)
        except grpc.RpcError as error:
            result["errors"].append(f"gRPC error: {error.details()}")
        return result

    def get_device_status(
        self,
        device_id,
        timestamp=None,
        task_type=pb2.TASKTYPE_UNSPECIFIED,
    ):
        """Get combined configuration and image compliance status."""
        request = pb2.GetDeviceStatusRequest(device_id=device_id, task_type=task_type)
        parsed_timestamp = _parse_timestamp(timestamp)
        if parsed_timestamp:
            request.timestamp.CopyFrom(parsed_timestamp)

        result = {"config_summary": {}, "image_status": {}}
        try:
            for response in self.stub.GetDeviceStatus(request, timeout=self.timeout):
                config_summary = response.config_summary
                result["config_summary"] = {
                    "config_compliance": config_summary.config_compliance,
                    "nop": config_summary.nop,
                    "ignore": config_summary.ignore,
                    "add": config_summary.add,
                    "delete": config_summary.delete,
                    "change": config_summary.change,
                    "digest": config_summary.digest,
                    "error": config_summary.error,
                }
                image_status = response.image_status
                result["image_status"] = {
                    "dual_sup": image_status.dual_sup,
                    "image_compliance": image_status.image_compliance,
                    "extension_compliance": image_status.extension_compliance,
                    "extension_compliance_for_peer_sup": (
                        image_status.extension_compliance_for_peer_sup
                    ),
                    "image_compliance_for_peer_sup": (
                        image_status.image_compliance_for_peer_sup
                    ),
                    "error": image_status.error,
                }
        except grpc.RpcError as error:
            result["error"] = f"gRPC error: {error.details()}"
        return result

    def get_image_diff(self, device_id, timestamp=None):
        """Get the legacy, single-supervisor image diff for a device."""
        request = pb2.GetImageDiffRequest(device_id=device_id)
        parsed_timestamp = _parse_timestamp(timestamp)
        if parsed_timestamp:
            request.timestamp.CopyFrom(parsed_timestamp)

        result = {
            "running_image": "",
            "designed_image": "",
            "running_image_version": "",
            "designed_image_version": "",
            "image_in_compliance": True,
            "image_reboot_required": False,
            "extension_reboot_required": False,
            "dual_sup": False,
            "running_extensions": [],
            "designed_extensions": [],
        }
        try:
            for response in self.stub.GetImageDiff(request, timeout=self.timeout):
                diff = response.diff
                result["running_image"] = diff.running_image
                result["designed_image"] = diff.designed_image
                result["running_image_version"] = diff.running_image_version
                result["designed_image_version"] = diff.designed_image_version
                result["image_in_compliance"] = (
                    diff.running_image == diff.designed_image
                )
                result["image_reboot_required"] = diff.image_reboot_required
                result["extension_reboot_required"] = diff.extension_reboot_required
                result["dual_sup"] = diff.dual_sup
                for extension in diff.running_extensions:
                    result["running_extensions"].append(
                        {
                            "name": extension.name,
                            "version": extension.version,
                            "reboot_required": extension.reboot_required,
                        }
                    )
                for extension in diff.designed_extensions:
                    result["designed_extensions"].append(
                        {
                            "name": extension.name,
                            "version": extension.version,
                        }
                    )
        except grpc.RpcError as error:
            result["error"] = f"gRPC error: {error.details()}"
        return result

    def get_image_diff_for_task(self, task_id):
        """Get the image diff for a CloudVision task."""
        request = pb2.GetImageDiffForTaskRequest(task_id=task_id)
        result = {
            "running_image": "",
            "designed_image": "",
            "image_in_compliance": True,
            "image_reboot_required": False,
            "running_extensions": [],
            "designed_extensions": [],
            "extensions_in_compliance": True,
        }
        try:
            for response in self.stub.GetImageDiffForTask(
                request, timeout=self.timeout
            ):
                diff = response.diff
                result["running_image"] = (
                    diff.running_image_version or diff.running_image
                )
                result["designed_image"] = (
                    diff.designed_image_version or diff.designed_image
                )
                result["image_in_compliance"] = (
                    diff.running_image == diff.designed_image
                )
                result["image_reboot_required"] = diff.image_reboot_required
                for extension in diff.running_extensions:
                    result["running_extensions"].append(
                        f"{extension.name}:{extension.version}"
                    )
                for extension in diff.designed_extensions:
                    result["designed_extensions"].append(
                        f"{extension.name}:{extension.version}"
                    )
                result["extensions_in_compliance"] = set(
                    result["running_extensions"]
                ) == set(result["designed_extensions"])
        except grpc.RpcError as error:
            result["error"] = f"gRPC error: {error.details()}"
        return result

    def get_image_diff_v2(
        self,
        device_id,
        timestamp=None,
        lhs_type=pb2.DESIGNED_IMAGE,
        rhs_type=pb2.RUNNING_IMAGE,
    ):
        """Compare two image states using structured image information."""
        lhs = pb2.ImageRequest(type=lhs_type, device_id=device_id)
        rhs = pb2.ImageRequest(type=rhs_type, device_id=device_id)
        parsed_timestamp = _parse_timestamp(timestamp)
        if parsed_timestamp:
            lhs.timestamp.CopyFrom(parsed_timestamp)
            rhs.timestamp.CopyFrom(parsed_timestamp)
        request = pb2.GetImageDiffRequestV2(lhs=lhs, rhs=rhs)

        result = {
            "lhs_image": "",
            "rhs_image": "",
            "lhs_image_version": "",
            "rhs_image_version": "",
            "image_reboot_required": False,
            "extension_reboot_required": False,
            "digest": "",
        }
        try:
            for response in self.stub.GetImageDiffV2(request, timeout=self.timeout):
                result["lhs_image"] = response.lhs.image
                result["lhs_image_version"] = response.lhs.image_version
                result["rhs_image"] = response.rhs.image
                result["rhs_image_version"] = response.rhs.image_version
                result["image_reboot_required"] = response.image_reboot_required
                result["extension_reboot_required"] = response.extension_reboot_required
                result["digest"] = response.digest
        except grpc.RpcError as error:
            result["error"] = f"gRPC error: {error.details()}"
        return result

    def get_image_diff_v3(
        self,
        device_id,
        timestamp=None,
        a_type=pb2.DESIGNED_IMAGE,
        b_type=pb2.RUNNING_IMAGE,
    ):
        """Get the latest image diff with per-supervisor granularity."""
        side_a = pb2.ImageRequest(type=a_type, device_id=device_id)
        side_b = pb2.ImageRequest(type=b_type, device_id=device_id)
        parsed_timestamp = _parse_timestamp(timestamp)
        if parsed_timestamp:
            side_a.timestamp.CopyFrom(parsed_timestamp)
            side_b.timestamp.CopyFrom(parsed_timestamp)
        request = pb2.GetImageDiffRequestV3(a=side_a, b=side_b)

        result = {
            "running_image": "",
            "designed_image": "",
            "image_in_compliance": True,
            "image_reboot_required": False,
            "running_extensions": [],
            "designed_extensions": [],
            "extensions_in_compliance": True,
        }
        try:
            for response in self.stub.GetImageDiffV3(request, timeout=self.timeout):
                image_info = response.image_info
                result["image_in_compliance"] = (
                    image_info.compliance_status == pb2.SOFTWARE_COMPLIANCE_CODE_IN_SYNC
                )

                for image_diff in image_info.software_image_diff.values.values():
                    if image_diff.a.version:
                        result["designed_image"] = image_diff.a.version
                    elif image_diff.a.name:
                        result["designed_image"] = image_diff.a.name
                    if image_diff.b.version:
                        result["running_image"] = image_diff.b.version
                    elif image_diff.b.name:
                        result["running_image"] = image_diff.b.name

                for extension_diffs in image_info.extensions_diff.values.values():
                    for extension_diff in extension_diffs.values:
                        if extension_diff.a.name:
                            result["designed_extensions"].append(
                                f"{extension_diff.a.name}:"
                                f"{extension_diff.a.version}"
                            )
                        if extension_diff.b.name:
                            result["running_extensions"].append(
                                f"{extension_diff.b.name}:"
                                f"{extension_diff.b.version}"
                            )

                result["extensions_in_compliance"] = set(
                    result["running_extensions"]
                ) == set(result["designed_extensions"])

                if response.HasField("reboot_required"):
                    reboot_required = response.reboot_required
                    result["image_reboot_required"] = (
                        reboot_required.software_image_reboot_required
                        or reboot_required.extension_reboot_required
                    )
        except grpc.RpcError as error:
            result["error"] = f"gRPC error: {error.details()}"
        return result
