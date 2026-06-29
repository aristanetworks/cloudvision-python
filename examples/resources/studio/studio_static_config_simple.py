#!/usr/bin/env python3

# Create containers, and assigns static configlets to devices in the CVP Studio Static Configuration.
#
# Prerequisites:
#   pip install "cloudvision>=1.29.1" pyyaml
#
# Usage:
#   1. List existing configlets and assignments:
#      python3 studio_static_config_simple.py \
#          --server 192.0.2.10:443 --token-file token.tok --insecure \
#          --operation get
#
#   2. Assign configlets defined in INVENTORY below:
#      python3 studio_static_config_simple.py \
#          --server 192.0.2.10:443 --token-file token.tok --insecure \
#          --operation set
#
#   Add --build-only to stop after building (no submission).


# Container paths use "/" to express nesting: "US/DC1" means DC1
# is a child of US.  Shared intermediate nodes (e.g. two devices both
# under "US/DC1" and "US/DC2") are created only once.
#
# "containers" can carry their own configlets that apply to all
# devices matched by the container query # (default 
# "location: <name-of-the-container>").
# "devices" carry per-device configlets and are placed under a
# container when "container" is specified.
#
# Each configlet entry supports three modes:
#   {"name": "x", "configlet_file": "path"}  → create from file
#   {"name": "x"}                            → look up by name on CV (should exist already)

# Warning: the script will re-create the container hierarchy from scratch every time the script is run.
# Thus, as it is, it does not support managing extra containers 'inside' what is defined in the script. 
# i.e. in the example below, if I create manually a 'US/DC3' container it will be deleted next time the 
# script is run. 
# However, it's possible to create a container outside of the 'US' hierarchy. 
# i.e. if I create a container 'France/DC3' using the UI, this will not be touched by the script.   
INVENTORY = {
    "containers": [
        {
            "name": "US/DC1",
            "configlets": [
                {"name": "ntp_dc1", "configlet_file": "configlets/ntp_dc1.cfg"},
            ],
        },
    ],
    "devices": [
        {
            "device_id": "JPE21231033",
            "container": "US/DC1",
            "configlets": [
                {"name": "leaf1", "configlet_file": "configlets/leaf1.cfg"},
                # {"name": "leaf1_exception", }
            ],
        },
        {
            "device_id": "JPE21231032",
            "container": "US/DC2",
            "configlets": [
                {"name": "leaf2", "configlet_file": "configlets/leaf2.cfg"},
                # {"name": "leaf2_exception"},
            ],
        },
    ],
}


import argparse
import asyncio
import json
import logging
import sys
import uuid
from uuid import uuid5, NAMESPACE_URL
from cloudvision.api import client as cv_client
from cloudvision.api import fmp
from cloudvision.api.arista.workspace import v1 as workspace
from cloudvision.api.arista.studio import v1 as studio
from cloudvision.api.arista.configlet import v1 as configlet
from cloudvision.api.arista.tag import v2 as tag
from cloudvision.cvlib.constants import MAINLINE_WS_ID

logger = logging.getLogger(__name__)

STATIC_CONFIGLET_STUDIO_ID = "studio-static-configlet"
RPC_TIMEOUT = 30
BUILD_TIMEOUT = 300

ID_NAMESPACE = uuid5(NAMESPACE_URL, 'assign-static-configlet')



def create_client(args):
    token = args.token_file.read().strip()
    host_parts = args.server.split(':')
    host = host_parts[0]
    port = int(host_parts[1]) if len(host_parts) > 1 else 443
    return cv_client.AsyncCVClient.from_token(
        token=token, host=host, port=port,
        cacert=args.cert_file, insecure=args.insecure,
    )


# ── GET: list existing configlets & assignments ──────────────────────


async def get_configlets_and_assignments(channel):
    stub = configlet.ConfigletServiceStub(channel)
    req = configlet.ConfigletStreamRequest(
        partial_eq_filter=[
            configlet.Configlet(
                key=configlet.ConfigletKey(workspace_id=MAINLINE_WS_ID)
            )
        ]
    )
    print("=== Existing Configlets ===")
    async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
        c = resp.value
        print(f"  ID:   {c.key.configlet_id}")
        print(f"  Name: {c.display_name}")
        body_preview = (c.body[:100] + '...') if c.body and len(c.body) > 100 else (c.body or '(empty)')
        print(f"  Body: {body_preview}")
        print()

    stub2 = configlet.ConfigletAssignmentServiceStub(channel)
    req2 = configlet.ConfigletAssignmentStreamRequest(
        partial_eq_filter=[
            configlet.ConfigletAssignment(
                key=configlet.ConfigletAssignmentKey(workspace_id=MAINLINE_WS_ID)
            )
        ]
    )
    print("=== Existing Assignments ===")
    async for resp in stub2.get_all(req2, timeout=RPC_TIMEOUT):
        a = resp.value
        print(f"  Assignment ID:  {a.key.configlet_assignment_id}")
        print(f"  Name:           {a.display_name}")
        print(f"  Query:          {a.query}")
        print(f"  Configlet IDs:  {a.configlet_ids.values}")
        print()


