#!/usr/bin/python3

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "cloudvision",
#     "polars"
# ]
# [tool.uv]
# exclude-newer = "2024-08-05T00:00:00Z"
# ///
# Example:
# uv run eol_planning.py --apiserver www.cv-prod-uk-1.arista.io:443 --auth=token,token.tok

# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec.custom_types import FrozenDict
from cloudvision.Connector.codec import Wildcard
from utils import pretty_print
import argparse
from parser import base
import polars as pl
from pprint import pprint as pp

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


def cards(client):
    ''' Returns the cards of a switch (Supervisors + Linecards + Fabric Modules)
    '''
    pathElts = [
        "Devices",
        Wildcard(),
        "versioned-data",
        "hardware",
        "inventory",
        "card"
    ]
    dataset = "analytics"
    result = {}
    query = [
        create_query([(pathElts, [])], dataset)
    ]

    for batch in client.get(query):
        for notif in batch["notifications"]:
            if not notif["updates"]:
                continue
            path_elts = notif["path_elements"]
            elem_key = path_elts[1]
            elem_val = result.get(elem_key, {})
            elem_val.update(notif["updates"])
            result[elem_key] = elem_val

    return result


def unfreeze(o):
    ''' Used to unfreeze Frozen dictionaries'''
    if isinstance(o, (dict, FrozenDict)):
        return dict({k: unfreeze(v) for k, v in o.items()})

    if isinstance(o, (str)):
        return o

    try:
        return [unfreeze(i) for i in o]
    except TypeError:
        pass

    return o


def getInventory(client):
    ''' Get device information.
    '''
    path_elts = ["DatasetInfo", "Devices"]
    dataset = "analytics"
    return get(client, dataset, path_elts)


def getLifecyclesHW(client):
    pathElts = [
        "lifecycles",
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


def getLifecyclesSW(client):
    pathElts = [
        "lifecycles",
        "software"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def getSKUs(client):
    pathElts = [
        "BugAlerts",
        "skus"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def main(apiserverAddr, token=None, certs=None, ca=None, key=None):

    with GRPCClient(apiserverAddr, token=token, key=key, ca=ca, certs=certs) as client:
        hw_inventory = unfreeze(cards(client))
        inventory = unfreeze(getInventory(client))
        sw_eol = unfreeze(getLifecyclesSW(client))
        hw_eol = unfreeze(getLifecyclesHW(client))
        device_sw_eol = unfreeze(getDeviceLifecyclesSW(client))
        skus = unfreeze(getSKUs(client))
        df = pl.DataFrame(hw_inventory, strict=False)
        eol = []
        for device in hw_inventory:
            for cardKey, cardValue in hw_inventory[device].items():
                parent_serial_number = device
                if "modelName" not in cardValue:
                    continue
                model_name = cardValue["modelName"]

                if "serialNum" in cardValue:
                    serial_number = cardValue["serialNum"]
                else:
                    serial_number = ""
                if "lifecycle" in cardValue:
                    lifecycle = cardValue["lifecycle"]
                    if "endOfLife" in lifecycle:
                        eol_date = lifecycle["endOfLife"]
                    else:
                        eol_date = ""
                    if "endOfHardwareRMARequests" in lifecycle:
                        eol_rma = lifecycle["endOfHardwareRMARequests"]
                    else:
                        eol_rma = ""
                    if "endOfSale" in lifecycle:
                        eol_sale = lifecycle["endOfSale"]
                    else:
                        eol_sale = ""
                    if "endOfTACSupport" in lifecycle:
                        eol_tac = lifecycle["endOfTACSupport"]
                    else:
                        eol_tac = ""
                else:
                    eol_date = ""
                    eol_rma = ""
                    eol_sale = ""
                    eol_tac = ""
                eol.append(
                    {
                        "hostname": inventory[device]["hostname"],
                        "Serial Number": serial_number,
                        "Parent Serial Number": parent_serial_number,
                        "Model Name": model_name,
                        "Current Software End Of Life": "",
                        "Hardware End Of Life": eol_date,
                        "Hardware End of RMA Requests": eol_rma,
                        "Hardware End of Sale": eol_sale,
                        "Hardware End of TAC Support": eol_tac,
                        "Last Supported Software Train": "",
                        "TerminAttr": "",
                        "Version": ""
                    }
                )
        filteredSkus = {}
        for key, value in skus.items():
            if "DCS-" in key:
                filteredSkus[key] = {}
                relNum = ""
                if value["releaseDeprecated"] != []:
                    deprecatedReleaseNum = value["releaseDeprecated"][0].split('.')
                    relNum = str(deprecatedReleaseNum[0]) + "."
                    relNum += str(int(deprecatedReleaseNum[1]) - 1)
                filteredSkus[key]["releaseDeprecated"] = relNum
        for device in inventory:
            for hwKey, hwValue in hw_eol.items():
                if inventory[device]["modelName"] == hwKey:
                    eol_date = hwValue["endOfLife"]
                    eol_sale = hwValue["endOfSale"]
                    eol_rma = hwValue["endOfHardwareRMARequests"]
                    eol_tac = hwValue["endOfTACSupport"]
            sw_eol_date = ""
            for swKey, swValue in device_sw_eol.items():
                if device == swKey:
                    sw_eol_date = swValue["endOfSupport"]
            for skuKey, skuValue in filteredSkus.items():
                if inventory[device]["modelName"] == skuKey:
                    last_supported_train = skuValue["releaseDeprecated"]
                else:
                    last_supported_train = ""
            for sw, swEol in sw_eol.items():
                if last_supported_train:
                    last_supported_train_eol = swEol["endOfSupport"]
                else:
                    last_supported_train_eol = ""
            eol.append(
                {
                    "hostname": inventory[device]["hostname"],
                    "Serial Number": device,
                    "Parent Serial Number": device,
                    "Model Name": inventory[device]["modelName"],
                    "Current Software End Of Life": sw_eol_date,
                    "Hardware End Of Life": eol_date,
                    "Hardware End of RMA Requests": eol_rma,
                    "Hardware End of Sale": eol_sale,
                    "Hardware End of TAC Support": eol_tac,
                    "Last Supported Software Train": last_supported_train_eol,
                    "TerminAttr": inventory[device]["terminAttrVersion"],
                    "Version": inventory[device]["eosVersion"]
                }
            )

        df = pl.DataFrame(eol)
        print(df)
        df.write_csv("eol.csv")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = base.parse_args()
    exit(main(args.apiserver, certs=args.certFile, key=args.keyFile,
              ca=args.caFile, token=args.tokenFile))
