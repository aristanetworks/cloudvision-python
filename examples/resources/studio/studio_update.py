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

# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
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
from arista.action.v1 import models as action_models
from arista.action.v1 import services as action_services
from arista.time import time_pb2

from fmp import wrappers_pb2 as fmp_wrappers
from google.protobuf import json_format
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


def getActionTriggers(filename):
    '''
    Reads action trigger data from a file.
    The file contains a comment header specifying:
      - the input path
        eg. # input path: ["sites", "0", "inputs", "sitesGroup", "devices"]
      - names of the dynamic arguments (optional)
        eg. # dynamic arguments: device, interface, profileID, source
    If dynamic argument names are specified:
      - after the header each line provides those dynamic args values for each trigger
    If dynamic args names are not specified:
      - one empty dynamic args is returned for one trigger

    Args:
        filename (str): The path to the input CSV file.

    Returns:
        tuple: (input_path, dyn_names, dyn_values)
            - input_path (str):   string extracted from comment line starting with
                                  '# input path:'
            - dyn_names (list):   list of strings extracted from comment line starting with
                                  '# dynamic arguments:'
            - dyn_values (list):  A list of dictionaries, where each dictionary
                                  represents a row and uses the dynamic args names as keys.
    '''
    input_path = ""
    dyn_names = []
    dyn_values = []
    path_prefix = "# input path:"
    dyn_prefix = "# dynamic arguments:"
    dyn_found = False
    path_found = False

    try:
        with open(filename, encoding='utf8') as f:
            for i, line in enumerate(f):
                stripped_line = line.strip()

                # --- 1. Header Parsing Logic ---
                if not dyn_found or not path_found and stripped_line.startswith('#'):
                    # Check for the explicit header definition comment
                    if stripped_line.startswith(dyn_prefix):
                        # Extract the comma-separated field names after the colon
                        dyn_names_line = stripped_line[len(dyn_prefix):].strip()
                        if dyn_names_line:
                            dyn_names = [col.strip() for col in dyn_names_line.split(',')]
                            dyn_found = True
                    if stripped_line.startswith(path_prefix):
                        input_path = stripped_line[len(path_prefix):].strip()
                        path_found = True
                    continue
                if not dyn_found or not path_found:
                    continue

                # --- 2. Dynamic Args Parsing Logic ---
                # If we have dynamic args names, process the dynamic arg values line
                if stripped_line.startswith('#'):
                    continue
                aline = [col.strip() for col in stripped_line.split(',')]

                # Skip malformed lines where column count doesn't match header count
                if len(aline) != len(dyn_names):
                    log(0, f'skipping invalid dynamic args values in action-file:'
                        f'{aline}')
                    continue

                # Create the action dictionary
                dyn_dict = {}
                for j, dyn_name in enumerate(dyn_names):
                    dyn_dict[dyn_name] = aline[j]

                dyn_values.append(dyn_dict)

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return [], []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [], []

    # if path and no args required,
    # append one empty args entry to still trigger one action
    if input_path and len(dyn_values) == 0:
        dyn_values.append({})
    return input_path, dyn_names, dyn_values


def update_inputs_via_autofill(channel, workspace_id, path, dyn_names, dyn_value):
    '''
    Sets inputs to the studio using autofill action.
    '''
    # pylint: disable=no-member
    exec_id = str(uuid.uuid4())
    req = action_services.ActionRunConfigSetRequest( # noqa
        value=action_models.ActionRunConfig(   # noqa
            key=action_models.ActionRunKey(  # noqa
                run_id=wrappers.StringValue(value=exec_id)
            ),
            action_id=wrappers.StringValue(value=action_id),
            dynamic_args=action_models.ActionArgValues(  # noqa
            )
        )
    )
    runConfig = action_models.ActionRunConfig()  # noqa
    dynamicArgs = {
        "InputPath": path,
        "StudioID": studio_id,
        "WorkspaceID": workspace_id,
    }
    for dyn_name in dyn_names:
        dynamicArgs[dyn_name] = dyn_value.get(dyn_name)

    runConfig.key.run_id.value = exec_id
    runConfig.action_id.value = action_id
    for k, v in dynamicArgs.items():
        runConfig.dynamic_args.values[k].value.value = v
    req.value.CopyFrom(runConfig)
    stub = action_services.ActionRunConfigServiceStub(channel)   # noqa
    stub.Set(req, timeout=RPC_TIMEOUT)
    log(0, f'Studio inputs set from autofill action:'
        f'\n\t{dyn_value}')
    stub = action_services.ActionRunServiceStub(channel)   # noqa
    for res in stub.Subscribe(req, timeout=RPC_TIMEOUT):
        if res.value.error.value != "":
            log(0, f'autofill failed with error:'
                f'\n\t{res.value.error.value}')
            break
        if res.value.is_finished.value:
            log(0, '\tautofill succeeded')
            break


