# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

# Synchronizes CVP Event Generation Configuration between two clusters
#
# Usage:
# python3 sync_events_cfg.py --src=10.83.12.79:8443 --srcauth=token,token1.txt,cvp1.crt \
#  --dst=10.83.12.173:8443 --dstauth=token,token2.txt,cvp2.crt

import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from cloudvision.Connector.grpc_client import GRPCClient, create_query, create_notification
from cloudvision.Connector.codec.custom_types import FrozenDict
from cloudvision.Connector.codec import Wildcard, Path
from utils import pretty_print
from dst_parser import add_arguments
import json
import argparse

debug = False


def get_client(apiserverAddr, token=None, certs=None, key=None, ca=None):
    ''' Returns the gRPC client used for authentication'''
    return GRPCClient(apiserverAddr, token=token, key=key, ca=ca, certs=certs)


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


def getTurbinesConfigs(client):
    ''' Returns all turbine config pointers'''
    pathElts = [
        "Turbines",
        "config"
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


def getEventTurbineNames(client):
    ''' Returns the name of all turbines that generate events'''
    turbine_cfg = getTurbinesConfigs(client)
    event_names = []
    for i in turbine_cfg.keys():
        if "event" in i:
            event_names.append(i)
    return event_names


def getEventsCfg(client):
    ''' Gets the configuration data of each event turbine'''
    event_names = getEventTurbineNames(client)

    dataset = "analytics"
    event_config = {}

    for event in event_names:

        # Initialize the event dictionary where the default and custom rules
        # along with the path elements for each type will be stored
        event_dict = {}
        event_dict['default'] = {"path_elements": [], "updates": {}}
        pathElts = [
            "Turbines",
            "config",
            event,
            Wildcard()
        ]
        query = [create_query([(pathElts, [])], dataset)]
        for batch in client.get(query):
            for notif in batch["notifications"]:

                # Only build a dictionary for custom rules if the custom key exists
                if "custom" in notif['path_elements']:
                    if "custom" in event_dict.keys():
                        event_dict['custom']["updates"].update(notif['updates'])
                        event_dict['custom']["path_elements"] = notif['path_elements']
                    else:
                        event_dict['custom'] = {"path_elements": [], "updates": {}}
                        event_dict['custom']["updates"].update(notif['updates'])
                        event_dict['custom']["path_elements"] = notif['path_elements']
                if "default" in notif['path_elements']:
                    event_dict['default']["updates"].update(notif['updates'])
                    event_dict['default']["path_elements"] = notif['path_elements']
        event_config[event] = event_dict
    return unfreeze(event_config)


def publish(client, dataset, pathElts, data={}):
    ''' Publish function used to update specific paths in the database'''
    ts = Timestamp()
    ts.GetCurrentTime()

    # Boilerplate values for dtype, sync, and compare
    dtype = "device"
    sync = True
    compare = None

    updates = []
    for dataKey in data.keys():
        dataValue = data.get(dataKey)
        updates.append((dataKey, dataValue))

    notifs = [create_notification(ts, pathElts, updates=updates)]

    client.publish(dtype=dtype, dId=dataset, sync=sync, compare=compare, notifs=notifs)
    return 0


def backupConfig(serverType, data):
    ''' Saves data in a json file'''
    filename = "backup" + str(serverType) + ".json"
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)


if __name__ == "__main__":
    ds = ("Synchronizes CVP Event Generation Configuration between two clusters\n"
          "Usage:\n"
          "\tpython3 sync_events_cfg.py --src=10.83.12.79:8443 --srcauth=token,token1.txt,cvp1.crt "
          "--dst=10.83.12.173:8443 --dstauth=token,token2.txt,cvp2.crt"
          )
    base = argparse.ArgumentParser(description=ds,
                                   formatter_class=argparse.RawTextHelpFormatter)
    add_arguments(base)
    args = base.parse_args()
    # Authenticate to the source and destination CVP servers
    clientSrc = get_client(args.src, certs=args.certFile, key=args.keyFile,
                           token=args.tokenFile, ca=args.caFile)
    clientDst = get_client(args.dst, certs=args.certFileDst, key=args.keyFileDst,
                           token=args.tokenFileDst, ca=args.caFileDst)

    # backup the event configurations from each server
    # this will create two files:
    #    - backupsource-cvp.json
    #    - backupdest-cvp.json
    source_config = getEventsCfg(clientSrc)
    dest_config = getEventsCfg(clientDst)
    backupConfig('source-cvp', source_config)
    backupConfig('dest-cvp', dest_config)

    dataset = "analytics"
    # Iterate through the custom events from the source CVP server
    # and publish the data and the pointer to that data
    for events in source_config:
        if "custom" in source_config[events].keys():
            pathElts = source_config[events]["custom"]["path_elements"]
            custom_data = source_config[events]["custom"]["updates"]
            publish(clientDst, dataset, pathElts, custom_data)
            # path pointers need to be created with a different encoding
            # they are optional to have, but
            ptr_data = {"custom": Path(keys=["Turbines", "config", events, "custom"])}
            publish(clientDst, dataset, pathElts[:-1], ptr_data)
