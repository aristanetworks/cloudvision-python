# CloudVision Connector Examples

## Authenticating with CloudVision

### CloudVision On-Prem

The [get_token.py](../get_token.py) script can be used to get the token and the certificate from
the CloudVision server:

`python3 get_token.py --server 10.83.12.79 --username cvpadmin --password arastra --ssl`

The two files that will be saved can then be used to authenticate:
- token.txt
- cvp.crt

### CloudVision as a Service

To access the CloudVision as-a-Service and send API requests, “Service Account Token” is needed.
After obtaining the service account token, it can be used for authentication when sending API requests.

Service accounts can be created from the Settings page where a service token can be generated as seen below:

![serviceaccount1](./media/serviceaccount1.png)
![serviceaccount2](./media/serviceaccount2.png)
![serviceaccount3](./media/serviceaccount3.png)

The token should be copied and saved to a file that can later be referred to.

## get_intf_rate.py
---

This script is an example on how to subscribe to the rate counters of an interface.

```
python3 get_intf_rate.py --apiserver 10.83.12.79:8443 --auth=token,~/go79/token.txt,~/go79/cvp.crt --
device JPE17182435 --interface Ethernet24
{
    "outOctets":99945180.4
}
{
    "outOctets":99660196.3
}
{
    "outOctets":99252974.8
}
{
    "outOctets":99084092.4
}
{
    "outOctets":100230212.3
}
```

In this example the subscription is made to the `outOctets` rate, other possible options are:
- alignmentErrors
- fcsErrors
- frameTooLongs
- frameTooShorts
- inBroadcastPkts
- inDiscards
- inErrors
- inMulticastPkts
- inOctets
- inUcastPkts
- outBroadcastPkts
- outDiscards
- outErrors
- outMulticastPkts

## get_intf_status.py
---

The `get_intf_status.py` is an example on how to get the status of all the interfaces of a device. The below example get the link status, however other states can be read from the same path such as `operStatus`, `autonegCapabilities`, `burnedInAddr` (the mac address of the interface), `mtu` and many others. For more details visit the Telemetry Browser in the CloudVision UI.
It also creates a report about how many interfaces are up and down (including the Management interface).

```
python3 get_intf_status.py --apiserver 10.83.12.79:8443 --auth=token,~/go79/token.txt,~/go79/cvp.crt --deviceId JPE17182435
Interface Name           Status

Ethernet10               linkDown
Ethernet1                linkDown
Ethernet2                linkDown
Ethernet3                linkDown
Ethernet8                linkDown
Ethernet5                linkDown
Ethernet9                linkDown
Ethernet24               linkUp
Ethernet26               linkUp
Management1              linkUp
<ommitted>

Ethernet Status on JPE17182435:
         8 interfaces connected (including Management)
        56 interfaces down
```

## get_switches.py

`get_switches.py` is an example on how to return all the actively streaming devices to CloudVision.

```
python3 get_switches.py --apiserver 10.83.12.79:8443 --auth=token,token.txt,cvp.crt
{
    "ZZZ9999999":{
        "capabilities":[
            "all"
        ],
        "eosVersion":"4.24.4M",
        "hostname":"leaf1",
        "isProvisioned":false,
        "mac":"de:ad:be:ef:ca:fe",
        "modelName":"DCS-7050TX-64",
        "primaryManagementIP":"172.28.160.226",
        "status":"active",
        "terminAttrVersion":"v1.10.0"
    }
}
{
    "ZZZ9999998":{
        "capabilities":[
            "all"
        ],
        "eosVersion":"4.24.3M",
        "hostname":"spine1",
        "isProvisioned":true,
        "mac":"de:ad:b3:3f:ca:f3",
        "modelName":"DCS-7280SR-48C6",
        "primaryManagementIP":"172.28.161.108",
        "status":"active",
        "terminAttrVersion":"v1.10.0"
    }
}
```

## sync_events_cfg.py
---

The purpose of writing this script is to synchronize event generation rule configurations between two different CVP cluster.

This was tested on 2020.2.0 - 2020.3.0. It is recommended to run this script between clusters that are on the same version.

Script files used:
- sync_events_cfg.py
- dst_parser.py
- get_token.py

### Steps

1\. Clone the repository
`git clone https://github.com/aristanetworks/cloudvision-python.git`

2\. Go to example directory
`cd examples`

3\. Create a folder for each server to store the token and ssl cert files

```
mkdir go79
mkdir go173
```

4\. Copy the get_token.py to these folders

```
cp get_token.py go79/
cp get_token.py go173/
```

5\. Generate the token and cert for each server

```
cd go79
python3 get_token.py --server 10.83.12.79 --username cvpadmin --password arastra --ssl

cd ../go173
python3 get_token.py --server 10.83.12.173 --username cvpadmin --password arastra --ssl
```

6\. After that you should have 3 files in each folder like below