def update_inputs_via_yaml(channel, workspace_id, filename, dev_ids):
    '''
    Sets inputs to the studio using the yaml file.
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


def synchronize_workspace(channel, workspace_id):
    '''
    Sends a request to synchronize a workspace with the latest
    mainline content, waits for it to finish, and reports the result.
    Returns True if the synchronization was successful and False otherwise.
    '''
    # pylint: disable=no-member
    log(0, 'Synchronizing workspace with mainline')
    # Check if workspace needs rebase by getting current workspace state
    get_req = workspace_services.WorkspaceRequest(
        key=workspace_models.WorkspaceKey(
            workspace_id=wrappers.StringValue(value=workspace_id)
        )
    )
    stub = workspace_services.WorkspaceServiceStub(channel)
    workspace_resp = stub.GetOne(get_req, timeout=RPC_TIMEOUT)

    # Check if rebase is needed
    if not workspace_resp.value.needs_rebase.value:
        log(0, '\tWorkspace is already up to date, no rebase needed')
        return True

    log(0, '\tWorkspace needs rebase, proceeding with synchronization')
    sync_id = str(uuid.uuid4())
    req = workspace_services.WorkspaceConfigSetRequest(
        value=workspace_models.WorkspaceConfig(
            key=workspace_models.WorkspaceKey(
                workspace_id=wrappers.StringValue(value=workspace_id)
            ),
            request=workspace_models.REQUEST_REBASE,
            request_params=workspace_models.RequestParams(
                request_id=wrappers.StringValue(value=sync_id)
            )
        )
    )
    stub = workspace_services.WorkspaceConfigServiceStub(channel)
    stub.Set(req, timeout=RPC_TIMEOUT)
    log(0, f'\tSynchronization request {sync_id} sent')
    # Wait until the workspace sync request finishes.
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
    log(0, '\tWaiting for synchronization to complete')
    for res in stub.Subscribe(req, timeout=RPC_TIMEOUT):
        if sync_id in res.value.responses.values:
            sync_res = res.value.responses.values[sync_id]
            if sync_res.status == workspace_models.RESPONSE_STATUS_FAIL:
                log(0, f'\tSynchronization failed: {sync_res.message.value}')
                return False
            if sync_res.status == workspace_models.RESPONSE_STATUS_SUCCESS:
                log(0, '\tSynchronization succeeded')
                download_sync_diffs(channel, workspace_id, res.value.last_rebased_at)
                return True
    log(0, '\tSynchronization failed')
    return False


def download_sync_diffs(channel, workspace_id, last_rebased_at=None):
    '''
    Downloads synchronization diffs for a workspace and saves them to a file.
    Returns True if successful, False otherwise.

    Note: This feature requires CloudVision API support for WorkspaceDiffsService.
    If not available, the function will log a warning and return False.
    '''
    # pylint: disable=no-member
    filename = f'{workspace_id}_sync_diffs.yaml'
    log(0, '\tDownloading sync diffs...')
    try:
        req = workspace_services.WorkspaceDiffsStreamRequest(
            partial_eq_filter=[
                workspace_models.WorkspaceDiffs(
                    key=workspace_models.DiffKey(
                        workspace_id=wrappers.StringValue(value=workspace_id),
                        diff_type=workspace_models.DIFF_TYPE_REBASE
                    )
                )
            ]
        )
        # If last_rebased_at timestamp is provided, use it to filter the diffs
        if last_rebased_at:
            req.time.end.CopyFrom(last_rebased_at)
            req.time.start.CopyFrom(last_rebased_at)

        stub = workspace_services.WorkspaceDiffsServiceStub(channel)
        diffs_data = []
        for resp in stub.GetAll(req, timeout=RPC_TIMEOUT):
            response_dict = json_format.MessageToDict(resp)
            # Extract only the 'value' field, excluding metadata 'time' and 'type'
            if 'value' in response_dict:
                diffs_data.append(response_dict['value'])
        with open(filename, 'w', encoding='utf8') as f:
            yaml.dump(diffs_data, f, default_flow_style=False)
        log(0, f'\tSync diffs saved to {filename}')
        return True
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNIMPLEMENTED:
            log(0, '\tWorkspaceDiffsService is not supported on this CloudVision server')
            log(0, '\tThis feature may require a newer CloudVision version')
            log(0, '\tSkipping sync diffs download')
        else:
            log(0, f'\tFailed to download sync diffs: {e.details()}')
        return False
    except Exception as e:
        log(0, f'\tFailed to download sync diffs: {e}')
        return False


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
        dyn_values = []
        if args.action_file:
            input_path, dyn_names, dyn_values = getActionTriggers(args.action_file.name)
        for dyn_value in dyn_values:
            update_inputs_via_autofill(
                channel, workspace_id, input_path, dyn_names, dyn_value)
            actionInvoked = True
        if not inputSet and not actionInvoked:
            return
        # Synchronize workspace if requested (before build)
        if args.sync:
            if not synchronize_workspace(channel, workspace_id):
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
        "            --action-id=action-ports-table\n"
        "   Optionally to build only and not submit:\n"
        "            --build-only=True\n"
        "   Optionally to synchronize workspace with mainline before building:\n"
        "            --sync=True\n"
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
    parser.add_argument("--sync", type=bool, default=False,
                        help="synchronize workspace with mainline before building")
    pargs = parser.parse_args()
    studio_id = pargs.studio_id
    if pargs.action_id:
        action_id = pargs.action_id
    conn = cv_client(
        server=pargs.server, token=pargs.token_file.read().strip(),
        cert_file=pargs.cert_file
    )
    main(pargs, conn)
