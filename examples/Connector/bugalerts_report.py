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


def getDeviceLifecycles(client):
    pathElts = [
        "lifecycles",
        "devices",
        "hardware"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def getDeviceLifecyclesSW(client):
    pathElts = [
        "lifecycles",
        "devices",
        "software"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def main(apiserverAddr, token=None, certs=None, key=None, ca=None):

    with GRPCClient(apiserverAddr, token=token, key=key,
                    ca=ca, certs=certs) as client:
        hw_eol = getDeviceLifecycles(client)
        sw_eol = getDeviceLifecyclesSW(client)
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

        print("\nReport #4 - Lifecycle statements - End of Life\n")
        print(f"{'Hostname':<40}{'Serial number':<40}{'Model':<40}{'End of Life':<40}")

        for k, v in hw_eol.items():
            hostname = datasetInfo[k]['hostname']
            eol_date = v['endOfLife']['date']
            eol_model_temp = v['endOfLife']['models']
            eol_model = []
            for km, vm in eol_model_temp.items():
                eol_model.append(km + "(" + str(vm) + ")")
            eol_mod = ", ".join(eol_model)
            print(f"{hostname:<40}{k:<40}{str(eol_mod):<40}{eol_date:<40}")

        print("\nReport #5 - Lifecycle statements - End of Sale\n")
        print(f"{'Hostname':<40}{'Serial number':<40}{'Model':<40}{'End of Sale':<40}")
        for k, v in hw_eol.items():
            hostname = datasetInfo[k]['hostname']
            eos_date = v['endOfSale']['date']
            eos_model_temp = v['endOfSale']['models']
            eos_model = []
            for km, vm in eos_model_temp.items():
                eos_model.append(km + "(" + str(vm) + ")")
            eos_mod = ", ".join(eos_model)
            print(f"{hostname:<40}{k:<40}{str(eos_mod):<40}{eos_date:<40}")

        print("\nReport #6 - Lifecycle statements - End of TAC Suppor\n")
        print(f"{'Hostname':<40}{'Serial number':<40}{'Model':<40}{'End of TAC Support':<40}")
        for k, v in hw_eol.items():
            hostname = datasetInfo[k]['hostname']
            eot_date = v['endOfTACSupport']['date']
            eot_model_temp = v['endOfTACSupport']['models']
            eot_model = []
            for km, vm in eot_model_temp.items():
                eot_model.append(km + "(" + str(vm) + ")")
            eot_mod = ", ".join(eot_model)
            print(f"{hostname:<40}{k:<40}{str(eot_mod):<40}{eot_date:<40}")

        print("\nReport #7 - Lifecycle statements - End of Hardware RMA Requests\n")
        print((f"{'Hostname':<40}{'Serial number':<40}{'Model':<40}"
               f"{'End of Hardware RMA Requests':<40}"))
        for k, v in hw_eol.items():
            hostname = datasetInfo[k]['hostname']
            eor_date = v['endOfHardwareRMARequests']['date']
            eor_model_temp = v['endOfHardwareRMARequests']['models']
            eor_model = []
            for km, vm in eor_model_temp.items():
                eor_model.append(km + "(" + str(vm) + ")")
            eor_mod = ", ".join(eor_model)
            print(f"{hostname:<40}{k:<40}{str(eor_mod):<40}{eor_date:<40}")

        print("\nReport #8 - End of Life (SW + HW)\n")
        print(f"{'Device':<40}{'Type':<40}{'Component':<40}{'End of Life':<40}")
        eol_report = []
        for k, v in sw_eol.items():
            hostname = datasetInfo[k]['hostname']
            eol_report.append({hostname: {'sn': k,
                                          'type': 'software',
                                          'component': v['version'],
                                          'date': v['endOfSupport']}})
        for k, v in hw_eol.items():
            hostname = datasetInfo[k]['hostname']
            eol_report.append({hostname: {'sn': k,
                                          'type': 'hardware',
                                          'component': v['endOfLife']['models'],
                                          'date': v['endOfLife']['date']}})
        for device in eol_report:
            hostname = list(device.keys())[0]
            eol_model = []
            eol_model_temp = device[hostname]['component']
            if type(eol_model_temp) != str:
                for km, vm in eol_model_temp.items():
                    eol_model.append(km + "(" + str(vm) + ")")
                eol_mod = ", ".join(eol_model)
            else:
                eol_mod = eol_model_temp
            print((f"{hostname:<40}{device[hostname]['type']:<40}"
                   f"{str(eol_mod):<40}{device[hostname]['date']:<40}"))

    return 0


if __name__ == "__main__":
    args = base.parse_args()
    exit(main(args.apiserver, certs=args.certFile, key=args.keyFile,
              ca=args.caFile, token=args.tokenFile))
