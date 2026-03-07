#!/usr/bin/python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml",
#     "cloudvision>=1.28.0"
# ]
# ///

# Copyright (c) 2026 Arista Networks, Inc.  All rights reserved.
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
# Note:
#   It's necessary to first log onto the cvp and create a service account,
#   generate a token, and copy the token to a local token.tok file.
#   If this is for a cvp dut using self-signed certs use the --insecure flag
#   e.g:
#   python studio_onboarding.py
#      --server 10.83.12.79:443
#      --token-file token.tok
#      --insecure
#      --operation=set-all


import argparse
import asyncio
import json
import logging
import sys
import uuid

from cloudvision.api import client as cv_client
from cloudvision.api.arista.workspace import v1 as workspace
from cloudvision.api.arista.studio_topology import v1 as studio_topology

logger = logging.getLogger(__name__)

RPC_TIMEOUT = 600  # in seconds


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


async def create_workspace(channel, workspace_name):
    '''
    Creates a workspace with a UUID using workspace_name
    as the display name. Returns the UUID.
    '''
    logger.info('Creating workspace "%s"', workspace_name)
    workspace_id = str(uuid.uuid4())
    req = workspace.WorkspaceConfigSetRequest(
        value=workspace.WorkspaceConfig(
            key=workspace.WorkspaceKey(
                workspace_id=workspace_id
            ),
            display_name=workspace_name
        )
    )
    stub = workspace.WorkspaceConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('\tWorkspaceID created: %s', workspace_id)
    return workspace_id


async def build_workspace(channel, workspace_id):
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
                workspace_id=workspace_id
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
                    workspace_id=workspace_id,
                )
            )
        ]
    )
    stub = workspace.WorkspaceServiceStub(channel)
    logger.info('\tWaiting for build to complete')
    async for res in stub.subscribe(req, timeout=RPC_TIMEOUT):
        if build_id in res.value.responses.values:
            build_res = res.value.responses.values[build_id]
            break
    if build_res.status == workspace.ResponseStatus.FAIL:
        # Get the workspace build details.
        fail_msg = await build_failure_message(channel, workspace_id, build_id)
        logger.error('\tBuild failed:\n%s', fail_msg)
        return False
    if build_res.status == workspace.ResponseStatus.SUCCESS:
        logger.info('\tBuild succeeded')
        return True
    logger.error('\tBuild failed')
    return False


