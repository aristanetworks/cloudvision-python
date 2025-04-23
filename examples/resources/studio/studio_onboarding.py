#!/usr/bin/python3
# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
#
# example usages:
#   python3 studio_onboarding.py
#        --server www.arista.io
#        --token-file token.tok
#   python3 studio_onboarding.py
#      --server www.arista.io
#      --token-file token.tok
#      --operation set
#      --update-id 'add::DEVICE::{"deviceId":"JPEXXXXXXX","hostname":"leaf123","interfaceSize":193}'


import argparse

import grpc

import json
import uuid
from arista.workspace.v1 import models as workspace_models
from arista.workspace.v1 import services as workspace_services
import arista.studio_topology.v1
from google.protobuf.json_format import Parse
from fmp import wrappers_pb2 as fmp_wrappers
from google.protobuf import wrappers_pb2 as wrappers


RPC_TIMEOUT = 600  # in seconds
LOGLEVEL = 0


def log(loglevel=0, logstring=''):
    if loglevel <= LOGLEVEL:
        print(logstring)


def cv_client(server, token, cert_file):
    '''
    Create secure connection to CloudVision.
    '''
    callCreds = grpc.access_token_call_credentials(token)
    if cert_file:
        cert = cert_file.read()
        channelCreds = grpc.ssl_channel_credentials(root_certificates=cert)
    else:
        channelCreds = grpc.ssl_channel_credentials()
    connCreds = grpc.composite_channel_credentials(channelCreds, callCreds)
    return grpc.secure_channel(server, connCreds)


def create_workspace(channel, workspace_name):
    '''
    Creates a workspace with a UUID using workspace_name
    as the display name. Returns the UUID.
    '''
    # pylint: disable=no-member
    log(0, f'Creating workspace "{workspace_name}"')
    workspace_id = str(uuid.uuid4())
    req = workspace_services.WorkspaceConfigSetRequest(
        value=workspace_models.WorkspaceConfig(
            key=workspace_models.WorkspaceKey(
                workspace_id=wrappers.StringValue(value=workspace_id)
            ),
            display_name=wrappers.StringValue(value=workspace_name)
        )
    )
    stub = workspace_services.WorkspaceConfigServiceStub(channel)
    stub.Set(req, timeout=RPC_TIMEOUT)
    log(0, f'\tWorkspaceID created: {workspace_id}')
    return workspace_id


def build_workspace(channel, workspace_id):
    '''
    Sends a request to build a workspace, waits for it
    to finish, and reports the result. Returns True if
    the build was successful and False otherwise.
    '''
    # pylint: disable=no-member
    log(0, 'Building workspace')
    # Send a request to build the workspace.
    build_id = str(uuid.uuid4())
    req = workspace_services.WorkspaceConfigSetRequest(
        value=workspace_models.WorkspaceConfig(
            key=workspace_models.WorkspaceKey(
                workspace_id=wrappers.StringValue(value=workspace_id)
            ),
            request=workspace_models.REQUEST_START_BUILD,
            request_params=workspace_models.RequestParams(
                request_id=wrappers.StringValue(value=build_id)
            )
        )
    )
    stub = workspace_services.WorkspaceConfigServiceStub(channel)
    stub.Set(req, timeout=RPC_TIMEOUT)
    log(0, f'\tBuild request {build_id} sent')
    # Wait until the workspace build request finishes.
    req = workspace_services.WorkspaceStreamRequest(
        partial_eq_filter=[
            workspace_models.Workspace(
                key=workspace_models.WorkspaceKey(
                    workspace_id=wrappers.StringValue(value=workspace_id),
                )
            )
        ]
    )
    stub = workspace_services.WorkspaceServiceStub(channel)
    log(0, '\tWaiting for build to complete')
    for res in stub.Subscribe(req, timeout=RPC_TIMEOUT):
        if build_id in res.value.responses.values:
            build_res = res.value.responses.values[build_id]
            break
    if build_res.status == workspace_models.RESPONSE_STATUS_FAIL:
        # Get the workspace build results.
        req = workspace_services.WorkspaceBuildRequest(
            key=workspace_models.WorkspaceBuildKey(
                workspace_id=wrappers.StringValue(value=workspace_id),
                build_id=wrappers.StringValue(value=build_id)
            )
        )
        stub = workspace_services.WorkspaceBuildServiceStub(channel)
        res = stub.GetOne(req, timeout=RPC_TIMEOUT)
        # Print the build failure into a more readable format.
        fail_msg = build_failure_message(res)
        log(0, f'\tBuild failed:\n{fail_msg}')
        return False
    if build_res.status == workspace_models.RESPONSE_STATUS_SUCCESS:
        log(0, '\tBuild succeeded')
        return True
    log(0, '\tBuild failed')
    return False


