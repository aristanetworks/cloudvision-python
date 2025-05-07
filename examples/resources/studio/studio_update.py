#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "cloudvision",
#     "pyyaml",
# ]
# [tool.uv]
# exclude-newer = "2024-08-05T00:00:00Z"
# ///

# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
#
# example usages:
#   python3 studio_update.py
#        --server www.arista.io
#        --token-file token.tok
#        --operation=get
#        --studio-id=studio-interface-v2-pkg
#   python3 studio_update.py
#        --server www.arista.io
#        --token-file token.tok
#        --operation=set
#        --studio-id=studio-interface-v2-pkg
#        --yaml-file=studio-interface-v2-pkg_inputs.yaml
#        --build-only True
#
# Note:
#   It's necessary to first log onto the cvp and create a service account,
#   generate a token, and copy the token to a local token.tok file.
#   If this is for a cvp dut using self-signed certs, then it's also
#   necessary to copy the file at /usr/share/nginx/certs/NginxCerts/cvp.crt
#   to a local file and send that in as an additional parameter, eg:
#   python3 studio_update.py
#        --server 192.0.2.10:443
#        --token-file token.tok
#        --cert-file cvp.crt
#        --operation=get
#        --studio-id=studio-interface-v2-pkg

import argparse
import json
import uuid
import time
import yaml

# pylint: disable=import-error
from arista.workspace.v1 import models as workspace_models
from arista.workspace.v1 import services as workspace_services
from arista.studio.v1 import models as studio_models
from arista.studio.v1 import services as studio_services
from arista.changecontrol.v1 import models as changecontrol_models
from arista.changecontrol.v1 import services as changecontrol_services

# may not be available in container until feature is GA
# from arista.action.v1 import models as action_models
# from arista.action.v1 import services as action_services

from fmp import wrappers_pb2 as fmp_wrappers
from google.protobuf import wrappers_pb2 as wrappers
import grpc

LOGLEVEL = 0


def log(loglevel=0, logstring=''):
    if loglevel <= LOGLEVEL:
        print(logstring)


RPC_TIMEOUT = 30  # in seconds
CC_EXECUTION_TIMEOUT = 60  # in seconds
MAINLINE_ID = ""  # ID to reference merged workspace data


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


def mergeInputs(root=None, path=None, inputs=None):
    '''
    If the studio resource returns inputs in multiple responses,
    this merges them
    '''
    prevElem = None
    prev = root
    currElem = None
    curr = root

    # Walk down the path from the root to the value
    # at the final element, creating any sub-objects
    # or sub-lists along the way if they don't exist.
    for currElem in path:
        # This element is a list index...
        if currElem.isnumeric():
            # If the current value is not a list, set it
            # to one.
            if not isinstance(curr, list):
                if prevElem is None:
                    root = []
                    curr = root
                elif prevElem.isnumeric():
                    prevElemInt = int(prevElem)
                    prev[prevElemInt] = []
                    curr = prev[prevElemInt]
                else:
                    prev[prevElem] = []
                    curr = prev[prevElem]
            # If this index is past the last index of
            # the current list, extend the list until
            # it is big enough for it.
            currElemInt = int(currElem)
            if currElemInt >= len(curr):
                while len(curr) < currElemInt + 1:
                    curr.append(None)
            # Move to the value at the index.
            prevElem = currElem
            prev = curr
            curr = curr[currElemInt]
        # This element is an object key...
        else:
            # If the current value is not an object, set
            # it to one.
            if not isinstance(curr, dict):
                if prevElem is None:
                    root = {}
                    curr = root
                elif prevElem.isnumeric():
                    prevElemInt = int(prevElem)
                    prev[prevElemInt] = {}
                    curr = prev[prevElemInt]
                else:
                    prev[prevElem] = {}
                    curr = prev[prevElem]
            # If the current value does not contain this
            # key, add it.
            if currElem not in curr:
                curr[currElem] = None
            # Move to the value at the key.
            prevElem = currElem
            prev = curr
            curr = curr[currElem]
    # If the path leads to an object, then
    # merge it with the previous object.
    if isinstance(curr, dict):
        curr.update(inputs)

    # If it leads to any other type, then
    # simply set it to the inputs.
    else:
        if currElem is None:
            root = inputs
        elif currElem.isnumeric():
            prev[int(currElem)] = inputs
        else:
            prev[currElem] = inputs
    return root


def get_inputs(channel, filename):
    '''
    Gets studio inputs from the mainline.
    Dumps then into a file named <studio_id>_inputs.yaml.
    '''
    # pylint: disable=no-member
    sid = wrappers.StringValue(value=studio_id)
    wid = wrappers.StringValue(value=MAINLINE_ID)
    key = studio_models.InputsKey(studio_id=sid,
                                  workspace_id=wid)
    pfilter = studio_models.Inputs(key=key)
    req = studio_services.InputsStreamRequest()
    req.partial_eq_filter.append(pfilter)
    stub = studio_services.InputsServiceStub(channel)
    mergedinputs = None
    for resp in stub.GetAll(req, timeout=RPC_TIMEOUT):
        path = resp.value.key.path.values
        split = json.loads(resp.value.inputs.value)
        mergedinputs = mergeInputs(mergedinputs, path, split)
    jsonPathInputs = {'path': [], 'inputs': mergedinputs}
    with open(filename, 'w', encoding='utf8') as f:
        yaml.dump(jsonPathInputs, f)


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