async def build_failure_message(channel, workspace_id, build_id):
    fail_msg = ''
    details_req = workspace.WorkspaceBuildDetailsStreamRequest(
        partial_eq_filter=[
            workspace.WorkspaceBuildDetails(
                key=workspace.WorkspaceBuildDetailsKey(
                    workspace_id=workspace_id,
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


async def submit_workspace(channel, workspace_id):
    '''
    Sends a request to submit a workspace, waits for it to
    finish, and reports the result. Returns the IDs of the
    spawned change controls.
    '''
    logger.info('Submitting workspace')
    # Send a request to submit the workspace.
    submit_id = str(uuid.uuid4())
    req = workspace.WorkspaceConfigSetRequest(
        value=workspace.WorkspaceConfig(
            key=workspace.WorkspaceKey(
                workspace_id=workspace_id
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
                    workspace_id=workspace_id,
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
                logger.error('\tSubmission failed: %s', submit_res.message)
                return None, False
            if submit_res.status == workspace.ResponseStatus.SUCCESS:
                logger.info('\tSubmission succeeded')
        if res.value.state == workspace.WorkspaceState.SUBMITTED:
            return res.value.cc_ids.values, True
    logger.error('\tSubmission failed')
    return None, False


async def main(args):

    with args._client as channel:
        workspace_name = "Accepting new devices and interfaces into I&T Studio"
        if args.wsid:
            workspace_id = args.wsid
        else:
            workspace_id = await create_workspace(channel, workspace_name)

        update_stub = studio_topology.UpdateServiceStub(channel)
        update_config_stub = studio_topology.UpdateConfigServiceStub(channel)

        if args.operation == 'get':
            req = studio_topology.UpdateStreamRequest(
                partial_eq_filter=[
                    studio_topology.Update(
                        status=studio_topology.UpdateStatus.NEW,
                        key=studio_topology.UpdateKey(
                            workspace_id=workspace_id
                        )
                    )
                ]
            )
            async for resp in update_stub.get_all(req, timeout=RPC_TIMEOUT):
                logger.info(resp.value.key.update_id)

        if args.operation == 'set-all':
            req = studio_topology.UpdateStreamRequest(
                partial_eq_filter=[
                    studio_topology.Update(
                        status=studio_topology.UpdateStatus.NEW,
                        key=studio_topology.UpdateKey(
                            workspace_id=workspace_id
                        )
                    )
                ]
            )
            async for resp in update_stub.get_all(req, timeout=RPC_TIMEOUT):
                update_id = resp.value.key.update_id
                set_req = studio_topology.UpdateConfigSetRequest(
                    value=studio_topology.UpdateConfig(
                        status=studio_topology.UpdateStatus.ACCEPTED,
                        key=studio_topology.UpdateKey(
                            workspace_id=workspace_id,
                            update_id=update_id
                        )
                    )
                )
                await update_config_stub.set(set_req, timeout=RPC_TIMEOUT)

        if args.operation == 'set':
            if not args.update_id:
                logger.error('update ID is required for set operation')
                return
            update_id = args.update_id
            set_req = studio_topology.UpdateConfigSetRequest(
                value=studio_topology.UpdateConfig(
                    status=studio_topology.UpdateStatus.ACCEPTED,
                    key=studio_topology.UpdateKey(
                        workspace_id=workspace_id,
                        update_id=update_id
                    )
                )
            )
            await update_config_stub.set(set_req, timeout=RPC_TIMEOUT)

        # Build the workspace.
        if not await build_workspace(channel, workspace_id):
            return
        # Stop here if --build-only.
        if args.build_only:
            return
        # Submit the workspace.
        cc_ids, submitted = await submit_workspace(channel, workspace_id)
        if not submitted:
            return


def check_cloudvision_version():
    from importlib.metadata import version as pkg_version
    MIN_VERSION = (1, 28, 0)
    cv_version = pkg_version("cloudvision")
    logger.info("cloudvision package version: %s", cv_version)
    version_tuple = tuple(int(x) for x in cv_version.split(".")[:3])
    if version_tuple < MIN_VERSION:
        min_ver_str = ".".join(str(x) for x in MIN_VERSION)
        logger.error("cloudvision >= %s is required (found %s).", min_ver_str, cv_version)
        logger.error("  Please upgrade:  pip install --upgrade cloudvision")
        logger.error("  Alternatively, use the older version of the script from"
                     " branches older than v1.28.0")
        sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    check_cloudvision_version()
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--server',
        required=True,
        help="CloudVision server to connect to in <host>:<port> format")
    parser.add_argument("--token-file", required=True,
                        type=argparse.FileType('r'), help="file with access token")
    parser.add_argument("--cert-file", type=str,
                        help="path to certificate file to use as root CA")
    parser.add_argument("--wsid", type=str, default=False,
                        help="existing workspace ID, if not wanting to create a new one")
    parser.add_argument("--operation", choices=['set', 'get', 'set-all'], default='get',
                        help="whether to get or set inputs")
    parser.add_argument("--update-id", type=str,
                        default=False, help="Update ID from UpdateService call to set")
    parser.add_argument("--build-only", type=bool, default=False,
                        help="whether to stop after building the changes (no submission)")
    parser.add_argument("--insecure", action="store_true", default=False,
                        help="skip TLS certificate verification")
    args = parser.parse_args()
    args._client = create_client(args)
    asyncio.run(main(args))
