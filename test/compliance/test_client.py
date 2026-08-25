# Copyright (c) 2026 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Tests for Compliance RPCs whose response bodies can be chunked."""

from unittest.mock import Mock

from cloudvision.compliance.client import ComplianceClient
from cloudvision.compliance.gen import compliancecheck_pb2 as pb2


def _client_with_responses(rpc_name, responses):
    client = ComplianceClient.__new__(ComplianceClient)
    client.stub = Mock()
    getattr(client.stub, rpc_name).return_value = iter(responses)
    client.timeout = 5
    return client


def _diff_entry(operation, line):
    return pb2.DiffEntry(op=operation, b_line=line)


def test_get_config_combines_all_streamed_chunks():
    client = _client_with_responses(
        "GetConfig",
        [
            pb2.GetConfigResponse(config="first\n"),
            pb2.GetConfigResponse(
                configFilterCodes=pb2.ConfigFilterCodes(
                    inLineFilterCode=[
                        pb2.InLineFilterCode(lineNo=1, filterCode=pb2.MANAGED_LINE)
                    ]
                )
            ),
            pb2.GetConfigResponse(config="second\n"),
            pb2.GetConfigResponse(
                sources=pb2.ConfigSources(
                    source=[
                        pb2.ConfigSource(
                            source_type=pb2.CONFIG_TYPE_STUDIO,
                            key="studio-id",
                        )
                    ]
                )
            ),
            pb2.GetConfigResponse(config="third\n"),
        ],
    )

    result = client.get_config("device-id")

    assert result["config"] == "first\nsecond\nthird\n"
    assert result["filter_codes"] == [{"line_no": 1, "filter_code": pb2.MANAGED_LINE}]
    assert result["sources"] == [
        {"source_type": pb2.CONFIG_TYPE_STUDIO, "key": "studio-id"}
    ]


def test_get_config_diff_combines_all_streamed_diff_chunks():
    client = _client_with_responses(
        "GetConfigDiff",
        [
            pb2.GetConfigDiffResponse(
                diff=pb2.ConfigDiff(entries=[_diff_entry(pb2.ADD, "added")])
            ),
            pb2.GetConfigDiffResponse(
                lhs=pb2.CvpConfigError(error_msg="left-side warning")
            ),
            pb2.GetConfigDiffResponse(
                diff=pb2.ConfigDiff(
                    entries=[
                        _diff_entry(pb2.DELETE, "deleted"),
                        _diff_entry(pb2.CHANGE, "changed"),
                    ]
                )
            ),
        ],
    )

    result = client.get_config_diff("device-id")

    assert [entry.b_line for entry in result["diff_entries"]] == [
        "added",
        "deleted",
        "changed",
    ]
    assert result["adds"] == 1
    assert result["deletes"] == 1
    assert result["changes"] == 1
    assert result["errors"] == ["left-side warning"]


def test_get_config_diff_for_task_combines_all_streamed_diff_chunks():
    client = _client_with_responses(
        "GetConfigDiffForTask",
        [
            pb2.GetConfigDiffForTaskResponse(
                diff=pb2.ConfigDiff(entries=[_diff_entry(pb2.ADD, "first")])
            ),
            pb2.GetConfigDiffForTaskResponse(
                diff=pb2.ConfigDiff(entries=[_diff_entry(pb2.ADD, "second")])
            ),
            pb2.GetConfigDiffForTaskResponse(
                error=pb2.CvpConfigError(error_msg="task warning")
            ),
        ],
    )

    result = client.get_config_diff_for_task("task-id")

    assert [entry.b_line for entry in result["diff_entries"]] == [
        "first",
        "second",
    ]
    assert result["adds"] == 2
    assert result["errors"] == ["task warning"]


def test_get_proposed_config_combines_all_streamed_config_chunks():
    client = _client_with_responses(
        "GetProposedConfig",
        [
            pb2.GetProposedConfigResponse(config="first\n"),
            pb2.GetProposedConfigResponse(partial_config="partial-1\n"),
            pb2.GetProposedConfigResponse(config="second\n"),
            pb2.GetProposedConfigResponse(partial_config="partial-2\n"),
            pb2.GetProposedConfigResponse(
                error=pb2.CvpConfigError(error_msg="config warning")
            ),
        ],
    )

    result = client.get_proposed_config("device-id", ["configlet-id"])

    assert result["config"] == "first\nsecond\n"
    assert result["partial_config"] == "partial-1\npartial-2\n"
    assert result["errors"] == ["config warning"]


def test_config_diff_raw_combines_all_streamed_output_chunks():
    client = _client_with_responses(
        "ConfigDiffRaw",
        [
            pb2.ConfigDiffRawResponse(
                diff_entries=pb2.ConfigDiff(entries=[_diff_entry(pb2.ADD, "first")])
            ),
            pb2.ConfigDiffRawResponse(reconciled_config="config-1\n"),
            pb2.ConfigDiffRawResponse(
                diff_entries=pb2.ConfigDiff(entries=[_diff_entry(pb2.DELETE, "second")])
            ),
            pb2.ConfigDiffRawResponse(reconciled_config="config-2\n"),
            pb2.ConfigDiffRawResponse(
                error=pb2.CvpConfigError(error_msg="raw warning")
            ),
        ],
    )

    result = client.config_diff_raw("lhs", "rhs")

    assert [entry.b_line for entry in result["diff_entries"]] == [
        "first",
        "second",
    ]
    assert result["reconciled_config"] == "config-1\nconfig-2\n"
    assert result["errors"] == ["raw warning"]
