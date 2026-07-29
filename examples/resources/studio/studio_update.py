#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml",
#     "cloudvision>=1.29.1"
# ]
# ///

# Copyright (c) 2026 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
#
# example usages:
#   python3 studio_update.py
#        --server www.arista.io
#        --token-file token.tok
#        --operation=get
#        --studio-id=studio-evpn-services
#        --yaml-file=get_paths.yaml
#   python3 studio_update.py
#        --server www.arista.io
#        --token-file token.tok
#        --operation=set
#        --studio-id=studio-evpn-services
#        --yaml-file=set_inputs.yaml
#        --build-only=True
#
# Note:
#   It's necessary to first log onto the cvp and create a service account,
#   generate a token, and copy the token to a local token.tok file.
#   If the cvp server uses self-signed certs use the --insecure flag
#   eg:
#   python3 studio_update.py
#        --server 192.0.2.10:443
#        --token-file token.tok
#        --insecure
#        --operation=get
#        --studio-id=studio-interface-v2-pkg
#
# This script can be invoked from a multi-threaded program.  It has the
# ability to rebase and order CCs appropriately to correctly process
# parallel executions.
#

import argparse
import asyncio
import json
import logging
import sys
import uuid
import yaml

from grpclib import Status
from grpclib.exceptions import GRPCError

from cloudvision.api import client as cv_client
from cloudvision.api import fmp
from cloudvision.api.arista.workspace import v1 as workspace
from cloudvision.api.arista.studio import v1 as studio
from cloudvision.api.arista.changecontrol import v1 as changecontrol
from cloudvision.api.arista.action import v1 as action
from cloudvision.cvlib.constants import MAINLINE_WS_ID

logger = logging.getLogger(__name__)


class InputPathNotFoundError(Exception):
    '''Indicates that a requested studio input path does not exist.'''


# CHANGE_SIGNATURE
#     - substring used in workspace and change control names,
#       used to identify changes automated by this script
CHANGE_SIGNATURE = "studio_update.py config push"
# RPC_TIMEOUT
#     - used for quick requests (in seconds)
RPC_TIMEOUT = 30
# BUILD_TIMEOUT
#     - set to max expected build time (in seconds)
#     - set higher proportional to supported device count
BUILD_TIMEOUT = 300
# SYNC_TIMEOUT
#     - set to max expected synchronization time (in seconds)
SYNC_TIMEOUT = 300
# CC_EXECUTION_TIMEOUT
#     - set to max expected CC time (in seconds)
#     - set higher proportional to supported device count and config size
CC_EXECUTION_TIMEOUT = 600
# MAX_SYNC_RETRIES
#     - set at minimum to max number parallel workspace requests
#     - since submits are serial, Nth workspace will need N-1 syncs
MAX_SYNC_RETRIES = 10
# CC_ORDERING_ENABLED
#     - when True, CCs will execute in creation order (waits for earlier CCs)
#     - when False, CCs execute immediately after submission
CC_ORDERING_ENABLED = True
# MAX_CC_WAIT_ITERATIONS
#     - maximum iterations to wait for earlier CCs to complete
MAX_CC_WAIT_ITERATIONS = 120
# CC_POLL_INTERVAL
#     - seconds to wait between polling for earlier CCs
CC_POLL_INTERVAL = 5
# assign_studio
#     - whether to modify studio device selection
assign_studio = False
# get_sync_diffs
#     - whether to get and output sync diffs into a file
get_sync_diffs = False


def create_client(args):
    '''
    Creates an AsyncCVClient from common CLI arguments
    (--server, --token-file, --cert-file, --insecure).
    '''
    token = args.token_file.read().strip()
    host_parts = args.server.split(':')
    host = host_parts[0]
    port = int(host_parts[1]) if len(host_parts) > 1 else 443
    return cv_client.AsyncCVClient.from_token(
        token=token, host=host, port=port,
        cacert=args.cert_file, insecure=args.insecure,
    )


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


def get_input_paths(filename):
    '''Loads and validates one or more input paths from a YAML file.'''
    with open(filename, encoding='utf8') as f:
        config = yaml.safe_load(f)

    configs = config if isinstance(config, list) else [config]
    if not configs:
        raise ValueError(f"Invalid YAML format in {filename}. "
                         "Expected at least one path.")

    paths = []
    for i, cfg in enumerate(configs, start=1):
        if not isinstance(cfg, dict) or set(cfg) != {'path'}:
            raise ValueError(f"Invalid YAML format in {filename} "
                             f"for config at index {i}. "
                             "Expected a dict containing only a 'path' key.")
        path = cfg['path']
        if (not isinstance(path, list)
                or not all(isinstance(elem, str) for elem in path)):
            raise ValueError(f"Invalid YAML format in {filename} "
                             f"for config at index {i}. "
                             "The 'path' value must be a list of strings.")
        paths.append(path)
    return paths, isinstance(config, list)