# ── GET studio inputs (configletAssignmentRoots) ─────────────────────


async def get_studio_inputs(channel):
    key = studio.InputsKey(
        studio_id=STATIC_CONFIGLET_STUDIO_ID,
        workspace_id=MAINLINE_WS_ID,
    )
    req = studio.InputsStreamRequest()
    req.partial_eq_filter.append(studio.Inputs(key=key))
    stub = studio.InputsServiceStub(channel)
    merged = None
    async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
        path = resp.value.key.path.values
        split = json.loads(resp.value.inputs)
        if not path:
            merged = split if merged is None else {**(merged or {}), **split}
        else:
            if merged is None:
                merged = {}
            merged['/'.join(path)] = split
    return merged


# ── Workspace lifecycle ──────────────────────────────────────────────


async def create_workspace(channel, name):
    ws_id = str(uuid.uuid4())
    req = workspace.WorkspaceConfigSetRequest(
        value=workspace.WorkspaceConfig(
            key=workspace.WorkspaceKey(workspace_id=ws_id),
            display_name=name,
        )
    )
    stub = workspace.WorkspaceConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('Workspace created: %s', ws_id)
    return ws_id


async def build_workspace(channel, ws_id):
    build_id = str(uuid.uuid4())
    req = workspace.WorkspaceConfigSetRequest(
        value=workspace.WorkspaceConfig(
            key=workspace.WorkspaceKey(workspace_id=ws_id),
            request=workspace.Request.START_BUILD,
            request_params=workspace.RequestParams(request_id=build_id),
        )
    )
    stub = workspace.WorkspaceConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('Build request %s sent', build_id)

    req = workspace.WorkspaceStreamRequest(
        partial_eq_filter=[
            workspace.Workspace(
                key=workspace.WorkspaceKey(workspace_id=ws_id)
            )
        ]
    )
    stub = workspace.WorkspaceServiceStub(channel)
    logger.info('Waiting for build to complete...')
    async for res in stub.subscribe(req, timeout=BUILD_TIMEOUT):
        if build_id in res.value.responses.values:
            build_res = res.value.responses.values[build_id]
            break

    if build_res.status == workspace.ResponseStatus.SUCCESS:
        logger.info('Build succeeded')
        return True

    logger.error('Build failed')
    fail_msg = await get_build_failure_message(channel, ws_id, build_id)
    if fail_msg:
        logger.error('Build details:\n%s', fail_msg)
    return False


async def get_build_failure_message(channel, ws_id, build_id):
    fail_msg = ''
    req = workspace.WorkspaceBuildDetailsStreamRequest(
        partial_eq_filter=[
            workspace.WorkspaceBuildDetails(
                key=workspace.WorkspaceBuildDetailsKey(
                    workspace_id=ws_id,
                    build_id=build_id,
                )
            )
        ]
    )
    stub = workspace.WorkspaceBuildDetailsServiceStub(channel)
    async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
        result = resp.value
        if result.state == workspace.BuildState.FAIL:
            dev_id = result.key.device_id
            fail_msg += f'  Device {dev_id}:\n'
            if result.stage == workspace.BuildStage.INPUT_VALIDATION:
                fail_msg += '    Input validation errors:\n'
                for sid, ivr in result.input_validation_results.values.items():
                    for err in ivr.input_schema_errors.values:
                        fail_msg += f'      Schema: {err.message}\n'
                    for err in ivr.input_value_errors.values:
                        fail_msg += f'      Value: {err.message}\n'
                    for err in ivr.other_errors.values:
                        fail_msg += f'      Other: {err}\n'
            if result.stage == workspace.BuildStage.CONFIGLET_BUILD:
                fail_msg += '    Configlet compilation errors:\n'
                for sid, cbr in result.configlet_build_results.values.items():
                    for err in cbr.template_errors.values:
                        fail_msg += f'      Line {err.line_num}: {err.exception}\n'
            if result.stage == workspace.BuildStage.CONFIG_VALIDATION:
                fail_msg += '    Config validation errors:\n'
                for err in result.config_validation_result.errors.values:
                    fail_msg += f'      {err.configlet_name} line {err.line_num}: {err.error_msg}\n'
    return fail_msg