def getActions(filename):
    '''
    Reads a list of actions from file.
    One line per action.
    Each action must have: device, interface, profileID
    Returns a list of Tuples: [(device, interface, profileID),(...]
    '''
    # Parse the action CSV file
    actions = []
    with open(f'{filename}', encoding='utf8') as f:
        for line in f:
            if line.strip().startswith('#'):
                continue
            aline = line.split(',')
            if len(aline) != 3:
                continue
            actions.append((
                aline[0].strip(),
                aline[1].strip(),
                aline[2].strip()))
    return actions


def update_inputs_via_autofill(channel, workspace_id, device, interface,
                               profileID):
    '''
    Sets inputs to the interfacev2 studio using autofill action.
    '''
    # pylint: disable=no-member
    # in case action service is commented out
    # pylint: disable=undefined-variable
    exec_id = str(uuid.uuid4())
    source = 'generate'
    req = action_services.ActionExecConfigSetRequest( # noqa
        value=action_models.ActionExecConfig(   # noqa
            key=action_models.ActionKey(  # noqa
                id=wrappers.StringValue(value=action_id)
            ),
            exec_id=wrappers.StringValue(value=exec_id),
            dynamic_args=action_models.ActionArgValues(  # noqa
            )
        )
    )
    execConfig = action_models.ActionExecConfig()  # noqa
    inputPath = ("[\"sites\", \"0\", \"inputs\", \"sitesGroup\", \"devices\", "
                 "\"0\", \"inputs\", \"devicesGroup\", \"stack\"]")
    dynamicArgs = {
        "InputPath": inputPath,
        "StudioID": studio_id,
        "WorkspaceID": workspace_id,
        "interface": interface,
        "profileID": profileID,
        "source": source,
        "device": device,
    }
    execConfig.key.id.value = action_id
    execConfig.exec_id.value = exec_id
    for k, v in dynamicArgs.items():
        execConfig.dynamic_args.values[k].value.value = v
    req.value.CopyFrom(execConfig)
    stub = action_services.ActionExecConfigServiceStub(channel)   # noqa
    stub.Set(req, timeout=RPC_TIMEOUT)
    log(0, f'Studio inputs set from autofill action:'
        f'\n\t{source} {device} {interface} {profileID}')


def update_inputs_via_yaml(channel, workspace_id, filename, dev_ids):
    '''
    Sets inputs to the interfacev2 studio using the yaml file.
    Also assigns studio to a set of devices.
    '''
    # pylint: disable=no-member
    # convert YAML input file to json inputs.
    with open(f'{filename}', encoding='utf8') as f:
        config = yaml.load(f, Loader=yaml.loader.SafeLoader)
    inputs = config['inputs']
    path = config['path']
    inputs = json.dumps(inputs)
    # Set the root path of the studio to the given inputs.
    req = studio_services.InputsConfigSetRequest(
        value=studio_models.InputsConfig(
            key=studio_models.InputsKey(
                workspace_id=wrappers.StringValue(value=workspace_id),
                studio_id=wrappers.StringValue(value=studio_id),
                path=fmp_wrappers.RepeatedString(values=path)
            ),
            inputs=wrappers.StringValue(value=inputs)
        )
    )
    stub = studio_services.InputsConfigServiceStub(channel)
    stub.Set(req, timeout=RPC_TIMEOUT)
    log(0, f'Studio inputs set from yaml:'
        f'\n\t{filename}')
    # Assign the studio to the given set of devices.
    req = studio_services.AssignedTagsConfigSetRequest(
        value=studio_models.AssignedTagsConfig(
            key=studio_models.StudioKey(
                workspace_id=wrappers.StringValue(value=workspace_id),
                studio_id=wrappers.StringValue(value=studio_id)
            ),
            query=wrappers.StringValue(value=f'device:{",".join(dev_ids)}')
        )
    )
    stub = studio_services.AssignedTagsConfigServiceStub(channel)
    stub.Set(req, timeout=RPC_TIMEOUT)
    log(0, f'\tDevices assigned to studio: {dev_ids}')


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
    for dev_id, result in res.value.build_results.values.items():
        if result.state == workspace_models.BUILD_STATE_FAIL:
            fail_msg += f'\t\tDevice {dev_id}:\n'
            if result.stage == workspace_models.BUILD_STAGE_INPUT_VALIDATION:
                fail_msg += '\t\t\tInput validation:\n'
                ivr = result.input_validation_results.values[
                    studio_id]
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
                cbr = result.configlet_build_results.values[
                    studio_id]
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
                cvr = result.configlet_validation_results.values[
                    studio_id]
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