async def get_inputs(channel, filename, path_filename=None):
    '''
    Gets studio inputs from the mainline, defaulting to the root path,
    but optionally at paths in a YAML file.
    Dumps them into a file named <studio_id>_inputs.yaml.
    '''
    sid = studio_id
    if path_filename is not None:
        paths, multiple = get_input_paths(path_filename)
        stub = studio.InputsServiceStub(channel)
        path_inputs = []
        for path in paths:
            key = studio.InputsKey(
                studio_id=sid,
                workspace_id=MAINLINE_WS_ID,
                path=fmp.RepeatedString(values=path),
            )
            req = studio.InputsRequest(key=key)
            try:
                resp = await stub.get_one(req, timeout=RPC_TIMEOUT)
            except GRPCError as err:
                if err.status == Status.NOT_FOUND:
                    raise InputPathNotFoundError(path) from None
                raise
            path_inputs.append({
                'path': path,
                'inputs': json.loads(resp.value.inputs),
            })
        output = path_inputs if multiple else path_inputs[0]
        with open(filename, 'w', encoding='utf8') as f:
            yaml.dump(output, f)
        return

    key = studio.InputsKey(studio_id=sid,
                           workspace_id=MAINLINE_WS_ID)
    pfilter = studio.Inputs(key=key)
    req = studio.InputsStreamRequest()
    req.partial_eq_filter.append(pfilter)
    stub = studio.InputsServiceStub(channel)
    mergedinputs = None
    async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
        path = resp.value.key.path.values
        split = json.loads(resp.value.inputs)
        mergedinputs = mergeInputs(mergedinputs, path, split)
    jsonPathInputs = {'path': [], 'inputs': mergedinputs}
    with open(filename, 'w', encoding='utf8') as f:
        yaml.dump(jsonPathInputs, f)


async def create_workspace(channel, workspace_name):
    '''
    Creates a workspace with a UUID using workspace_name
    as the display name. Returns the UUID.
    '''
    logger.info('Creating workspace "%s"', workspace_name)
    ws_id = str(uuid.uuid4())
    key = workspace.WorkspaceKey(workspace_id=ws_id)
    req = workspace.WorkspaceConfigSetRequest(
        value=workspace.WorkspaceConfig(
            key=key,
            display_name=workspace_name
        )
    )
    stub = workspace.WorkspaceConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)

    req = workspace.WorkspaceStreamRequest(
        partial_eq_filter=[
            workspace.Workspace(key=key)
        ]
    )
    stub = workspace.WorkspaceServiceStub(channel)
    logger.info('\tWaiting for workspace to become ready')
    async for res in stub.subscribe(req, timeout=RPC_TIMEOUT):
        if res.value.state == workspace.WorkspaceState.PENDING:
            logger.info('\tWorkspaceID created: %s', ws_id)
            return ws_id

    raise RuntimeError(f'Workspace {ws_id} did not become ready')


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
                    logger.warning('skipping invalid dynamic args values in '
                                   'action-file: %s', aline)
                    continue

                # Create the action dictionary
                dyn_dict = {}
                for j, dyn_name in enumerate(dyn_names):
                    dyn_dict[dyn_name] = aline[j]

                dyn_values.append(dyn_dict)

    except FileNotFoundError:
        logger.error("The file '%s' was not found.", filename)
        return [], []
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        return [], []

    # if path and no args required,
    # append one empty args entry to still trigger one action
    if input_path and len(dyn_values) == 0:
        dyn_values.append({})
    return input_path, dyn_names, dyn_values


async def update_inputs_via_autofill(channel, ws_id, path, dyn_names, dyn_value):
    '''
    Sets inputs to the studio using autofill action.
    '''
    exec_id = str(uuid.uuid4())
    dynamicArgs = {
        "InputPath": path,
        "StudioID": studio_id,
        "WorkspaceID": ws_id,
    }
    for dyn_name in dyn_names:
        dynamicArgs[dyn_name] = dyn_value.get(dyn_name)

    run_config = action.ActionRunConfig(
        key=action.ActionRunKey(run_id=exec_id),
        action_id=action_id,
        dynamic_args=action.ActionArgValues(
            values={k: action.ActionArgValue(value=v) for k, v in dynamicArgs.items()}
        )
    )
    req = action.ActionRunConfigSetRequest(value=run_config)
    stub = action.ActionRunConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('Studio inputs set from autofill action:'
                '\n\t%s', dyn_value)

    # Subscribe to action run to wait for completion.
    sub_req = action.ActionRunStreamRequest(
        partial_eq_filter=[
            action.ActionRun(key=action.ActionRunKey(run_id=exec_id))
        ]
    )
    run_stub = action.ActionRunServiceStub(channel)
    async for res in run_stub.subscribe(sub_req, timeout=RPC_TIMEOUT):
        if res.value.error and res.value.error != "":
            logger.error('autofill failed with error:'
                         '\n\t%s', res.value.error)
            break
        if res.value.is_finished:
            logger.info('\tautofill succeeded')
            break