async def submit_workspace(channel, ws_id):
    submit_id = str(uuid.uuid4())
    req = workspace.WorkspaceConfigSetRequest(
        value=workspace.WorkspaceConfig(
            key=workspace.WorkspaceKey(workspace_id=ws_id),
            request=workspace.Request.SUBMIT,
            request_params=workspace.RequestParams(request_id=submit_id),
        )
    )
    stub = workspace.WorkspaceConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('Submission request %s sent', submit_id)

    req = workspace.WorkspaceStreamRequest(
        partial_eq_filter=[
            workspace.Workspace(
                key=workspace.WorkspaceKey(workspace_id=ws_id)
            )
        ]
    )
    stub = workspace.WorkspaceServiceStub(channel)
    logger.info('Waiting for submission to complete...')
    async for res in stub.subscribe(req, timeout=RPC_TIMEOUT):
        if submit_id in res.value.responses.values:
            submit_res = res.value.responses.values[submit_id]
            if submit_res.status == workspace.ResponseStatus.FAIL:
                logger.error('Submission failed: %s', submit_res.message)
                return None, False
            if submit_res.status == workspace.ResponseStatus.SUCCESS:
                logger.info('Submission succeeded')
        if res.value.state == workspace.WorkspaceState.SUBMITTED:
            return res.value.cc_ids.values, True
    logger.error('Submission failed')
    return None, False


# ── SET: create configlet, assignment, update studio inputs ──────────


async def get_configlet_name_to_id(channel):
    """Build a display_name -> configlet_id map from mainline."""
    stub = configlet.ConfigletServiceStub(channel)
    req = configlet.ConfigletStreamRequest(
        partial_eq_filter=[
            configlet.Configlet(
                key=configlet.ConfigletKey(workspace_id=MAINLINE_WS_ID)
            )
        ]
    )
    name_map = {}
    async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
        c = resp.value
        name_map[c.display_name] = c.key.configlet_id
    return name_map


async def resolve_configlet(channel, ws_id, entry, existing_configlets):
    """Return the configlet ID for an INVENTORY entry.

    - ``configlet_file`` given → create a new configlet from the file.
    - name-only → look up an existing configlet by display name.
    """
    if "configlet_file" in entry:
        with open(entry["configlet_file"]) as f:
            configlet_body = f.read()
        return await create_configlet(channel, ws_id, entry["name"], configlet_body)

    cid = existing_configlets.get(entry["name"])
    if cid is None:
        raise ValueError(
            f'Configlet "{entry["name"]}" not found on CloudVision '
            f'and no configlet_file or configlet_id provided'
        )
    logger.info('Resolved existing configlet "%s" -> %s', entry["name"], cid)
    return cid


async def create_configlet(channel, ws_id, configlet_name, configlet_body):
    configlet_id = str(uuid5(ID_NAMESPACE, f'configlet:{configlet_name}'))
    req = configlet.ConfigletConfigSetRequest(
        value=configlet.ConfigletConfig(
            key=configlet.ConfigletKey(
                workspace_id=ws_id,
                configlet_id=configlet_id,
            ),
            display_name=configlet_name,
            body=configlet_body,
        )
    )
    stub = configlet.ConfigletConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('Configlet created: %s (ID: %s)', configlet_name, configlet_id)
    return configlet_id


async def create_assignment(channel, ws_id, device_id, device_query, configlet_ids):
    assignment_id = str(uuid5(ID_NAMESPACE, f'assignment:{device_id}'))
    req = configlet.ConfigletAssignmentConfigSetRequest(
        value=configlet.ConfigletAssignmentConfig(
            key=configlet.ConfigletAssignmentKey(
                workspace_id=ws_id,
                configlet_assignment_id=assignment_id,
            ),
            query=device_query,
            configlet_ids=fmp.RepeatedString(values=configlet_ids),
            match_policy=configlet.MatchPolicy.MATCH_FIRST,
        )
    )
    stub = configlet.ConfigletAssignmentConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('Assignment created: %s -> %s (ID: %s)',
                device_query, configlet_ids, assignment_id)
    return assignment_id


