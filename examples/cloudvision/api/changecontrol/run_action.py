#!/usr/bin/env python
# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
#
# NOTE: Requires python 3.10 to run
#
# Create Change Control for specific action(s) and monitor for completion
# Example usage:
#  python3 run_action.py --server 192.0.2.100 --token-file token.txt \
#    --action-args actionsAndArgs.json
import asyncio

import argparse
import datetime
from json import load
import logging
from typing import Dict
from uuid import uuid4

from cloudvision.api import client as cv_client
from cloudvision.api.arista.changecontrol import v1 as changecontrol
from cloudvision.api import fmp

from grpclib import client as grpc_client


RPC_TIMEOUT = 30  # in seconds

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


def createChannel(server, tokenFile) -> grpc_client.Channel:
    # read the file containing a session token to authenticate with
    token = tokenFile.read().strip()
    return cv_client.AsyncCVClient.from_token(token, server)


async def addCC(channel: grpc_client.Channel, ccID: str,
                actionsAndArgs: Dict[str, Dict[str, str]]) -> datetime.datetime:
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
                        and action2 in that order, with args provided to action1 only. (NOTE:
                        "action" key should be action ID, e.g "bcPGQ4iQp81d6W7uomB0K")

    Returns:
        Timestamp: Timestamp of the write that can be used to approve the CC
    """
    logging.info("Creating Change Control with ID %s", ccID)
    ccName = "run_action script created change"
    rootStageId = "stage-root"
    rootStageRows = []
    stageConfigMapDict = {}
    for actionID, args in actionsAndArgs.items():
        currActionID = f"stage-action {actionID}"
        if args:
            action = changecontrol.Action(
                name=actionID,
                args=fmp.MapStringString(values=args),
            )
        else:
            action = changecontrol.Action(
                name=actionID,
            )
        rootStageRows.append(fmp.RepeatedString(values=[currActionID]))
        stageConfigMapDict[currActionID] = changecontrol.StageConfig(
            name=f"Scheduled action {actionID}",
            action=action
        )

    stageConfigMapDict[rootStageId] = changecontrol.StageConfig(
        name=f"{ccName} Root",
        rows=changecontrol.RepeatedRepeatedString(
            values=rootStageRows
        )
    )
    stageConfigMap = changecontrol.StageConfigMap(
        values=stageConfigMapDict
    )
    changeConfig = changecontrol.ChangeConfig(
        name=ccName,
        root_stage_id=rootStageId,
        stages=stageConfigMap,
        notes="Created and managed by script"
    )
    key = changecontrol.ChangeControlKey(id=ccID)
    setReq = changecontrol.ChangeControlConfigSetRequest(
        value=changecontrol.ChangeControlConfig(
            key=key,
            change=changeConfig,
        )
    )

    cc_stub = changecontrol.ChangeControlConfigServiceStub(channel)
    resp = await cc_stub.set(setReq, timeout=RPC_TIMEOUT)
    logging.info("Change Control %s created successfully", ccID)
    return resp.time


async def approveCC(channel: grpc_client.Channel, ccID: str, ts: datetime.datetime):
    """
    Approves a Change Control of the given ID and Timestamp

    Args:
        channel (grpc.Channel): The GRPC channel that can be used by rAPI stubs
        ccID (str): The ID of the Change Control to approve
        ts (Timestamp): The Timestamp of the Change Control to approve
    """
    logging.info("Approving Change Control with ID %s", ccID)
    key = changecontrol.ChangeControlKey(id=ccID)
    setReq = changecontrol.ApproveConfigSetRequest(
        value=changecontrol.ApproveConfig(
            key=key,
            approve=changecontrol.FlagConfig(
                value=True,
            ),
            # NOTE: TS needs to match that of the cc update in the DB
            version=ts
        )
    )

    cc_apr_stub = changecontrol.ApproveConfigServiceStub(channel)
    await cc_apr_stub.set(setReq, timeout=RPC_TIMEOUT)
    logging.info("Change Control %s approved successfully", ccID)


async def executeCC(channel: grpc_client.Channel, ccID: str):
    """
    Executes and approved Change Control of the given ID

    Args:
        channel (grpc.Channel): The GRPC channel that can be used by rAPI stubs
        ccID (str): The ID of the Change Control to approve
    """
    logging.info("Executing Change Control with ID %s", ccID)
    key = changecontrol.ChangeControlKey(id=ccID)
    setReq = changecontrol.ChangeControlConfigSetRequest(
        value=changecontrol.ChangeControlConfig(
            key=key,
            start=changecontrol.FlagConfig(
                value=True,
            ),
        )
    )
    cc_stub = changecontrol.ChangeControlConfigServiceStub(channel)
    await cc_stub.set(setReq, timeout=RPC_TIMEOUT)
    logging.info("Change Control %s executed successfully", ccID)


async def subscribeToCCStatus(channel: grpc_client.Channel, ccID: str):
    """
    Subscribes to a Change Control and monitors it until completion

    Args:
        channel (grpc.Channel): The GRPC channel that can be used by rAPI stubs
        ccID (str): The ID of the Change Control to approve
    """
    logging.info("Subscribing to %s to monitor for completion", ccID)
    key = changecontrol.ChangeControlKey(id=ccID)
    subReq = changecontrol.ChangeControlStreamRequest()
    subReq.partial_eq_filter.append(changecontrol.ChangeControl(key=key))

    cc_stub = changecontrol.ChangeControlServiceStub(channel)
    async for resp in cc_stub.subscribe(subReq, timeout=RPC_TIMEOUT):
        if resp.value.status == changecontrol.ChangeControlStatus.COMPLETED:
            if resp.value.error and resp.value.error:
                err = resp.value.error
                logging.info("Changecontrol %s completed with error: %s", ccID, err)
            else:
                logging.info("Changecontrol %s completed successfully", ccID)
            break


async def main(args):
    with createChannel(args.server, args.token_file) as channel:
        ccID = str(uuid4())
        actionsAndArgs = load(open(args.action_args))
        ts = await addCC(channel, ccID, actionsAndArgs)
        await approveCC(channel, ccID, ts)
        await executeCC(channel, ccID)
        await subscribeToCCStatus(channel, ccID)


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
    args = parser.parse_args()
    asyncio.run(main(args))