async def update_inputs_via_yaml(channel, ws_id, filename, dev_ids):
    '''
    Adds or removes studio inputs using the yaml file.
    Optionally assigns studio to a set of devices.

    Supports two formats:
    1. Single input update:
       path: [...]
       inputs: {...}

       Or removal:
       path: [...]
       remove: true

    2. Multiple input updates (list format):
       - path: [...]
         inputs: {...}
       - path: [...]
         remove: true
    '''
    # convert YAML input file to json inputs.
    with open(f'{filename}', encoding='utf8') as f:
        config = yaml.safe_load(f)

    # Determine if this is a single input update or multiple updates.
    configs = []
    if isinstance(config, list):
        configs = config
        logger.info('Processing %d input updates from yaml file: %s',
                    len(configs), filename)
    elif isinstance(config, dict):
        configs = [config]
        logger.info('Processing single input update from yaml file: %s', filename)
    else:
        raise ValueError(f"Invalid YAML format in {filename}. "
                         "Expected an input update or a list of input updates.")

    # Process each input update in the order given.
    stub = studio.InputsConfigServiceStub(channel)
    for i, cfg in enumerate(configs, start=1):
        if not isinstance(cfg, dict) or 'path' not in cfg:
            raise ValueError(f"Invalid YAML format in {filename} "
                             f"for config at index {i}. "
                             "Expected a dict with a 'path' key.")

        has_inputs = 'inputs' in cfg
        remove = cfg.get('remove', False)
        if not isinstance(remove, bool):
            raise ValueError(f"Invalid YAML format in {filename} "
                             f"for config at index {i}. "
                             "The 'remove' value must be true or false.")
        if remove and has_inputs:
            raise ValueError(f"Invalid YAML format in {filename} "
                             f"for config at index {i}. "
                             "Do not specify 'inputs' with 'remove: true'.")
        if not remove and not has_inputs:
            raise ValueError(f"Invalid YAML format in {filename} "
                             f"for config at index {i}. "
                             "Specify 'inputs' unless 'remove' is true.")

        path = cfg['path']
        if (not isinstance(path, list)
                or not all(isinstance(elem, str) for elem in path)):
            raise ValueError(f"Invalid YAML format in {filename} "
                             f"for config at index {i}. "
                             "The 'path' value must be a list of strings.")
        key = studio.InputsKey(
            workspace_id=ws_id,
            studio_id=studio_id,
            path=fmp.RepeatedString(values=path)
        )
        if remove:
            value = studio.InputsConfig(
                key=key,
                remove=True
            )
            operation = 'removed'
        else:
            value = studio.InputsConfig(
                key=key,
                inputs=json.dumps(cfg['inputs'])
            )
            operation = 'set'

        req = studio.InputsConfigSetRequest(
            value=value
        )
        await stub.set(req, timeout=RPC_TIMEOUT)
        logger.info('\tStudio inputs %s (%d/%d) - path: %s',
                    operation, i, len(configs), path)

    logger.info('All studio input updates applied from yaml: %s', filename)

    if not assign_studio:
        return

    # Assign the studio to the given set of devices.
    req = studio.AssignedTagsConfigSetRequest(
        value=studio.AssignedTagsConfig(
            key=studio.StudioKey(
                workspace_id=ws_id,
                studio_id=studio_id
            ),
            query=f'device:{",".join(dev_ids)}'
        )
    )
    stub = studio.AssignedTagsConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('\tDevices assigned to studio: %s', dev_ids)


