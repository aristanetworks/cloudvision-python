# Copyright (c) 2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
#
# Create and Assign Tags
# Tag creation is necessary before Tag assignment
# Example usage:
#  python3 manage_tags.py --server 192.0.2.79:443 --token-file token.txt \
#  --cert-file cvp.crt --file tags.yaml --create-and-assign
#  python3 manage_tags.py --server 192.0.2.79:443 --token-file token.txt \
#  --cert-file cvp.crt --file tags.yaml --create
#  python3 manage_tags.py --server 192.0.2.79:443 --token-file token.txt \
#  --cert-file cvp.crt --file tags.yaml --assign
#  python3 manage_tags.py --server 192.0.2.79:443 --token-file token.txt \
#  --cert-file cvp.crt --file tags.yaml --unassign

import argparse
import json
import uuid
import grpc
import yaml
import copy

from arista.workspace.v1 import models as workspace_models
from arista.workspace.v1 import services as workspace_services

# import the tags models and services
import arista.tag.v2
from google.protobuf import wrappers_pb2 as wrappers
from google.protobuf.json_format import Parse

RPC_TIMEOUT = 30  # in seconds

payload_template = {
    "value": {
        "key": {
            "workspaceId": "",
            "elementType": 2,
            "label": "",
            "value": "",
        }
    }
}


def create_workspace(channel, workspace_name):
    """
    Creates a workspace with a UUID using workspace_name
    as the display name. Returns the UUID.
    """
    print(f'Creating workspace "{workspace_name}"')

    workspace_id = str(uuid.uuid4())
    req = workspace_services.WorkspaceConfigSetRequest(
        value=workspace_models.WorkspaceConfig(
            key=workspace_models.WorkspaceKey(
                workspace_id=wrappers.StringValue(value=workspace_id)
            ),
            display_name=wrappers.StringValue(value=workspace_name),
        )
    )
    stub = workspace_services.WorkspaceConfigServiceStub(channel)
    stub.Set(req, timeout=RPC_TIMEOUT)
    print(f"\tWorkspace {workspace_id} created")
    return workspace_id


def build_workspace(channel, workspace_id):
    """
    Sends a request to build a workspace, waits for it
    to finish, and reports the result. Returns True if
    the build was successful and False otherwise.
    """
    print("Building workspace")

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
            ),
        )
    )
    stub = workspace_services.WorkspaceConfigServiceStub(channel)
    stub.Set(req, timeout=RPC_TIMEOUT)
    print(f"\tBuild request {build_id} sent")

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
    print("\tWaiting for build to complete")
    for res in stub.Subscribe(req, timeout=RPC_TIMEOUT):
        if build_id in res.value.responses.values:
            build_res = res.value.responses.values[build_id]
            break
    if build_res.status == workspace_models.RESPONSE_STATUS_FAIL:

        # Get the workspace build results.
        req = workspace_services.WorkspaceBuildRequest(
            key=workspace_models.WorkspaceBuildKey(
                workspace_id=wrappers.StringValue(value=workspace_id),
                build_id=wrappers.StringValue(value=build_id),
            )
        )
        stub = workspace_services.WorkspaceBuildServiceStub(channel)
        res = stub.GetOne(req, timeout=RPC_TIMEOUT)
        print("\tBuild failed")
        return False
    if build_res.status == workspace_models.RESPONSE_STATUS_SUCCESS:
        print("\tBuild succeeded")
        return True


def submit_workspace(channel, workspace_id):
    """
    Sends a request to submit a workspace, waits for it to
    finish, and reports the result. Returns the IDs of the
    spawned change controls.
    """
    print("Submitting workspace")

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
            ),
        )
    )
    stub = workspace_services.WorkspaceConfigServiceStub(channel)
    stub.Set(req, timeout=RPC_TIMEOUT)
    print(f"\tSubmission request {submit_id} sent")

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
    print("\tWaiting for submission to complete")
    for res in stub.Subscribe(req, timeout=RPC_TIMEOUT):
        if submit_id in res.value.responses.values:
            submit_res = res.value.responses.values[submit_id]
            if submit_res.status == workspace_models.RESPONSE_STATUS_FAIL:
                print(f"\tSubmission failed: {submit_res.message.value}")
                return None, False
            if submit_res.status == workspace_models.RESPONSE_STATUS_SUCCESS:
                print("\tSubmission succeeded")
        if res.value.state == workspace_models.WORKSPACE_STATE_SUBMITTED:
            return res.value.cc_ids.values, True


def create_tags(channel, json_request):
    """
    Create tags
    """
    req = Parse(json_request, arista.tag.v2.services.TagConfigSetRequest(), False)
    tag_stub = arista.tag.v2.services.TagConfigServiceStub(channel)
    tag_stub.Set(req, timeout=RPC_TIMEOUT)


def assign_tags(channel, json_request):
    """
    Assign tags
    """
    req = Parse(
        json_request,
        arista.tag.v2.services.TagAssignmentConfigSetRequest(),
        False,
    )

    tag_stub = arista.tag.v2.services.TagAssignmentConfigServiceStub(channel)
    tag_stub.Set(req, timeout=RPC_TIMEOUT)


