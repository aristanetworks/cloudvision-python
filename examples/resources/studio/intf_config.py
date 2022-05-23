#!/usr/bin/python3

# Copyright (c) 2021 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import argparse
import grpc
import uuid
import yaml
import json

from arista.workspace.v1 import models as workspace_models
from arista.workspace.v1 import services as workspace_services
from arista.studio.v1 import models as studio_models
from arista.studio.v1 import services as studio_services
from arista.changecontrol.v1 import models as changecontrol_models
from arista.changecontrol.v1 import services as changecontrol_services

from fmp import wrappers_pb2 as fmp_wrappers
from google.protobuf import wrappers_pb2 as wrappers

RPC_TIMEOUT = 30  # in seconds
CC_EXECUTION_TIMEOUT = 60  # in seconds
MAINLINE_ID = ""  # ID to reference merged workspace data
INTF_CONFIG_STUDIO_ID = "studio-interface-manager"


def main(args):

    # Get connection credentials.
    token = args.token_file.read().strip()
    callCreds = grpc.access_token_call_credentials(token)
    if args.cert_file:
        cert = args.cert_file.read()
        channelCreds = grpc.ssl_channel_credentials(root_certificates=cert)
    else:
        channelCreds = grpc.ssl_channel_credentials()
    connCreds = grpc.composite_channel_credentials(channelCreds, callCreds)

    with grpc.secure_channel(args.server, connCreds) as channel:

        # Parse the interface config YAML file.
        with open(f'{args.config_file.name}') as f:
            config = yaml.load(f, Loader=yaml.loader.SafeLoader)

        # Convert the YAML configuration to Interface Configuration studio inputs.
        total_intfs = 0
        inputs = {"devices": []}
        for dev_id, intfs in config.items():
            dev_query = f'device:{dev_id}'
            dev_inputs = {
                "inputs": {
                    "interface": []
                },
                "tags": {
                    "query": dev_query
                }
            }
            for intf_name, intf_config in intfs.items():
                intf_query = f'interface:{intf_name}@{dev_id}'
                intf_inputs = {
                    "inputs": {
                        "intfConfig": intf_config
                    },
                    "tags": {
                        "query": intf_query
                    }
                }
                dev_inputs["inputs"]["interface"].append(intf_inputs)
                total_intfs += 1
            inputs["devices"].append(dev_inputs)

        # Create a workspace.
        workspace_name = f'Configure {total_intfs} interface(s) across {len(config)} device(s)'
        workspace_id = create_workspace(channel, workspace_name)

        # Update the interface config studio.
        update_intf_config_studio(channel, workspace_id, json.dumps(inputs), config.keys())

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

        # Execute the spawned change control.
        print(f'{len(cc_ids)} change control(s) created')
        for cc_id in cc_ids:
            run_change_control(channel, cc_id)


def create_workspace(channel, workspace_name):
    '''
    Creates a workspace with a UUID using workspace_name
    as the display name. Returns the UUID.
    '''
    print(f'Creating workspace "{workspace_name}"')

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
    print(f'\tWorkspace {workspace_id} created')
    return workspace_id


def update_intf_config_studio(channel, workspace_id, inputs, dev_ids):
    '''
    Sets all inputs on the interface configuration studio
    and assigns it to a set of devices.
    '''
    print('Updating interface configuration studio')

    # Set the root path of the studio to the given inputs.
    req = studio_services.InputsConfigSetRequest(
        value=studio_models.InputsConfig(
            key=studio_models.InputsKey(
                workspace_id=wrappers.StringValue(value=workspace_id),
                studio_id=wrappers.StringValue(value=INTF_CONFIG_STUDIO_ID),
                path=fmp_wrappers.RepeatedString(values=[])
            ),
            inputs=wrappers.StringValue(value=inputs)
        )
    )
    stub = studio_services.InputsConfigServiceStub(channel)
    stub.Set(req, timeout=RPC_TIMEOUT)
    print('\tStudio inputs set')

    # Assign the studio to the given set of devices.
    req = studio_services.AssignedTagsConfigSetRequest(
        value=studio_models.AssignedTagsConfig(
            key=studio_models.StudioKey(
                workspace_id=wrappers.StringValue(value=workspace_id),
                studio_id=wrappers.StringValue(value=INTF_CONFIG_STUDIO_ID)
            ),
            query=wrappers.StringValue(value=f'device:{",".join(dev_ids)}')
        )
    )
    stub = studio_services.AssignedTagsConfigServiceStub(channel)
    stub.Set(req, timeout=RPC_TIMEOUT)
    print(f'\tStudio assigned to {len(dev_ids)} device(s)')