async def build_workspace(channel, ws_id):
    '''
    Sends a request to build a workspace, waits for it
    to finish, and reports the result. Returns True if
    the build was successful and False otherwise.
    '''
    logger.info('Building workspace')
    # Send a request to build the workspace.
    build_id = str(uuid.uuid4())
    req = workspace.WorkspaceConfigSetRequest(
        value=workspace.WorkspaceConfig(
            key=workspace.WorkspaceKey(
                workspace_id=ws_id
            ),
            request=workspace.Request.START_BUILD,
            request_params=workspace.RequestParams(
                request_id=build_id
            )
        )
    )
    stub = workspace.WorkspaceConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('\tBuild request %s sent', build_id)
    # Wait until the workspace build request finishes.
    req = workspace.WorkspaceStreamRequest(
        partial_eq_filter=[
            workspace.Workspace(
                key=workspace.WorkspaceKey(
                    workspace_id=ws_id,
                )
            )
        ]
    )
    stub = workspace.WorkspaceServiceStub(channel)
    logger.info('\tWaiting for build to complete')
    async for res in stub.subscribe(req, timeout=BUILD_TIMEOUT):
        if build_id in res.value.responses.values:
            build_res = res.value.responses.values[build_id]
            break
    if build_res.status == workspace.ResponseStatus.FAIL:
        # Get the workspace build details.
        fail_msg = await build_failure_message(channel, ws_id, build_id)
        logger.error('\tBuild failed:\n%s', fail_msg)
        return False
    if build_res.status == workspace.ResponseStatus.SUCCESS:
        logger.info('\tBuild succeeded')
        return True
    logger.error('\tBuild failed')
    return False


async def build_failure_message(channel, ws_id, build_id):
    fail_msg = ''
    details_req = workspace.WorkspaceBuildDetailsStreamRequest(
        partial_eq_filter=[
            workspace.WorkspaceBuildDetails(
                key=workspace.WorkspaceBuildDetailsKey(
                    workspace_id=ws_id,
                    build_id=build_id
                )
            )
        ]
    )
    details_stub = workspace.WorkspaceBuildDetailsServiceStub(channel)
    async for resp in details_stub.get_all(details_req, timeout=RPC_TIMEOUT):
        result = resp.value
        dev_id = result.key.device_id
        if result.state == workspace.BuildState.FAIL:
            fail_msg += f'\t\tDevice {dev_id}:\n'
            if result.stage == workspace.BuildStage.INPUT_VALIDATION:
                fail_msg += '\t\t\tInput validation:\n'
                for sid, ivr in result.input_validation_results.values.items():
                    fail_msg += f'\t\t\t\tStudio: {sid}\n'
                    schema_errs = ivr.input_schema_errors.values
                    if len(schema_errs) > 0:
                        fail_msg += '\t\t\t\tInput schema errors:\n'
                    for i, err in enumerate(schema_errs, start=1):
                        fail_msg += f'\t\t\t\t\t--- # {i}\n'
                        fail_msg += f'\t\t\t\t\tField ID: {err.field_id}\n'
                        fail_msg += f'\t\t\t\t\tPath: {err.path.values}\n'
                        fail_msg += f'\t\t\t\t\tMembers: {err.members.values}\n'
                        fail_msg += f'\t\t\t\t\tDetails: {err.message}\n'
                    value_errs = ivr.input_value_errors.values
                    if len(value_errs) > 0:
                        fail_msg += '\t\t\t\tInput value errors:\n'
                    for i, err in enumerate(value_errs, start=1):
                        fail_msg += f'\t\t\t\t\t--- # {i}\n'
                        fail_msg += f'\t\t\t\t\tField ID: {err.field_id}\n'
                        fail_msg += f'\t\t\t\t\tPath: {err.path.values}\n'
                        fail_msg += f'\t\t\t\t\tMembers: {err.members.values}\n'
                        fail_msg += f'\t\t\t\t\tDetails: {err.message}\n'
                    other_errs = ivr.other_errors.values
                    if len(other_errs) > 0:
                        fail_msg += '\t\t\t\tOther errors:\n'
                    for i, err in enumerate(other_errs, start=1):
                        fail_msg += f'\t\t\t\t\t--- # {i}\n'
                        fail_msg += f'\t\t\t\t\t{err}\n'
            if result.stage == workspace.BuildStage.CONFIGLET_BUILD:
                fail_msg += '\t\t\tConfiglet compilation:\n'
                for sid, cbr in result.configlet_build_results.values.items():
                    fail_msg += f'\t\t\t\tStudio: {sid}\n'
                    templ_errs = cbr.template_errors.values
                    if len(templ_errs) > 0:
                        fail_msg += '\t\t\t\tTemplate errors:\n'
                    for i, err in enumerate(templ_errs, start=1):
                        fail_msg += f'\t\t\t\t\t--- # {i}\n'
                        fail_msg += f'\t\t\t\t\tLine number: {err.line_num}\n'
                        fail_msg += f'\t\t\t\t\tException: {err.exception}\n'
                        fail_msg += f'\t\t\t\t\tDetails: {err.detail}\n'
                    if cbr.other_error:
                        fail_msg += f'\t\t\t\tOther error: {cbr.other_error}\n'
            if result.stage == workspace.BuildStage.CONFIG_VALIDATION:
                fail_msg += '\t\t\tConfiglet validation:\n'
                errs = result.config_validation_result.errors.values
                if len(errs) > 0:
                    fail_msg += '\t\t\t\tErrors:\n'
                for i, err in enumerate(errs, start=1):
                    fail_msg += f'\t\t\t\t\t--- # {i}\n'
                    fail_msg += f'\t\t\t\t\tCode: {err.error_code}\n'
                    fail_msg += f'\t\t\t\t\tConfiglet: {err.configlet_name}\n'
                    fail_msg += f'\t\t\t\t\tLine number: {err.line_num}\n'
                    fail_msg += f'\t\t\t\t\tDetails: {err.error_msg}\n'
    return fail_msg