def run_change_control(channel, cc_id):
    '''
    Approves and starts a change control, waits for it to finish,
    and reports the result. Returns True if execution was successful
    and False otherwise.
    '''
    # pylint: disable=no-member
    log(0, f'Executing change control {cc_id}')
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
    log(0, '\tChange control approved')
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
    log(0, '\tChange control flagged to start')
    # Wait until the change control completes execution.
    req = changecontrol_services.ChangeControlStreamRequest(
        partial_eq_filter=[
            changecontrol_models.ChangeControl(key=key)
        ]
    )
    stub = changecontrol_services.ChangeControlServiceStub(channel)
    log(0, '\tWaiting for execution to complete')
    for res in stub.Subscribe(req, timeout=CC_EXECUTION_TIMEOUT):
        if res.value.status == changecontrol_models.CHANGE_CONTROL_STATUS_COMPLETED:
            if res.value.error.value != "":
                log(0, f'\tExecution failed: {res.value.error.value}')
                return False
            log(0, '\tExecution succeeded')
            return True
    log(0, '\tExecution failed')
    return False


def main(args, channel):
    with channel:
        # Get Inputs
        if args.operation == 'get':
            filename = f'{studio_id}-inputs.yaml'
            get_inputs(channel, filename)
            log(0, f'Mainline inputs have been written to: {filename}')
            return
        # Set Inputs in Multiple Steps
        # Create a workspace.
        workspace_name = f'{studio_id} config push'
        if args.wsid:
            workspace_id = args.wsid
        else:
            workspace_id = create_workspace(channel, workspace_name)
        time.sleep(1)
        # Update the studio with yaml file
        inputSet = False
        actionInvoked = False
        if args.yaml_file:
            update_inputs_via_yaml(
                channel, workspace_id, args.yaml_file.name, "*")
            inputSet = True
        # Update the studio with autofill action
        # Currently very specific to the interfaceV2 studio
        actions = []
        if args.action_file:
            actions = getActions(args.action_file.name)
        for (device, interface, profileID) in actions:
            update_inputs_via_autofill(
                channel, workspace_id, device, interface, profileID)
            actionInvoked = True
            time.sleep(0.1)
        if not inputSet and not actionInvoked:
            return
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
        log(0, f'{len(cc_ids)} change control(s) created')
        for cc_id in cc_ids:
            run_change_control(channel, cc_id)


if __name__ == '__main__':
    desc = (
        "1. Get studio inputs from mainline.\n"
        "   Example:\n"
        "     python3 studio_update.py --server=192.0.2.10:443\n"
        "            --token-file=token.tok --cert-file=cvp.crt\n"
        "            --operation=get --studio-id=studio-evpn-services\n"
        "2. Set studio inputs using a YAML input file or autofill input file.\n"
        "   This will populate, build and submit the studio change.\n"
        "   Example:\n"
        "     python3 studio_update.py --server=192.0.2.10:443\n"
        "            --token-file=token.tok --cert-file=cvp.crt\n"
        "            --operation=set --studio-id=studio-evpn-services\n"
        "            --yaml-file=studio-evpn-services-inputs.yaml\n"
        "   Optionally to trigger action:\n"
        "            --action-file=actions.csv\n"
        "   Optionally to build only and not submit:\n"
        "            --build-only=True\n"
    )
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--server",
                        required=True,
                        metavar="www.arista.io|192.0.2.10:443",
                        help=("endpoint for CVP on-prem cluster or CVaaS tenant "
                              "(must be the www endpoint in case of CVaaS)"))
    parser.add_argument("--token-file", required=True, type=argparse.FileType('r'),
                        help="file with access token")
    parser.add_argument("--cert-file", type=argparse.FileType('rb'),
                        help="file with certificate to use as root CA")
    parser.add_argument("--operation", choices=['set', 'get'], default='get',
                        help="whether to get or set inputs")
    parser.add_argument("--yaml-file", type=argparse.FileType('r'),
                        help="YAML file containing studio inputs")
    parser.add_argument("--action-file", type=argparse.FileType('r'),
                        help="csv file containing studio autofill inputs")
    parser.add_argument("--build-only", type=bool, default=False,
                        help="whether to stop after building the changes (no submission)")
    parser.add_argument("--studio-id", type=str, required=True,
                        help="ID of the Studio, e.g. studio-interface-v2-pkg")
    parser.add_argument("--action-id", type=str,
                        help="ID of the action, e.g. action-ports-table")
    parser.add_argument("--wsid", type=str, default=False,
                        help="existing workspace ID, if not wanting to create a new one")
    pargs = parser.parse_args()
    studio_id = pargs.studio_id
    if pargs.action_id:
        action_id = pargs.action_id
    conn = cv_client(
        server=pargs.server, token=pargs.token_file.read().strip(),
        cert_file=pargs.cert_file
    )
    main(pargs, conn)