async def create_container(channel, ws_id, container_id, display_name,
                           child_assignment_ids, configlet_ids=None):
    req = configlet.ConfigletAssignmentConfigSetRequest(
        value=configlet.ConfigletAssignmentConfig(
            key=configlet.ConfigletAssignmentKey(
                workspace_id=ws_id,
                configlet_assignment_id=container_id,
            ),
            display_name=display_name,
            description=f'Container created by assign_static_configlet.py',
            query=f'location:{display_name}',
            configlet_ids=fmp.RepeatedString(values=configlet_ids or []),
            child_assignment_ids=fmp.RepeatedString(values=child_assignment_ids),
            match_policy=configlet.MatchPolicy.MATCH_FIRST,
        )
    )
    stub = configlet.ConfigletAssignmentConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('Container created: %s (ID: %s) with %d children',
                display_name, container_id, len(child_assignment_ids))


async def update_studio_roots(channel, ws_id, new_assignment_ids):
    current_inputs = await get_studio_inputs(channel)
    existing_roots = current_inputs.get('configletAssignmentRoots', []) if current_inputs else []
    existing_set = set(existing_roots)
    updated_roots = existing_roots + [aid for aid in new_assignment_ids if aid not in existing_set]

    inputs_json = json.dumps({"configletAssignmentRoots": updated_roots})
    req = studio.InputsConfigSetRequest(
        value=studio.InputsConfig(
            key=studio.InputsKey(
                workspace_id=ws_id,
                studio_id=STATIC_CONFIGLET_STUDIO_ID,
                path=fmp.RepeatedString(values=[]),
            ),
            inputs=inputs_json,
        )
    )
    stub = studio.InputsConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('Studio inputs updated with assignment roots: %s', updated_roots)


# ── Tags: create and assign location tags to devices ────────────────


async def create_tag_if_needed(channel, ws_id, label, value, created_tags):
    """Create a tag (label:value) unless already created in this run."""
    if (label, value) in created_tags:
        return
    req = tag.TagConfigSetRequest(
        value=tag.TagConfig(
            key=tag.TagKey(
                workspace_id=ws_id,
                element_type=tag.ElementType.DEVICE,
                label=label,
                value=value,
            ),
        )
    )
    stub = tag.TagConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    created_tags.add((label, value))
    logger.info('Tag created: %s:%s', label, value)


async def assign_tag_to_device(channel, ws_id, device_id, label, value):
    req = tag.TagAssignmentConfigSetRequest(
        value=tag.TagAssignmentConfig(
            key=tag.TagAssignmentKey(
                workspace_id=ws_id,
                element_type=tag.ElementType.DEVICE,
                label=label,
                value=value,
                device_id=device_id,
            ),
        )
    )
    stub = tag.TagAssignmentConfigServiceStub(channel)
    await stub.set(req, timeout=RPC_TIMEOUT)
    logger.info('Tag %s:%s assigned to device %s', label, value, device_id)


# ── Main ─────────────────────────────────────────────────────────────