async def synchronize_workspace(channel, ws_id):
    '''
    Sends a request to synchronize a workspace with the latest
    mainline content, waits for it to finish, and reports the result.
    Returns True if the synchronization was successful and False otherwise.
    '''
    logger.info('Synchronizing workspace with mainline')
    # Check if workspace needs rebase by getting current workspace state
    get_req = workspace.WorkspaceRequest(
        key=workspace.WorkspaceKey(
            workspace_id=ws_id
        )
    )
    stub = workspace.WorkspaceServiceStub(channel)
    workspace_resp = await stub.get_one(get_req, timeout=RPC_TIMEOUT)

    # Check if rebase is needed
    if not workspace_resp.value.needs_rebase:
        logger.info('\tWorkspace is already up to date, no rebase needed')
        return True

    logger.info('\tWorkspace needs rebase, proceeding with synchronization')
    sync_id = str(uuid.uuid4())
    req = workspace.WorkspaceConfigSetRequest(
        value=workspace.WorkspaceConfig(
            key=workspace.WorkspaceKey(
                workspace_id=ws_id
            ),
            request=workspace.Request.REBASE,
            request_params=workspace.RequestParams(
                request_id=sync_id
            )
        )
    )
    stub = workspace.WorkspaceConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('\tSynchronization request %s sent', sync_id)
    # Wait until the workspace sync request finishes.
    req = workspace.WorkspaceStreamRequest(
        partial_eq_filter=[
            workspace.Workspace(
                key=workspace.WorkspaceKey(
                    workspace_id=ws_id,
                )
            )
        ]
    )
    stub = workspace.WorkspaceServiceStub(channel)
    logger.info('\tWaiting for synchronization to complete')
    async for res in stub.subscribe(req, timeout=SYNC_TIMEOUT):
        if sync_id in res.value.responses.values:
            sync_res = res.value.responses.values[sync_id]
            if sync_res.status == workspace.ResponseStatus.FAIL:
                logger.error('\tSynchronization failed: %s', sync_res.message)
                return False
            if sync_res.status == workspace.ResponseStatus.SUCCESS:
                logger.info('\tSynchronization succeeded')
                if get_sync_diffs:
                    await download_sync_diffs(channel, ws_id, res.value.last_rebased_at)
                return True
    logger.error('\tSynchronization failed')
    return False


async def download_sync_diffs(channel, ws_id, last_rebased_at=None):
    '''
    Downloads synchronization diffs for a workspace and saves them to a file.
    Returns True if successful, False otherwise.
    '''
    filename = f'{ws_id}_sync_diffs.yaml'
    logger.info('\tDownloading sync diffs...')
    try:
        req = workspace.WorkspaceDiffsStreamRequest(
            partial_eq_filter=[
                workspace.WorkspaceDiffs(
                    key=workspace.DiffKey(
                        workspace_id=ws_id,
                        diff_type=workspace.DiffType.REBASE
                    )
                )
            ]
        )
        stub = workspace.WorkspaceDiffsServiceStub(channel)
        diffs_data = []
        async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
            response_dict = resp.to_dict()
            if 'value' in response_dict:
                diffs_data.append(response_dict['value'])
        with open(filename, 'w', encoding='utf8') as f:
            yaml.dump(diffs_data, f, default_flow_style=False)
        logger.info('\tSync diffs saved to %s', filename)
        return True
    except Exception as e:
        logger.error('\tFailed to download sync diffs: %s', e)
        return False