def main(args):
    """
    Main function to create tags
    """
    # read the file containing a session token to authenticate with
    token = args.token_file.read().strip()
    # create the header object for the token
    callCreds = grpc.access_token_call_credentials(token)

    # if using a self-signed certificate (should be provided as arg)
    if args.cert_file:
        # create the channel using the self-signed cert
        cert = args.cert_file.read()
        channelCreds = grpc.ssl_channel_credentials(root_certificates=cert)
    else:
        # otherwise default to checking against CAs
        channelCreds = grpc.ssl_channel_credentials()
    connCreds = grpc.composite_channel_credentials(channelCreds, callCreds)

    if args.file:
        filename = args.file
    else:
        filename = "tags.yaml"
    with open(filename, "r") as file:
        tags = yaml.safe_load(file)

    # initialize a connection to the server using our connection settings (auth + TLS)
    with grpc.secure_channel(args.server, connCreds) as channel:
        # Create a workspace.
        workspace_name = "Override LLDP tags"
        workspace_id = create_workspace(channel, workspace_name)
        if "device_tags" in tags["tags"]:
            for tag in tags["tags"]["device_tags"]:
                payload = copy.deepcopy(payload_template)
                payload["value"]["key"]["workspaceId"] = workspace_id
                payload["value"]["key"]["label"] = tag["label"]
                payload["value"]["key"]["value"] = tag["value"]
                payload["value"]["key"]["elementType"] = 1
                json_request = json.dumps(payload)
                if args.create:
                    create_tags(channel, json_request)
                elif args.assign:
                    payload["value"]["key"]["deviceId"] = tag["device_id"]
                    json_request = json.dumps(payload)
                    assign_tags(channel, json_request)
                elif args.unassign:
                    payload["value"]["key"]["deviceId"] = tag["device_id"]
                    payload["value"]["remove"] = True
                    json_request = json.dumps(payload)
                    assign_tags(channel, json_request)
                elif args.create_and_assign:
                    create_tags(channel, json_request)
                    payload["value"]["key"]["deviceId"] = tag["device_id"]
                    json_request = json.dumps(payload)
                    assign_tags(channel, json_request)
        if "interface_tags" in tags["tags"]:
            for tag in tags["tags"]["interface_tags"]:
                payload = copy.deepcopy(payload_template)
                payload["value"]["key"]["workspaceId"] = workspace_id
                payload["value"]["key"]["label"] = tag["label"]
                payload["value"]["key"]["value"] = tag["value"]
                payload["value"]["key"]["elementType"] = 2
                json_request = json.dumps(payload)
                if args.create:
                    create_tags(channel, json_request)
                elif args.assign:
                    payload["value"]["key"]["deviceId"] = tag["device_id"]
                    payload["value"]["key"]["interfaceId"] = tag["interface_id"]
                    json_request = json.dumps(payload)
                    assign_tags(channel, json_request)
                elif args.unassign:
                    payload["value"]["key"]["deviceId"] = tag["device_id"]
                    payload["value"]["key"]["interfaceId"] = tag["interface_id"]
                    payload["value"]["remove"] = True
                    json_request = json.dumps(payload)
                    assign_tags(channel, json_request)
                elif args.create_and_assign:
                    create_tags(channel, json_request)
                    payload["value"]["key"]["deviceId"] = tag["device_id"]
                    payload["value"]["key"]["interfaceId"] = tag["interface_id"]
                    json_request = json.dumps(payload)
                    assign_tags(channel, json_request)
        elif len(tags["tags"]) == 0:
            print("No tags found in the tags.yaml file")
            return
        # Build the workspace.
        if not build_workspace(channel, workspace_id):
            return
        # Submit the workspace.
        submit_workspace(channel, workspace_id)


if __name__ == "__main__":
    ds = (
        "Create interface or device tags "
        "Examples:\n"
        "python3 manage_tags.py --server 192.0.2.79:443 --token-file token.txt"
        '--cert-file cvp.crt --file tags.yaml"'
    )
    parser = argparse.ArgumentParser(
        description=ds, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--server",
        required=True,
        help="CloudVision server to connect to in <host>:<port> format",
    )
    parser.add_argument(
        "--token-file",
        required=True,
        type=argparse.FileType("r"),
        help="file with access token",
    )
    parser.add_argument(
        "--cert-file",
        type=argparse.FileType("rb"),
        help="certificate to use as root CA",
    )
    parser.add_argument(
        "--file",
        required=True,
        help="yaml file containing the tags to create and assign",
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create tags",
    )
    parser.add_argument(
        "--assign",
        action="store_true",
        help="Create tags",
    )
    parser.add_argument(
        "--unassign",
        action="store_true",
        help="Create tags",
    )
    parser.add_argument(
        "--create-and-assign",
        action="store_true",
        help="Create tags",
    )
    args = parser.parse_args()
    main(args)
