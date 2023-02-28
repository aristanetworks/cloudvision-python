# Copyright (c) 2021 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec import Wildcard, Path
from cloudvision.Connector.codec.custom_types import FrozenDict
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from utils import pretty_print
from parser import base
import copy
import requests
import csv
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

debug = False
emptyEndpoint = {'ipAddrSet': set(),
                 'hostname': '',
                 'device': '',
                 'interface': '',
                 'vlanId': None,
                 'timestamp': ''}
endpointDict = {}


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


def get_mac_table(client, dId):
    ''' Get the MAC Table for a device
    '''
    pathElts = [
        "Smash",
        "bridging",
        "status",
        "smashFdbStatus"
    ]
    output = get(client, dId, pathElts)
    for key, value in output.items():
        if value['key'] and value['key']['addr']:
            macAddr = value['key']['addr']
            endpointDict[macAddr] = copy.deepcopy(emptyEndpoint)

    return endpointDict


def get_arp_table(client, dId):
    ''' Get the ARP Table for a device
    '''
    pathElts = [
        "Smash",
        "arp",
        "status",
        Wildcard()
    ]
    output = get(client, dId, pathElts)
    for key, value in output.items():
        if 'key' in value and 'addr' in value['key'] and 'ethAddr' in value:
            macAddr = value['ethAddr']
            ipAddr = value['key']['addr']
            if macAddr not in endpointDict:
                endpointDict[macAddr] = copy.deepcopy(emptyEndpoint)
            endpointDict[macAddr]['ipAddrSet'].add(ipAddr)
    return endpointDict


def get_eco_data(client):
    ''' Get the EOS Campus Observer device information
    '''
    pathElts = [
        "ECO",
        "deviceInfo",
    ]
    output = get(client, "analytics", pathElts)
    for key, value in output.items():
        if 'value' in value and 'hostname' in value['value']:
            macAddr = key
            hostname = value['value']['hostname']
            if macAddr not in endpointDict:
                endpointDict[macAddr] = copy.deepcopy(emptyEndpoint)
            endpointDict[macAddr]['hostname'] = hostname
    return endpointDict


def getSwitchesInfo(client):
    ''' Get the inventory (actively streaming devices)
    '''
    pathElts = [
        "DatasetInfo",
        "Devices"
    ]
    dataset = "analytics"
    return get(client, dataset, pathElts)


def get_endpointlocation(macAddr, server, inventory, tokenFile):
    ''' Get the endpoint location for a MAC address
    '''
    endpoint_url = "/api/resources/endpointlocation/v1/EndpointLocation"
    queryParam = "?key.searchTerm={}".format(macAddr)
    head = {'Authorization': 'Bearer {}'.format(tokenFile)}
    url = "https://" + server + endpoint_url + queryParam
    r = requests.get(url, headers=head, verify=False)
    response = [r.json()]
    if len(response) == 1:
        deviceMap = response[0]['value']['deviceMap']['values']
        if len(deviceMap) == 1:
            for deviceKey, deviceVal in deviceMap.items():
                if 'locationList' in deviceVal:
                    locationList = deviceVal['locationList']['values']
                    if len(locationList) > 0:
                        topLocation = locationList[0]
                        device = topLocation['deviceId']
                        endpointDict[macAddr]['device'] = inventory[device]['hostname']
                        endpointDict[macAddr]['interface'] = topLocation['interface']
                        endpointDict[macAddr]['vlanId'] = topLocation['vlanId']
                        endpointDict[macAddr]['timestamp'] = topLocation['learnedTime']


def main(apiserverAddr, output_file, token=None, certs=None, key=None, ca=None):

    with GRPCClient(apiserverAddr, token=token, key=key,
                    ca=ca, certs=certs) as client:
        switches_info = getSwitchesInfo(client)
        switches = list(switches_info.keys())

        for switch in switches:
            get_mac_table(client, switch)
        for switch in switches:
            get_arp_table(client, switch)
        for key, value in switches_info.items():
            if 'mac' in value and value['mac'] != '' and 'hostname' in value:
                macAddr = value['mac']
                hostname = value['hostname']
                if macAddr not in endpointDict:
                    endpointDict[macAddr] = copy.deepcopy(emptyEndpoint)
                endpointDict[macAddr]['hostname'] = hostname
        get_eco_data(client)

    # Get location for each endpoint
    futures_list = []
    with ThreadPoolExecutor(max_workers=40) as executor:
        for macAddr, _ in endpointDict.items():
            futures = executor.submit(get_endpointlocation, macAddr, server, switches_info,
                                      tokenFile)
            futures_list.append(futures)

    # Build the CSV
    csv_columns = ['MAC Address', 'IP Address List', 'Hostname', 'Device', 'Interface', 'VlanID',
                   'Timestamp']
    csv_file = args.output_file
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t')
            writer.writerow(csv_columns)
            for macAddr, endpointVals in endpointDict.items():
                writer.writerow([macAddr,
                                ', '.join(endpointVals['ipAddrSet']),
                                 endpointVals['hostname'],
                                 endpointVals['device'],
                                 endpointVals['interface'],
                                 str(endpointVals['vlanId']),
                                 endpointVals['timestamp']])
    except IOError:
        print('I/O error')
        print(endpointDict)

    return 0


if __name__ == "__main__":
    base.add_argument("--output-file", required=True, type=str,
                      help="output file for endpoint list")
    args = base.parse_args()
    server = args.apiserver.split(":")[0]
    with open(args.tokenFile) as f:
        tokenFile = f.read().strip("\n")
    exit(main(args.apiserver, args.output_file, certs=args.certFile, key=args.keyFile,
              ca=args.caFile, token=args.tokenFile))