async def submit_workspace(channel, ws_id):
    '''
    Sends a request to submit a workspace, waits for it to
    finish, and reports the result. Returns a tuple of:
    (cc_ids, submitted, sync_required) where:
    - cc_ids: List of change control IDs (or None if failed)
    - submitted: Boolean indicating if submission succeeded
    - sync_required: Boolean indicating if synchronization is required
    '''
    logger.info('Submitting workspace')
    # Send a request to submit the workspace.
    submit_id = str(uuid.uuid4())
    req = workspace.WorkspaceConfigSetRequest(
        value=workspace.WorkspaceConfig(
            key=workspace.WorkspaceKey(
                workspace_id=ws_id
            ),
            request=workspace.Request.SUBMIT,
            request_params=workspace.RequestParams(
                request_id=submit_id
            )
        )
    )
    stub = workspace.WorkspaceConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('\tSubmission request %s sent', submit_id)
    # Wait until the submission request finishes.
    req = workspace.WorkspaceStreamRequest(
        partial_eq_filter=[
            workspace.Workspace(
                key=workspace.WorkspaceKey(
                    workspace_id=ws_id,
                )
            )
        ]
    )
    stub = workspace.WorkspaceServiceStub(channel)
    logger.info('\tWaiting for submission to complete')
    async for res in stub.subscribe(req, timeout=RPC_TIMEOUT):
        if submit_id in res.value.responses.values:
            submit_res = res.value.responses.values[submit_id]
            if submit_res.status == workspace.ResponseStatus.FAIL:
                # Check for synchronization requirement first
                if submit_res.code == workspace.ResponseCode.SYNCHRONIZATION_REQUIRED:
                    logger.warning('\tSubmission requires synchronization: %s',
                                   submit_res.message)
                    return None, False, True
                # Then handle general failure
                logger.error('\tSubmission failed: %s', submit_res.message)
                return None, False, False
            # Now handle success
            if submit_res.status == workspace.ResponseStatus.SUCCESS:
                logger.info('\tSubmission succeeded')
        if res.value.state == workspace.WorkspaceState.SUBMITTED:
            return res.value.cc_ids.values, True, False
    logger.error('\tSubmission failed')
    return None, False, False


async def get_earlier_change_controls(channel, my_timestamp):
    '''
    Query all CCs that:
    1. Were created before my_timestamp
    2. Are still pending, approved, or running (not completed/cancelled)
    3. Were created by studio_update.py (name contains CHANGE_SIGNATURE)

    Returns a list of earlier CCs that are still active.
    '''
    stub = changecontrol.ChangeControlServiceStub(channel)

    # Query CCs with active statuses (server-side filter to reduce data transfer)
    # We still need to filter by timestamp and name client-side
    req = changecontrol.ChangeControlStreamRequest(
        partial_eq_filter=[
            changecontrol.ChangeControl(
                status=changecontrol.ChangeControlStatus.NOT_STARTED
            ),
            changecontrol.ChangeControl(
                status=changecontrol.ChangeControlStatus.SCHEDULED
            ),
            changecontrol.ChangeControl(
                status=changecontrol.ChangeControlStatus.RUNNING
            )
        ]
    )

    earlier_ccs = []

    try:
        async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
            cc_data = resp.value
            cc_timestamp = cc_data.creation.time

            # Check if this CC was created before mine
            # aristaproto converts Timestamp to datetime, so we can compare directly
            is_earlier = cc_timestamp < my_timestamp

            if not is_earlier:
                continue

            # Only consider CCs created by studio_update.py
            # These have CHANGE_SIGNATURE in their name
            cc_name = cc_data.change.name if cc_data.change and cc_data.change.name else ""
            if CHANGE_SIGNATURE not in cc_name:
                continue

            # Status already filtered server-side, so we can add directly
            earlier_ccs.append(cc_data)
    except Exception as e:
        logger.warning('\tError querying earlier CCs: %s', e)
        return []

    return earlier_ccs


async def wait_for_earlier_change_controls(channel, my_timestamp):
    '''
    Wait until all CCs created before this one have completed.
    This ensures CCs execute in creation order.

    This is best-effort: on timeout, proceed anyway to avoid deadlock.
    '''
    if not CC_ORDERING_ENABLED:
        return

    logger.info('\tChecking for earlier change controls...')

    for iteration in range(MAX_CC_WAIT_ITERATIONS):
        # Get all pending and running CCs created before mine
        earlier_ccs = await get_earlier_change_controls(channel, my_timestamp)

        if not earlier_ccs:
            # No earlier CCs pending/running, safe to proceed
            if iteration == 0:
                logger.info('\tNo earlier CCs blocking execution')
            else:
                logger.info('\tAll earlier CCs completed, proceeding with execution')
            return

        # Log waiting status with CC names
        earlier_cc_info = [(cc.key.id, cc.change.name if cc.change else 'unknown')
                           for cc in earlier_ccs]
        if len(earlier_cc_info) <= 3:
            logger.info('\tWaiting for %d earlier CC(s): %s',
                        len(earlier_ccs), [name for _, name in earlier_cc_info])
        else:
            logger.info('\tWaiting for %d earlier CC(s): %s ... and %d more',
                        len(earlier_ccs), [name for _, name in earlier_cc_info[:3]],
                        len(earlier_ccs) - 3)

        # Wait before next check
        await asyncio.sleep(CC_POLL_INTERVAL)

    # Timeout waiting for earlier CCs
    max_wait_time = MAX_CC_WAIT_ITERATIONS * CC_POLL_INTERVAL
    logger.warning('Timeout waiting for earlier CCs after %ds, proceeding anyway',
                   max_wait_time)