def build_failure_message(res):
    fail_msg = ''
    studio_id = "TOPOLOGY"
    for dev_id, result in res.value.build_results.values.items():
        if result.state == workspace_models.BUILD_STATE_FAIL:
            fail_msg += f'\t\tDevice {dev_id}:\n'
            if result.stage == workspace_models.BUILD_STAGE_INPUT_VALIDATION:
                fail_msg += '\t\t\tInput validation:\n'
                ivr = result.input_validation_results.values[studio_id]
                schema_errs = ivr.input_schema_errors.values
                if len(schema_errs) > 0:
                    fail_msg += '\t\t\t\tInput schema errors:\n'
                for i, err in enumerate(schema_errs, start=1):
                    fail_msg += f'\t\t\t\t\t--- # {i}\n'
                    fail_msg += f'\t\t\t\t\tField ID: {err.field_id.value}\n'
                    fail_msg += f'\t\t\t\t\tPath: {err.path.values}\n'
                    fail_msg += f'\t\t\t\t\tMembers: {err.members.values}\n'
                    fail_msg += f'\t\t\t\t\tDetails: {err.message.value}\n'
                value_errs = ivr.input_value_errors.values
                if len(value_errs) > 0:
                    fail_msg += '\t\t\t\tInput value errors:\n'
                for i, err in enumerate(value_errs, start=1):
                    fail_msg += f'\t\t\t\t\t--- # {i}\n'
                    fail_msg += f'\t\t\t\t\tField ID: {err.field_id.value}\n'
                    fail_msg += f'\t\t\t\t\tPath: {err.path.values}\n'
                    fail_msg += f'\t\t\t\t\tMembers: {err.members.values}\n'
                    fail_msg += f'\t\t\t\t\tDetails: {err.message.value}\n'
                other_errs = ivr.other_errors.values
                if len(other_errs) > 0:
                    fail_msg += '\t\t\t\tOther errors:\n'
                for i, err in enumerate(other_errs, start=1):
                    fail_msg += f'\t\t\t\t\t--- # {i}\n'
                    fail_msg += f'\t\t\t\t\t{err}\n'
            if result.stage == workspace_models.BUILD_STAGE_CONFIGLET_BUILD:
                fail_msg += '\t\t\tConfiglet compilation:\n'
                cbr = result.configlet_build_results.values[studio_id]
                templ_errs = cbr.template_errors.values
                if len(templ_errs) > 0:
                    fail_msg += '\t\t\t\tTemplate errors:\n'
                for i, err in enumerate(templ_errs, start=1):
                    fail_msg += f'\t\t\t\t\t--- # {i}\n'
                    fail_msg += f'\t\t\t\t\tLine number: {err.line_num.value}\n'
                    fail_msg += f'\t\t\t\t\tException: {err.exception.value}\n'
                    fail_msg += f'\t\t\t\t\tDetails: {err.details.value}\n'
            if result.stage == workspace_models.BUILD_STAGE_CONFIG_VALIDATION:
                fail_msg += '\t\t\tConfiglet validation:\n'
                cvr = result.configlet_validation_results.values[studio_id]
                errs = cvr.errors.values
                if len(errs) > 0:
                    fail_msg += '\t\t\t\tErrors:\n'
                for i, err in enumerate(errs, start=1):
                    fail_msg += f'\t\t\t\t\t--- # {i}\n'
                    fail_msg += f'\t\t\t\t\tCode: {err.error_code}\n'
                    fail_msg += f'\t\t\t\t\tConfiglet: {err.configlet_name}\n'
                    fail_msg += f'\t\t\t\t\tLine number: {err.line_num}\n'
                    fail_msg += f'\t\t\t\t\tDetails: {err.error_msg}\n'
    return fail_msg