```
 cvp.crt
 get_token.py
 token.txt
```

7\. Now you can run the script

```
cd ../Connector

python3 sync_events_cfg.py --src=10.83.12.79:8443 --srcauth=token,../go79/token.txt,../go79/cvp.crt --dst=10.83.12.173:8443 --dstauth=token,../go173/token.txt,../go173/cvp.crt
```

8\. After this you should see the rules from server1 replicated to server2.

### What does the script do?

Gets all the data under ‘/Turbine/configs’ in the ‘analytics’ dataset where the the turbine configurations are stored
creates a list with all the turbine names that generate events
based on that list gets the configuration of each event turbine and saves that data in a dictionary
for each event there will be a ‘default’ key and in case a custom rule was applied it will also have a ‘custom’ key, each key will have an ‘updates’ key and a ‘path_elements’ key, e.g.:

```
     eventName: { “default”: {“updates”: {<RULE data>},
                              “path_elements”:[<aeris path in list format>]
                              },
                  “custom”: {“updates”: {<RULE data>},
                             “path_elements”:[<aeris path in list format>]
                                                 }}
```

the default configs are backed up and saved in a json file from both servers, the filenames are:
- backupsource-cvp.json
- backupdest-cvp.json

the config from the source server is pushed to the destination server

![eventsync1](media/eventsync1.png)
![eventsync2](media/eventsync2.png)
![eventsync3](media/eventsync3.png)

# get_events.py
---

This script is a very simplistic example of the resource API equivalent `get_events.py` and it prints all current active events in CloudVision.

```
python3 get_events.py  --apiserver 10.83.12.79:8443 --auth=token,~/go79/token.txt,~/go79/cvp.crt
{
    "74694dfb259599":{
        "ack":true,
        "acknowledgement":{
            "timestamp":"1604061595270",
            "userId":"cvpadmin"
        },
        "components":[
            {
                "deviceId":"JPE17182435",
                "type":"device"
            }
        ],
        "data":{
            "checkItems":{
                "Flood List":{
                    "desc":"No flood list configured",
                    "name":"Flood List",
                    "result":"Fail"
                },
                "Loopback IP Address":{
                    "desc":"",
                    "name":"Loopback IP Address",
                    "result":"Pass"
                },
                "Routing":{
                    "desc":"",
                    "name":"Routing",
                    "result":"Pass"
                },
                "VLAN-VNI Map":{
                    "desc":"",
                    "name":"VLAN-VNI Map",
                    "result":"Pass"
                }
            },
            "deviceId":"JPE17182435"
        },
        "delTime":0,
        "description":"Local VTEP configuration check failed",
        "eventType":"VXLAN_CONFIG_SANITY",
        "isInteractionUpdate":true,
        "key":"74694dfb259599",
        "keySchema":[
            "deviceId"
        ],
        "lastUpdatedTime":1604061595270,
        "severity":"WARNING",
        "timestamp":1597406296448,
        "title":"Vxlan Config Sanity Check failed"
    }
}
```

Get events within a certain period of time:

`python3 get_events.py  --apiserver 10.83.12.79:8443 --auth=token,token.txt,cvp.crt --start=2021-02-02T10:00:00 --end=2021-02-02T21:46:00 --exact_range=True`

> Note that without setting the `-exact_range` flag to `True` events before the start time that were active at start time will also
> be presented.

## Utilities
---

- `pretty_print` from `utils.py` can be used to pretty print notifications that have frozen dictionaries
- `parser.py` and `dst_parser.py` contain the arugment parsers for connecting to CloudVision
- `delete.py` can delete keys from a specific path ( Not recommended to be used without contacting Arista Support )

## CloudVision as a Service example

The only difference between sending requests to CloudVision as a Service compared to CloudVision On-Prem is that only the service token is needed and the API endpoint is at TCP 443 instead of 8443.

```
python3 get_switches.py --apiserver apiserver.arista.io:443 --auth=token,cvaasToken.txt
{
    "0123F2E4462997EB155B7C50EC148767":{
        "capabilities":[
            "all"
        ],
        "deviceType":"",
        "eosVersion":"4.24.3M",
        "hostname":"tp-avd-leaf2",
        "isProvisioned":true,
        "mac":"50:08:00:b1:5b:0b",
        "modelName":"vEOS",
        "primaryManagementIP":"10.83.13.215",
        "status":"active",
        "terminAttrVersion":"v1.12.2"
    }
}
{
    "2568DB4A33177968A78C4FD5A8232159":{
        "capabilities":[
            "all"
        ],
        "deviceType":"",
        "eosVersion":"4.24.3M",
        "hostname":"tp-avd-spine2",
        "isProvisioned":true,
        "mac":"50:08:00:8c:22:49",
        "modelName":"vEOS",
        "primaryManagementIP":"10.83.13.213",
        "status":"active",
        "terminAttrVersion":"v1.12.2"
    }
}
```