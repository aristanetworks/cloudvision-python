# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec.custom_types import FrozenDict
from cloudvision.Connector.codec import Wildcard, Path
from utils import pretty_print
import argparse
from parser import base

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


def hw_inventory(client, dId):
    ''' Returns the hardware inventory of a switche without transceivers and power supplies
    '''
    pathElts = [
        "Devices",
        dId,
        "versioned-data",
        "hardware",
        "inventory",
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def xcvr(client, dId):
    ''' Returns the transceiver inventory of a switch
    '''
    pathElts = [
        "Devices",
        dId,
        "versioned-data",
        "hardware",
        "inventory",
        "xcvr"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def psu(client, dId):
    ''' Returns the power supply inventory of a switch
    '''
    pathElts = [
        "Devices",
        dId,
        "versioned-data",
        "hardware",
        "inventory",
        "powerSupply"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def fans(client, dId):
    ''' Returns the FANs inventory of a switch
    '''
    pathElts = [
        "Devices",
        dId,
        "versioned-data",
        "hardware",
        "inventory",
        "fanTray"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def cards(client, dId):
    ''' Returns the cards of a switch (Supervisors + Linecards + Fabric Modules)
    '''
    pathElts = [
        "Devices",
        dId,
        "versioned-data",
        "hardware",
        "inventory",
        "card"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def getSwitchesInfo(client):
    ''' Returns all devices streaming to CVP and their states
    '''
    pathElts = [
        "DatasetInfo",
        "Devices"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


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


def main(apiserverAddr, token=None, certs=None, ca=None, key=None):

    with GRPCClient(apiserverAddr, token=token, key=key,
                    ca=ca, certs=certs) as client:
        dataset_info = getSwitchesInfo(client)
        dev_hw_db = {}
        for device in dataset_info:
            dev_hw_db.update({device: {'inventory': hw_inventory(client, device)}})
            # replace the xcvr pointer data with the actual transceiver data
            if 'xcvr' in dev_hw_db[device]['inventory']:
                dev_hw_db[device]['inventory']['xcvr'] = unfreeze(xcvr(client, device))
            # replace the power supply pointer data with the actual power supply data
            if 'powerSupply' in dev_hw_db[device]['inventory']:
                dev_hw_db[device]['inventory']['powerSupply'] = unfreeze(psu(client, device))
            # replace the card pointer data with the actual cards data
            if 'card' in dev_hw_db[device]['inventory']:
                dev_hw_db[device]['inventory']['card'] = unfreeze(cards(client, device))
            # replace the fanTray pointer data with the actual fans data
            if 'fanTray' in dev_hw_db[device]['inventory']:
                dev_hw_db[device]['inventory']['fanTray'] = unfreeze(fans(client, device))
        pretty_print(dev_hw_db)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = base.parse_args()
    exit(main(args.apiserver, certs=args.certFile, key=args.keyFile,
              ca=args.caFile, token=args.tokenFile))
