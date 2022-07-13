# Inventory resource examples

## gRPC ports

- 8443 up to 2021.2.2
- 443 from 2021.3.0 or newer

## Authenticating with CloudVision

### CloudVision On-Prem


The [get_token.py](../../get_token.py) script can be used to get the token and the certificate from
the CloudVision server:

`python3 get_token.py --server 10.83.12.79 --username cvpadmin --password arastra --ssl`

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

The token should be copied and saved to a file that can later be referred to.
## lookup_device.py


`lookup_device.py` can fetch information such as the serial number, hostname, software version, model name,
hardware revision, FQDN, domain name, system MAC address, boot time, streaming status and the status of extended
attributes (danz, mlag).

```
python3 lookup_device.py --help
usage: lookup_device.py [-h] --server SERVER --token-file TOKEN_FILE [--cert-file CERT_FILE] [--serial SERIAL]
                        [--hostname HOSTNAME]

Lookup a single device by serial, hostname, or require both.

optional arguments:
  -h, --help            show this help message and exit
  --server SERVER       CloudVision server to connect to in <host>:<port> format
  --token-file TOKEN_FILE
                        file with access token
  --cert-file CERT_FILE
                        certificate to use as root CA
  --serial SERIAL       serial number of device to lookup
  --hostname HOSTNAME   hostname of device to lookup
```

### Example

```
python3 lookup_device.py --server 10.83.12.79:443 --token-file ~/go79/token.txt --cert-file ~/go79/cvp.crt --hostname leaf1
value {
  key {
    device_id {
      value: "ZZZ9999999"
    }
  }
  software_version {
    value: "4.25.1F"
  }
  model_name {
    value: "DCS-7160-48YC6"
  }
  hardware_revision {
    value: "11.01"
  }
  fqdn {
    value: "leaf1.aristanetworks.com"
  }
  hostname {
    value: "leaf1"
  }
  domain_name {
    value: "aristanetworks.com"
  }
  system_mac_address {
    value: "de:ad:be:ef:ca:fe"
  }
  boot_time {
    seconds: 1612184247
    nanos: 650255203
  }
  streaming_status: STREAMING_STATUS_INACTIVE
  extended_attributes {
    feature_enabled {
      key: "Danz"
      value: false
    }
    feature_enabled {
      key: "Mlag"
      value: false
    }
  }
}
time {
  seconds: 1612224995
  nanos: 877583211
}
type: INITIAL
```

## get_versions.py

The `get_versions.py` script can get all devices and their EOS versions
or get the EOS version of a specific device.

```
python3 get_versions.py --help
usage: get_versions.py [-h] --server SERVER --token-file TOKEN_FILE [--cert-file CERT_FILE] [--serial SERIAL]
                       [--hostname HOSTNAME]

Lookup a single device by serial, hostname, or require both.

optional arguments:
  -h, --help            show this help message and exit
  --server SERVER       CloudVision server to connect to in <host>:<port> format
  --token-file TOKEN_FILE
                        file with access token
  --cert-file CERT_FILE
                        certificate to use as root CA
  --serial SERIAL       serial number of device to lookup
  --hostname HOSTNAME   hostname of device to lookup
```

### Example

Get all devices and their EOS versions:

```
python3 get_versions.py --server 10.83.12.79:443 --token-file token.txt --cert-file cvp.crt
Hostname                 EOS Version

leaf1                    4.24.4M
leaf2                    4.24.3M
core1                   4.20.12.1M
core2                    4.20.12.1M
sw-10.83.12.244          4.22.1F
spine1                   4.25.0F
sw-10.83.12.245          4.22.1F
```

Get the EOS version of a specific device:

```
python3 get_versions.py --server 10.83.12.79:443 --token-file token.txt --cert-file cvp.crt \
--serial ZZZ9999999 --hostname leaf1
Hostname                 EOS Version

leaf1                    4.24.4M
```

## example_utility.py

The example_utility.py allows reading all devices, only active devices, only inactive devices,
or looking up a single device by serial number(similarly to `lookup_device.py`).
The `--active` filter takes priority over `--inactive`, and the GetAll takes priority
over the single-device path.

```
python3 example_utility.py --help
usage: example_utility.py [-h] --server SERVER --token-file TOKEN_FILE [--cert-file CERT_FILE] [--device DEVICE]
                          [--active] [--inactive]

Get devices in inventory.

optional arguments:
  -h, --help            show this help message and exit
  --server SERVER       CloudVision server to connect to in <host>:<port> format
  --token-file TOKEN_FILE
                        file with access token
  --cert-file CERT_FILE
                        certificate to use as root CA
  --device DEVICE       get a single device by serial number
  --active              get only actively streaming devices
  --inactive            get only non-actively streaming devices
```

### Example

Get all actively streaming devices and their serial numbers:

```
python3 example_utility.py --server 10.83.12.79:443 --token-file ~/go79/token.txt --cert-file ~/go79/cvp.crt --active
leaf1                    5298089ABC0DA0D24213681DDDB30CE6
leaf2                    6298089ABC0DA0D24213681DDDB30C26
core1                    7298089ABC0DA0D24213681DDDB30C46
core2                    9298089ABC0DA0D24213681DDDB30C36
sw-10.83.12.244          1298089ABC0DA0D24213681DDDB30CE6
sw-10.83.12.245          3359B0469FE6C1E92CBB93C5CA77E83C
spine1                   4881D89918374E56222F62553E89319B
7 matching devices in inventory
```

## CloudVision as a Service example

The only difference between sending requests to CloudVision as a Service compared to CloudVision On-Prem is that only the service token is needed and the API endpoint is at TCP 443 instead of 8443.

For example to get all actively streaming devices and their serial numbers we can run the following:

```
python3 example_utility.py --server www.arista.io:443 --token-file cvaasToken.txt --active
tp-avd-leaf2             0123F2E4462997EB155B7C50EC148767
tp-avd-spine2            2568DB4A33177968A78C4FD5A8232159
tp-avd-leaf4             6323DA7D2B542B5D09630F87351BEA41
tp-avd-spine1            CD0EADBEEA126915EA78E0FB4DC776CA
tp-avd-leaf3             8520AF39790A4EC959550166DC5DEADE
tp-avd-leaf1             BAD032986065E8DC14CBB6472EC314A6
6 matching devices in inventory
```