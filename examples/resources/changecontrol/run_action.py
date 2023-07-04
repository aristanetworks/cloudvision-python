# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
#
# NOTE: Requires python 3.10 to run
#
# Create Change Control for specific action(s) and monitor for completion
# Example usage:
#  python3 run_action.py --server 192.0.2.100 --token-file token.txt \
#  --cert-file cvp.crt --action-args actionsAndArgs.json

import argparse
import grpc
from json import load
import logging
from typing import Dict
from uuid import uuid4

from arista.changecontrol.v1 import models, services
from fmp import wrappers_pb2 as fmp_wrappers
from google.protobuf import wrappers_pb2 as wrappers
from google.protobuf.timestamp_pb2 import Timestamp

RPC_TIMEOUT = 30  # in seconds

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


def createChannel(server, tokenFile, certFile) -> grpc.Channel:
    """
    Creates a grpc secure channel with the provided info

    Args:
        server: Address of the CV instance to create the channel to
        tokenFile: Path to a file containing a token
        certFile: Path to a file containing the cert (optional)

    Returns:
        grpc.Channel: Channel that rAPI stubs can use
    """

    # read the file containing a session token to authenticate with
    token = tokenFile.read().strip()
    # create the header object for the token
    callCreds = grpc.access_token_call_credentials(token)

    # if using a self-signed certificate (should be provided as arg)
    if certFile:
        # create the channel using the self-signed cert
        cert = certFile.read()
        channelCreds = grpc.ssl_channel_credentials(root_certificates=cert)
    else:
        # otherwise default to checking against CAs
        channelCreds = grpc.ssl_channel_credentials()
    connCreds = grpc.composite_channel_credentials(channelCreds, callCreds)

    # initialize a connection to the server using our connection settings (auth + TLS)
    return grpc.secure_channel(server, connCreds)


def addCC(channel: grpc.Channel, ccID: str,
          actionsAndArgs: Dict[str, Dict[str, str]]) -> Timestamp:
    """
    Creates a Change Control of the given ID and returns the Timestamp for approval

    Args:
        channel:        The GRPC channel that can be used by rAPI stubs
        ccID:           The ID of the Change Control to create
        actionsAndArgs: A string dictionary of the actions and their respective arguments.
                        The top level keys should be for each action in the order to be executed,
                        and each of the contents of those entries a str->str dictionary of
                        the arguments to be passed. Those actions without an empty entry will
                        not be provided arguments.
                        e.g. {"action1":{"DeviceID":"abc123"}, "action2":{}} schedules action1
                        and action2 in that order, with args provided to action1 only.

    Returns:
        Timestamp: Timestamp of the write that can be used to approve the CC
    """
    logging.info(f"Creating Change Control with ID {ccID}")
    ccName = "run_action script created change"
    rootStageId = "stage-root"
    rootStageRows = []
    stageConfigMapDict = {}
    for actionID, args in actionsAndArgs.items():
        currActionID = f"stage-action {actionID}"
        if args:
            action = models.Action(
                name=wrappers.StringValue(value=actionID),
                args=fmp_wrappers.MapStringString(values=args),
            )
        else:
            action = models.Action(
                name=wrappers.StringValue(value=actionID),
            )
        rootStageRows.append(fmp_wrappers.RepeatedString(values=[currActionID]))
        stageConfigMapDict[currActionID] = models.StageConfig(
            name=wrappers.StringValue(value=f"Scheduled action {actionID}"),
            action=action
        )

    stageConfigMapDict[rootStageId] = models.StageConfig(
        name=wrappers.StringValue(value=f"{ccName} Root"),
        rows=models.RepeatedRepeatedString(
            values=rootStageRows
        )
    )
    stageConfigMap = models.StageConfigMap(
        values=stageConfigMapDict
    )
    changeConfig = models.ChangeConfig(
        name=wrappers.StringValue(value=ccName),
        root_stage_id=wrappers.StringValue(value=rootStageId),
        stages=stageConfigMap,
        notes=wrappers.StringValue(value="Created and managed by script")
    )
    key = models.ChangeControlKey(id=wrappers.StringValue(value=ccID))
    setReq = services.ChangeControlConfigSetRequest(
        value=models.ChangeControlConfig(
            key=key,
            change=changeConfig,
        )
    )

    cc_stub = services.ChangeControlConfigServiceStub(channel)
    resp = cc_stub.Set(setReq, timeout=RPC_TIMEOUT)
    logging.info(f"Change Control {ccID} created successfully")
    return resp.time