def build_workspace(channel, workspace_id):
    '''
    Sends a request to build a workspace, waits for it
    to finish, and reports the result. Returns True if
    the build was successful and False otherwise.
    '''
    print('Building workspace')

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
    print(f'\tBuild request {build_id} sent')

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
    print('\tWaiting for build to complete')
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
        fail_msg = ''
        for dev_id, result in res.value.build_results.values.items():
            if result.state == workspace_models.BUILD_STATE_FAIL:
                fail_msg += f'\t\tDevice {dev_id}:\n'
                if result.stage == workspace_models.BUILD_STAGE_INPUT_VALIDATION:
                    fail_msg += '\t\t\tInput validation:\n'
                    ivr = result.input_validation_results.values[INTF_CONFIG_STUDIO_ID]
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
                    cbr = result.configlet_build_results.values[INTF_CONFIG_STUDIO_ID]
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
                    cvr = result.configlet_validation_results.values[INTF_CONFIG_STUDIO_ID]
                    errs = cvr.errors.values
                    if len(errs) > 0:
                        fail_msg += '\t\t\t\tErrors:\n'
                        for i, err in enumerate(errs, start=1):
                            fail_msg += f'\t\t\t\t\t--- # {i}\n'
                            fail_msg += f'\t\t\t\t\tCode: {err.error_code}\n'
                            fail_msg += f'\t\t\t\t\tConfiglet: {err.configlet_name}\n'
                            fail_msg += f'\t\t\t\t\tLine number: {err.line_num}\n'
                            fail_msg += f'\t\t\t\t\tDetails: {err.error_msg}\n'
        print(f'\tBuild failed:\n{fail_msg}')
        return False
    if build_res.status == workspace_models.RESPONSE_STATUS_SUCCESS:
        print('\tBuild succeeded')
        return True


def submit_workspace(channel, workspace_id):
    '''
    Sends a request to submit a workspace, waits for it to
    finish, and reports the result. Returns the IDs of the
    spawned change controls.
    '''
    print('Submitting workspace')

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
    print(f'\tSubmission request {submit_id} sent')

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
    print('\tWaiting for submission to complete')
    for res in stub.Subscribe(req, timeout=RPC_TIMEOUT):
        if submit_id in res.value.responses.values:
            submit_res = res.value.responses.values[submit_id]
            if submit_res.status == workspace_models.RESPONSE_STATUS_FAIL:
                print(f'\tSubmission failed: {submit_res.message.value}')
                return None, False
            if submit_res.status == workspace_models.RESPONSE_STATUS_SUCCESS:
                print('\tSubmission succeeded')
        if res.value.state == workspace_models.WORKSPACE_STATE_SUBMITTED:
            return res.value.cc_ids.values, True


def run_change_control(channel, cc_id):
    '''
    Approves and starts a change control, waits for it to finish,
    and reports the result. Returns True if execution was successful
    and False otherwise.
    '''
    print(f'Executing change control {cc_id}')
    key = changecontrol_models.ChangeControlKey(
        id=wrappers.StringValue(value=cc_id)
    )

    # Approve the change control.
    req = changecontrol_services.ChangeControlRequest(key=key)
    stub = changecontrol_services.ChangeControlServiceStub(channel)
    res = stub.GetOne(req)
    req = changecontrol_services.ApproveConfigSetRequest(
        value=changecontrol_models.ApproveConfig(
            key=key,
            approve=changecontrol_models.FlagConfig(
                value=wrappers.BoolValue(value=True)
            ),
            version=res.time
        )
    )
    stub = changecontrol_services.ApproveConfigServiceStub(channel)
    stub.Set(req)
    print('\tChange control approved')

    # Send a request to start the change control.
    req = changecontrol_services.ChangeControlConfigSetRequest(
        value=changecontrol_models.ChangeControlConfig(
            key=key,
            start=changecontrol_models.FlagConfig(
                value=wrappers.BoolValue(value=True)
            )
        )
    )
    stub = changecontrol_services.ChangeControlConfigServiceStub(channel)
    stub.Set(req)
    print('\tChange control flagged to start')

    # Wait until the change control completes execution.
    req = changecontrol_services.ChangeControlStreamRequest(
        partial_eq_filter=[
            changecontrol_models.ChangeControl(key=key)
        ]
    )
    stub = changecontrol_services.ChangeControlServiceStub(channel)
    print('\tWaiting for execution to complete')
    for res in stub.Subscribe(req, timeout=CC_EXECUTION_TIMEOUT):
        if res.value.status == changecontrol_models.CHANGE_CONTROL_STATUS_COMPLETED:
            if res.value.error.value != "":
                print(f'\tExecution failed: {res.value.error.value}')
                return False
            print('\tExecution succeeded')
            return True


if __name__ == '__main__':
    desc = (
        "Configure interfaces on devices using a YAML file which populates and"
        "submits the built-in Interface Configuration studio.\n"
        "Example:\n"
        "python3 intf_config.py --server 10.83.12.79:8443 --token-file token.txt"
        "--cert-file cvp.crt --config-file=intf_config.yaml"
    )
    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--server', required=True,
                        help="CloudVision server to connect to in <host>:<port> format")
    parser.add_argument("--token-file", required=True, type=argparse.FileType('r'),
                        help="file with access token")
    parser.add_argument("--cert-file", type=argparse.FileType('rb'),
                        help="file with certificate to use as root CA")
    parser.add_argument("--config-file", required=True, type=argparse.FileType('r'),
                        help="YAML file containing interface configurations per device")
    parser.add_argument("--build-only", type=bool, default=False,
                        help="whether to stop after building the changes (no submission)")
    args = parser.parse_args()
    main(args)