async def main(args, client):
    with client as channel:

        if args.operation == 'get':
            await get_configlets_and_assignments(channel)
            inputs = await get_studio_inputs(channel)
            print("=== Studio Inputs (configletAssignmentRoots) ===")
            print(f"  {json.dumps(inputs, indent=2)}")
            return

        # --- SET: assign configlets to devices and containers ---
        devices = INVENTORY.get("devices", [])
        containers = INVENTORY.get("containers", [])
        if not devices and not containers:
            logger.error('INVENTORY is empty, nothing to do')
            sys.exit(1)

        ws_parts = []
        if devices:
            ws_parts.append(', '.join(d["device_id"] for d in devices))
        if containers:
            ws_parts.append(', '.join(c["name"] for c in containers))
        ws_name = f'Assign configlets to {"; ".join(ws_parts)}'
        ws_id = await create_workspace(channel, ws_name)

        # Fetch existing configlets once so name-only entries can be resolved.
        existing_configlets = await get_configlet_name_to_id(channel)

        # ── Build the container tree from INVENTORY paths ──
        #
        # Each node in the tree tracks its own child container nodes,
        # the device assignment IDs that land directly on it, and
        # configlet IDs assigned to the container itself.
        # A path like "DC1/France" produces two nodes:
        #   ""     (virtual root)  ->  children: {"DC1": node}
        #   "DC1"                  ->  children: {"France": node}
        #   "DC1/France"           ->  device_assignment_ids: [...]
        #
        # After all devices are processed the tree is walked bottom-up
        # so that each container's child_assignment_ids are known before
        # its own ConfigletAssignment is created on CloudVision.

        def _container_id_for_path(path):
            return str(uuid5(ID_NAMESPACE, f'container:{path}'))

        tree = {}          # path -> {"children": {}, "device_ids": [], "configlet_ids": []}
        root_children = {} # name -> path   (top-level containers)

        def _ensure_path(path):
            if path in tree:
                return
            tree[path] = {"children": {}, "device_ids": [], "configlet_ids": []}
            parts = path.split("/")
            if len(parts) == 1:
                root_children[parts[0]] = path
                return
            parent_path = "/".join(parts[:-1])
            _ensure_path(parent_path)
            tree[parent_path]["children"][parts[-1]] = path

        root_assignment_ids = []

        # ── Create / resolve configlets for containers ──
        for container in containers:
            container_path = container["name"]
            _ensure_path(container_path)
            for entry in container.get("configlets", []):
                cid = await resolve_configlet(
                    channel, ws_id, entry, existing_configlets
                )
                tree[container_path]["configlet_ids"].append(cid)

        # ── Create / resolve configlets and assignments for devices ──
        for device in devices:
            device_id = device["device_id"]
            device_query = f'device:{device_id}'

            configlet_ids = []
            for entry in device["configlets"]:
                cid = await resolve_configlet(
                    channel, ws_id, entry, existing_configlets
                )
                configlet_ids.append(cid)

            assignment_id = await create_assignment(
                channel, ws_id, device_id, device_query, configlet_ids
            )

            if "container" in device:
                container_path = device["container"]
                _ensure_path(container_path)
                tree[container_path]["device_ids"].append(assignment_id)
            else:
                root_assignment_ids.append(assignment_id)

        # ── Assign container location tags to devices ──
        # Each segment of a device's container path becomes a
        # location:<segment> tag on that device, so the container
        # queries (location:<name>) match correctly.
        created_tags = set()
        for device in devices:
            if "container" not in device:
                continue
            parts = device["container"].split("/")
            for part in parts:
                await create_tag_if_needed(
                    channel, ws_id, "location", part, created_tags
                )
                await assign_tag_to_device(
                    channel, ws_id, device["device_id"], "location", part
                )

        # Walk every path bottom-up (longest paths first) so children
        # are created before their parents.
        for path in sorted(tree, key=lambda p: p.count("/"), reverse=True):
            node = tree[path]
            child_assignment_ids = (
                [_container_id_for_path(cp) for cp in node["children"].values()]
                + node["device_ids"]
            )
            display_name = path.split("/")[-1]
            await create_container(
                channel, ws_id,
                _container_id_for_path(path),
                display_name,
                child_assignment_ids,
                configlet_ids=node["configlet_ids"],
            )

        # Only true roots go into configletAssignmentRoots.
        for path in root_children.values():
            root_assignment_ids.append(_container_id_for_path(path))

        await update_studio_roots(channel, ws_id, root_assignment_ids)

        if not await build_workspace(channel, ws_id):
            return

        if args.build_only:
            logger.info('Build-only mode, stopping here. Workspace ID: %s', ws_id)
            return

        cc_ids, submitted = await submit_workspace(channel, ws_id)
        if not submitted:
            return
        logger.info('%d change control(s) created: %s', len(cc_ids), cc_ids)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%H:%M:%S',
    )

    parser = argparse.ArgumentParser(
        description='Assign static configlets to devices via CVP Studio API.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'Examples:\n'
            '  # List existing configlets and assignments:\n'
            '  python3 assign_static_configlet.py \\\n'
            '      --server 192.0.2.10:443 --token-file token.tok --insecure \\\n'
            '      --operation get\n\n'
            '  # Assign configlets defined in INVENTORY:\n'
            '  python3 assign_static_configlet.py \\\n'
            '      --server 192.0.2.10:443 --token-file token.tok --insecure \\\n'
            '      --operation set\n'
        ),
    )
    parser.add_argument('--server', required=True,
                        help='CVP server in <host>:<port> format')
    parser.add_argument('--token-file', required=True, type=argparse.FileType('r'),
                        help='File containing the service account token')
    parser.add_argument('--cert-file', type=str, default=None,
                        help='Path to CA certificate file')
    parser.add_argument('--insecure', action='store_true', default=False,
                        help='Skip TLS certificate verification')
    parser.add_argument('--operation', choices=['get', 'set'], default='get',
                        help='get: list configlets/assignments; set: assign configlets')
    parser.add_argument('--build-only', action='store_true', default=False,
                        help='Stop after building (no submission)')

    args = parser.parse_args()
    client = create_client(args)
    asyncio.run(main(args, client))