async def run_change_control(channel, cc_id):
    '''
    Approves and starts a change control, waits for it to finish,
    and reports the result. Returns True if execution was successful
    and False otherwise.

    If CC_ORDERING_ENABLED is True, waits for all earlier CCs to complete
    before executing this one.
    '''
    logger.info('Executing change control %s', cc_id)
    key = changecontrol.ChangeControlKey(
        id=cc_id
    )

    # Get this CC's creation timestamp for ordering
    req = changecontrol.ChangeControlRequest(key=key)
    stub = changecontrol.ChangeControlServiceStub(channel)
    res = await stub.get_one(req)

    my_timestamp = res.value.creation.time
    my_cc_name = res.value.change.name if res.value.change else "unknown"
    logger.info('\tCC "%s" created at: %s', my_cc_name, my_timestamp)

    # Best-effort wait for all earlier CCs to complete,
    # if ordering is enabled
    await wait_for_earlier_change_controls(channel, my_timestamp)

    # Now safe to proceed with approval and execution
    # Approve the change control
    req = changecontrol.ApproveConfigSetRequest(
        value=changecontrol.ApproveConfig(
            key=key,
            approve=changecontrol.FlagConfig(
                value=True
            ),
            version=res.time
        )
    )
    stub = changecontrol.ApproveConfigServiceStub(channel)
    await stub.set(req)
    logger.info('\tChange control approved')
    # Send a request to start the change control.
    req = changecontrol.ChangeControlConfigSetRequest(
        value=changecontrol.ChangeControlConfig(
            key=key,
            start=changecontrol.FlagConfig(
                value=True
            )
        )
    )
    stub = changecontrol.ChangeControlConfigServiceStub(channel)
    await stub.set(req)
    logger.info('\tChange control flagged to start')
    # Wait until the change control completes execution.
    req = changecontrol.ChangeControlStreamRequest(
        partial_eq_filter=[
            changecontrol.ChangeControl(key=key)
        ]
    )
    stub = changecontrol.ChangeControlServiceStub(channel)
    logger.info('\tWaiting for execution to complete')
    async for res in stub.subscribe(req, timeout=CC_EXECUTION_TIMEOUT):
        if res.value.status == changecontrol.ChangeControlStatus.COMPLETED:
            if res.value.error and res.value.error != "":
                logger.error('\tExecution failed: %s', res.value.error)
                return False
            logger.info('\tExecution succeeded')
            return True
    logger.error('\tExecution failed')
    return False


async def main(args, client):
    with client as channel:
        # Get Inputs
        if args.operation == 'get':
            filename = f'{studio_id}-inputs.yaml'
            path_filename = args.yaml_file.name if args.yaml_file else None
            await get_inputs(channel, filename, path_filename)
            logger.info('Mainline inputs have been written to: %s', filename)
            return
        # Set Inputs in Multiple Steps
        # Create a workspace.
        workspace_name = f'{studio_id} {CHANGE_SIGNATURE}'
        if args.wsid:
            ws_id = args.wsid
        else:
            ws_id = await create_workspace(channel, workspace_name)
        # Update the studio with yaml file
        inputSet = False
        actionInvoked = False
        if args.yaml_file:
            await update_inputs_via_yaml(
                channel, ws_id, args.yaml_file.name, "*")
            inputSet = True
        # Update the studio with autofill action
        dyn_values = []
        if args.action_file:
            input_path, dyn_names, dyn_values = getActionTriggers(args.action_file.name)
        for dyn_value in dyn_values:
            await update_inputs_via_autofill(
                channel, ws_id, input_path, dyn_names, dyn_value)
            actionInvoked = True
        if not inputSet and not actionInvoked:
            return
        # Synchronize workspace if requested (before build)
        if args.sync:
            if not await synchronize_workspace(channel, ws_id):
                return

        # Build-submit loop with synchronization retry
        sync_retry_count = 0
        cc_ids = None

        while sync_retry_count <= MAX_SYNC_RETRIES:
            # Build the workspace.
            if not await build_workspace(channel, ws_id):
                return

            # Stop here if --build-only.
            if args.build_only:
                return

            # Submit the workspace.
            cc_ids, submitted, sync_required = await submit_workspace(channel, ws_id)

            if not submitted:
                if sync_required and sync_retry_count < MAX_SYNC_RETRIES:
                    logger.info('Synchronization required. Retry attempt %d of %d',
                                sync_retry_count + 1, MAX_SYNC_RETRIES)
                    # Perform synchronization
                    if not await synchronize_workspace(channel, ws_id):
                        logger.error('Synchronization failed during retry')
                        return
                    # Increment retry counter and loop back to rebuild
                    sync_retry_count += 1
                    continue
                else:
                    # Either not sync-related failure, or max retries exceeded
                    if sync_required and sync_retry_count >= MAX_SYNC_RETRIES:
                        logger.error('Maximum synchronization retries (%d) exceeded',
                                     MAX_SYNC_RETRIES)
                    return

            # Success - break out of retry loop
            break

        # Stop here if --submit-only.
        if args.submit_only:
            logger.info('%s change control(s) created', len(cc_ids))
            logger.info('Change control IDs: %s', cc_ids)
            return
        # Execute the spawned change control.
        logger.info('%s change control(s) created', len(cc_ids))
        for cc_id in cc_ids:
            await run_change_control(channel, cc_id)


