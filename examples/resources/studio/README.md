# Studios examples

These examples use multiple resources including studio.v1, workspace.v1, studio_topology.v1.

## Authenticating with CloudVision

### CloudVision On-Prem

Service accounts are the recommended way to generate tokens (same steps can be used as on [CVaaS](#cloudvision-as-a-service)).

For quick tests the [get_token.py](../../get_token.py) script can be used to get the token and the certificate from
the CloudVision server:

`python3 get_token.py --server 192.0.2.79 --username cvpadmin --password arastra --ssl`

The two files that will be saved can then be used to authenticate:
- token.txt
- cvp.crt

### CloudVision as a Service

To access the CloudVision as-a-Service and send API requests, “Service Account Token” is needed.
After obtaining the service account token, it can be used for authentication when sending API requests.

Service accounts can be created from the Settings page where a service token can be generated as seen below:

![serviceaccount1](../../Connector/media/serviceaccount1.png)
![serviceaccount2](../../Connector/media/serviceaccount2.png)
![serviceaccount3](../../Connector/media/serviceaccount3.png)

## studio_onboarding.py

The `studio_onboarding.py` script can be used to manage the `Inventory & Topology` studio to onboard
devices and their interfaces.

```shell
python examples/resources/studio/studio_onboarding.py --help
usage: studio_onboarding.py [-h] --server SERVER --token-file TOKEN_FILE [--cert-file CERT_FILE] [--wsid WSID]
                            [--operation {set,get,set-all}] [--update-id UPDATE_ID] [--build-only BUILD_ONLY]

options:
  -h, --help            show this help message and exit
  --server SERVER       CloudVision server to connect to in <host>:<port> format
  --token-file TOKEN_FILE
                        file with access token
  --cert-file CERT_FILE
                        certificate to use as root CA
  --wsid WSID           existing workspace ID, if not wanting to create a new one
  --operation {set,get,set-all}
                        whether to get or set inputs
  --update-id UPDATE_ID
                        Update ID from UpdateService call to set
  --build-only BUILD_ONLY
                        whether to stop after building the changes (no submission)
```

### Get the updates

```shell
python studio_onboarding.py --server www.arista.io:443 --token-file token.tok --build-only True

Creating workspace "Accepting new devices and interfaces into I&T Studio"
	WorkspaceID created: 5f88c496-71ca-469d-af19-2a17a5f5d583
modified::CONNECTION::{"deviceId":"3AB1C9E6B1A1D4DC6B11990838D1D5E9","hostname":"ag-dc1-spine2","interfaceName":"Management0","newValue":{"neighborDeviceId":"D60EC473E29C51A45C50D84B9D89F756","neighborHostname":"ag-dc1-leaf1b","neighborInterfaceName":"Management0"},"oldValue":{"neighborDeviceId":"1207F35678E44BD8E7C7EC8BB18DDB8C","neighborHostname":"ag-dc1-leaf1a","neighborInterfaceName":"Management0"}}
add::DEVICE::{"deviceId":"C7CEA9FC9030555D54E33DA26E0DC09B","hostname":"dc1-leaf2c","interfaceSize":1}
add::DEVICE::{"deviceId":"ZZZ7777777","hostname":"leaf503","interfaceSize":73}
remove::DEVICE::{"deviceId":"SN-dc1-leaf1","hostname":"dc1-leaf1","interfaceSize":6}
remove::DEVICE::{"deviceId":"ZZZ9999999","hostname":"leaf401","interfaceSize":73}
Building workspace
	Build request 09e4c82c-173e-4c79-a235-ca2fd48ce2be sent
	Waiting for build to complete
	Build succeeded
```

### Accept all updates

```shell
python studio_onboarding.py --server www.arista.io:443 --token-file token.tok \
    --wsid 5f88c496-71ca-469d-af19-2a17a5f5d583 --operation set-all
```

### Accept specific updates

```shell
python studio_onboarding.py --server www.cv-staging.corp.arista.io:443 --token-file token.tok \
    --wsid 5f88c496-71ca-469d-af19-2a17a5f5d583 --operation set \
    --update-id 'add::DEVICE::{"deviceId":"ZZZ7777777","hostname":"leaf503","interfaceSize":73}'
```

## studio_update.py

The `studio_update.py` can be used to manage built-in and custom studios

### Get the input of a studio

```shell
python3 studio_update.py --server www.arista.io --token-file token.tok \
        --operation=get --studio-id=studio-avd-campus-fabric-inputs
Mainline inputs have been written to: studio-avd-campus-fabric-inputs.yaml
```

### Update the inputs of a studio

```shell
 python3 studio_update.py --server www.arista.io --token-file token.tok \
      --operation set \
      --studio-id studio-avd-campus-fabric \
      --yaml-file studio-avd-campus-fabric-inputs.yaml \
      --build-only true \
      --sync true \
      --sync-diffs true


Reading inline script metadata from: studio_update.py
Creating workspace "studio-avd-campus-fabric config push"
	WorkspaceID created: ef3c470c-bade-431a-bc7e-11a4ce656dc8
Studio inputs set from yaml:
	studio-avd-campus-fabric-inputs.yaml
	Devices assigned to studio: *
Synchronizing workspace with mainline
	Synchronization request a5f840c5-e9cf-4118-b4d7-611fd0a46aa2 sent
	Waiting for synchronization to complete
	Synchronization succeeded
Downloading sync diffs...
	Sync diffs saved to ef3c470c-bade-431a-bc7e-11a4ce656dc8_sync_diffs.yaml
Building workspace
	Build request f6b4bdc0-5e0a-4409-8231-34c6cab0e5c2 sent
	Waiting for build to complete
	Build succeeded
```

Alternatively [uv](https://docs.astral.sh/uv/getting-started/installation/) can be used as well:

```shell
uv run studio_update.py  --server 192.0.2.10:443 --token-file token.tok --cert-file cvp.crt \
    --operation set \
    --studio-id studio-avd-campus-fabric \
    --yaml-file=studio-avd-campus-fabric-inputs.yaml \
    --build-only True
```