def submit_workspace(channel, workspace_id):
    '''
    Sends a request to submit a workspace, waits for it to
    finish, and reports the result. Returns the IDs of the
    spawned change controls.
    '''
    # pylint: disable=no-member
    log(0, 'Submitting workspace')
    # Send a request to submit the workspace.
    submit_id = str(uuid.uuid4())
    req = workspace_services.WorkspaceConfigSetRequest(
        value=workspace_models.WorkspaceConfig(
            key=workspace_models.WorkspaceKey(
                workspace_id=wrappers.StringValue(value=workspace_id)
            ),
            request=workspace_models.REQUEST_SUBMIT,
            request_params=workspace_models.RequestParams(
                request_id=wrappers.StringValue(value=submit_id)
            )
        )
    )
    stub = workspace_services.WorkspaceConfigServiceStub(channel)
    stub.Set(req, timeout=RPC_TIMEOUT)
    log(0, f'\tSubmission request {submit_id} sent')
    # Wait until the submission request finishes.
    req = workspace_services.WorkspaceStreamRequest(
        partial_eq_filter=[
            workspace_models.Workspace(
                key=workspace_models.WorkspaceKey(
                    workspace_id=wrappers.StringValue(value=workspace_id),
                )
            )
        ]
    )
    stub = workspace_services.WorkspaceServiceStub(channel)
    log(0, '\tWaiting for submission to complete')
    for res in stub.Subscribe(req, timeout=RPC_TIMEOUT):
        if submit_id in res.value.responses.values:
            submit_res = res.value.responses.values[submit_id]
            if submit_res.status == workspace_models.RESPONSE_STATUS_FAIL:
                log(0, f'\tSubmission failed: {submit_res.message.value}')
                return None, False
            if submit_res.status == workspace_models.RESPONSE_STATUS_SUCCESS:
                log(0, '\tSubmission succeeded')
        if res.value.state == workspace_models.WORKSPACE_STATE_SUBMITTED:
            return res.value.cc_ids.values, True
    log(0, '\tSubmission failed')
    return None, False


def main(args, channel):

    with channel:
        workspace_name = "Accepting new devices and interfaces into I&T Studio"
        if args.wsid:
            workspace_id = args.wsid
        else:
            workspace_id = create_workspace(channel, workspace_name)
        # set the status to UPDATE_STATUS_NEW (1)
        json_request = json.dumps({
            "partialEqFilter": [{"status": 1, "key": {"workspaceId": workspace_id}}]
        })
        req = Parse(json_request, arista.studio_topology.v1.services.UpdateStreamRequest(), False)
        update_stub = arista.studio_topology.v1.services.UpdateServiceStub(channel)
        if args.operation == 'get':
            for resp in update_stub.GetAll(req, timeout=RPC_TIMEOUT):
                print(resp.value.key.update_id.value)
        if args.operation == 'set-all':
            for resp in update_stub.GetAll(req, timeout=RPC_TIMEOUT):
                update_id = resp.value.key.update_id.value
                # set the status to UPDATE_STATUS_ACCEPTED (2)
                json_request = json.dumps({
                    "value": {
                        "status": 2,
                        "key": {
                            "workspaceId": workspace_id,
                            "updateId": update_id
                        }
                    }
                })
                req = Parse(
                    json_request,
                    arista.studio_topology.v1.services.UpdateConfigSetRequest(),
                    False
                )
                update_stub = arista.studio_topology.v1.services.UpdateConfigServiceStub(channel)
                update_stub.Set(req, timeout=RPC_TIMEOUT)
        if args.operation == 'set':
            if not args.update_id:
                print('Error: update ID is required for set operation')
                return
            update_id = args.update_id
            json_request = json.dumps({
                "value": {
                    "status": 2,
                    "key": {
                        "workspaceId": workspace_id,
                        "updateId": update_id
                    }
                }
            })
            req = Parse(
                json_request,
                arista.studio_topology.v1.services.UpdateConfigSetRequest(),
                False
            )
            update_stub = arista.studio_topology.v1.services.UpdateConfigServiceStub(channel)
            update_stub.Set(req, timeout=RPC_TIMEOUT)
        # Build the workspace.
        if not build_workspace(channel, workspace_id):
            return
        # Stop here if --build-only.
        if args.build_only:
            return
        # Submit the workspace.
        cc_ids, submitted = submit_workspace(channel, workspace_id)
        if not submitted:
            return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--server',
        required=True,
        help="CloudVision server to connect to in <host>:<port> format")
    parser.add_argument("--token-file", required=True,
                        type=argparse.FileType('r'), help="file with access token")
    parser.add_argument("--cert-file", type=argparse.FileType('rb'),
                        help="certificate to use as root CA")
    parser.add_argument("--wsid", type=str, default=False,
                        help="existing workspace ID, if not wanting to create a new one")
    parser.add_argument("--operation", choices=['set', 'get', 'set-all'], default='get',
                        help="whether to get or set inputs")
    parser.add_argument("--update-id", type=str,
                        default=False, help="Update ID from UpdateService call to set")
    parser.add_argument("--build-only", type=bool, default=False,
                        help="whether to stop after building the changes (no submission)")
    args = parser.parse_args()
    conn = cv_client(
        server=args.server, token=args.token_file.read().strip(),
        cert_file=args.cert_file)
    main(args, conn)