def check_cloudvision_version():
    from importlib.metadata import version as pkg_version
    MIN_VERSION = (1, 29, 1)
    cv_version = pkg_version("cloudvision")
    logger.info("cloudvision package version: %s", cv_version)
    version_tuple = tuple(int(x) for x in cv_version.split(".")[:3])
    if version_tuple < MIN_VERSION:
        min_ver_str = ".".join(str(x) for x in MIN_VERSION)
        logger.error("cloudvision >= %s is required (found %s).", min_ver_str, cv_version)
        logger.error("  Please upgrade:  pip install --upgrade cloudvision")
        logger.error("  Alternatively, use the older version of the script from"
                     " branches older than v1.29.1")
        sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S')
    check_cloudvision_version()
    desc = (
        "1. Get studio inputs from mainline.\n"
        "   Example:\n"
        "     python3 studio_update.py --server=192.0.2.10:443\n"
        "            --token-file=token.tok\n"
        "            --operation=get --studio-id=studio-evpn-services\n"
        "   Optionally get inputs at paths specified in a YAML file:\n"
        "            --yaml-file=studio-evpn-services-paths.yaml\n"
        "2. Set studio inputs using a YAML input file or autofill input file.\n"
        "   This will populate, build and submit the studio change.\n"
        "   Example:\n"
        "     python3 studio_update.py --server=192.0.2.10:443\n"
        "            --token-file=token.tok\n"
        "            --operation=set --studio-id=studio-evpn-services\n"
        "            --yaml-file=studio-evpn-services-inputs.yaml\n"
        "   Optionally to trigger action:\n"
        "            --action-file=actions.csv\n"
        "            --action-id=action-ports-table\n"
        "   Optionally to build only and not submit:\n"
        "            --build-only=True\n"
        "   Optionally to submit only and not execute the change controls:\n"
        "            --submit-only=True\n"
        "   Optionally to synchronize workspace with mainline before building:\n"
        "            --sync=True\n"
        "3. Inputs yaml file.\n"
        "   Example:\n"
        "   - path: ['tenants', '[name=Arista1]', 'vlans', '[vlanId=100]']\n"
        "     remove: true\n"
        "   - path: ['tenants', '[name=Arista1]', 'vlans', '[vlanId=101]']\n"
        "     inputs:\n"
        "       name: vlan101\n"
        "       vlanId: 101\n"
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
    parser.add_argument("--cert-file", type=str,
                        help="path to certificate file to use as root CA")
    parser.add_argument("--operation", choices=['set', 'get'], default='get',
                        help="whether to get or set inputs")
    parser.add_argument("--yaml-file", type=argparse.FileType('r'),
                        help=("YAML file containing studio inputs for set, "
                              "or input paths for get"))
    parser.add_argument("--action-file", type=argparse.FileType('r'),
                        help="csv file containing studio autofill inputs")
    parser.add_argument("--build-only", type=bool, default=False,
                        help="whether to stop after building the changes (no submission)")
    parser.add_argument("--submit-only", type=bool, default=False,
                        help="whether to stop after submitting the workspace "
                             "(no change control execution)")
    parser.add_argument("--studio-id", type=str, required=True,
                        help="ID of the Studio, e.g. studio-interface-v2-pkg")
    parser.add_argument("--action-id", type=str,
                        help="ID of the action, e.g. action-ports-table")
    parser.add_argument("--wsid", type=str, default=False,
                        help="existing workspace ID, if not wanting to create a new one")
    parser.add_argument("--sync", type=bool, default=False,
                        help="synchronize workspace with mainline before building")
    parser.add_argument("--insecure", action="store_true", default=False,
                        help="skip TLS certificate verification")
    pargs = parser.parse_args()
    studio_id = pargs.studio_id
    if pargs.action_id:
        action_id = pargs.action_id
    conn = create_client(pargs)
    try:
        asyncio.run(main(pargs, conn))
    except InputPathNotFoundError as err:
        logger.error("Studio inputs path does not exist: %s", err)
        sys.exit(1)