def approveCC(channel: grpc.Channel, ccID: str, ts: Timestamp):
    """
    Approves a Change Control of the given ID and Timestamp

    Args:
        channel (grpc.Channel): The GRPC channel that can be used by rAPI stubs
        ccID (str): The ID of the Change Control to approve
        ts (Timestamp): The Timestamp of the Change Control to approve
    """
    logging.info(f"Approving Change Control with ID {ccID}")
    key = models.ChangeControlKey(id=wrappers.StringValue(value=ccID))
    setReq = services.ApproveConfigSetRequest(
        value=models.ApproveConfig(
            key=key,
            approve=models.FlagConfig(
                value=wrappers.BoolValue(value=True),
            ),
            # NOTE: TS needs to match that of the cc update in the DB
            version=ts
        )
    )

    cc_apr_stub = services.ApproveConfigServiceStub(channel)
    cc_apr_stub.Set(setReq, timeout=RPC_TIMEOUT)
    logging.info(f"Change Control {ccID} approved successfully")


def executeCC(channel: grpc.Channel, ccID: str):
    """
    Executes and approved Change Control of the given ID

    Args:
        channel (grpc.Channel): The GRPC channel that can be used by rAPI stubs
        ccID (str): The ID of the Change Control to approve
    """
    logging.info(f"Executing Change Control with ID {ccID}")
    key = models.ChangeControlKey(id=wrappers.StringValue(value=ccID))
    setReq = services.ChangeControlConfigSetRequest(
        value=models.ChangeControlConfig(
            key=key,
            start=models.FlagConfig(
                value=wrappers.BoolValue(value=True),
            ),
        )
    )
    cc_stub = services.ChangeControlConfigServiceStub(channel)
    cc_stub.Set(setReq, timeout=RPC_TIMEOUT)
    logging.info(f"Change Control {ccID} executed successfully")


def subscribeToCCStatus(channel: grpc.Channel, ccID: str):
    """
    Subscribes to a Change Control and monitors it until completion

    Args:
        channel (grpc.Channel): The GRPC channel that can be used by rAPI stubs
        ccID (str): The ID of the Change Control to approve
    """
    logging.info(f"Subscribing to {ccID} to monitor for completion")
    key = models.ChangeControlKey(id=wrappers.StringValue(value=ccID))
    subReq = services.ChangeControlStreamRequest()
    subReq.partial_eq_filter.append(models.ChangeControl(key=key))

    cc_stub = services.ChangeControlServiceStub(channel)
    for resp in cc_stub.Subscribe(subReq, timeout=RPC_TIMEOUT):
        if resp.value.status == models.CHANGE_CONTROL_STATUS_COMPLETED:
            if resp.value.error and resp.value.error.value:
                err = resp.value.error.value
                logging.info(f"Changecontrol {ccID} completed with error: {err}")
            else:
                logging.info(f"Changecontrol {ccID} completed successfully")
            break


def main(args):
    with createChannel(args.server, args.token_file, args.cert_file) as channel:
        ccID = str(uuid4())
        actionsAndArgs = load(open(args.action_args))
        ts = addCC(channel, ccID, actionsAndArgs)
        approveCC(channel, ccID, ts)
        executeCC(channel, ccID)
        subscribeToCCStatus(channel, ccID)


if __name__ == '__main__':
    ds = ("Create a change control for given actions and executes them"
          "Examples:\n"
          "python3 run_action.py --server 192.0.2.100 --token-file token.txt"
          "--cert-file cvp.crt --action-args actionsAndArgs.json")
    parser = argparse.ArgumentParser(
        description=ds,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--server', required=True,
        help="CloudVision server to connect to in <host>:<port> format")
    parser.add_argument(
        "--action-args", required=True,
        help=("path to json file of the actions and arguments to be run, e.g. actionsAndArgs.json."
              " Top level keys should be the action IDs, with each actionID entry containing"
              " the string arguments for that action. Actions will be executed serially in"
              " the order defined"))
    parser.add_argument(
        "--token-file", required=True,
        type=argparse.FileType('r'), help="file with access token")
    parser.add_argument(
        "--cert-file", type=argparse.FileType('rb'),
        help="(optional) certificate to use as root CA")
    args = parser.parse_args()
    main(args)
