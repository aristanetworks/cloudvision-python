# Copyright (c) 2021 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec import Wildcard, Path
from utils import pretty_print
from parser import base
import json

debug = False


def get(client, dataset, pathElts):
    ''' Returns a query on a path element'''
    result = {}
    query = [
        create_query([(pathElts, [])], dataset)
    ]

    for batch in client.get(query):
        for notif in batch["notifications"]:
            if debug:
                pretty_print(notif["updates"])
            result.update(notif["updates"])
    return result


def deviceBugCount(client):
    pathElts = [
        "BugAlerts",
        "DevicesBugsCount"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def deviceBugs(client):
    pathElts = [
        "tags",
        "BugAlerts",
        "devices"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def getBugInfo(client, bugId, mem=dict()):
    if bugId in mem:
        return mem[bugId]
    pathElts = [
        "BugAlerts",
        "bugs",
        bugId
    ]
    dataset = "analytics"
    bugInfo = get(client, dataset, pathElts)
    mem[bugId] = bugInfo

    return bugInfo


def getSwitchesInfo(client):
    pathElts = [
        "DatasetInfo",
        "Devices"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def main(apiserverAddr, token=None, certs=None, key=None, ca=None):

    with GRPCClient(apiserverAddr, token=token, key=key,
                    ca=ca, certs=certs) as client:
        bugCount = deviceBugCount(client)
        datasetInfo = getSwitchesInfo(client)
        print("Report #1 - BugCount\n")
        print(f"{'Device SN':<50}{'Number of bugs':<50}")
        for k, v in bugCount.items():
            print(f"{k:<50}{v:<50}")
        devices = deviceBugs(client)
        print("\nReport #2 - CVEs\n")
        print(f"{'Device Hostname':<30}{'EOS Version':<30}{'CVEs':<30}")
        for k, v in devices.items():
            cve_list = []
            for bug in v:
                bugId = getBugInfo(client, bug)
                if 'CVE' in bugId['cve']:
                    cve_list.append(bugId['cve'])
            hostname = datasetInfo[k]['hostname']
            version = datasetInfo[k]['eosVersion']
            print(f"{hostname:<30}{version:<30}{','.join([str(elem) for elem in cve_list]):<30}")
        print("\nReport #3 - Bugs\n")
        for k, v in devices.items():
            hostname = datasetInfo[k]['hostname']
            version = datasetInfo[k]['eosVersion']
            print(f"{hostname:<30}{version:<30}{','.join([str(elem) for elem in v]):<30}")

    return 0


if __name__ == "__main__":
    args = base.parse_args()
    exit(main(args.apiserver, certs=args.certFile, key=args.keyFile,
              ca=args.caFile, token=args.tokenFile))
