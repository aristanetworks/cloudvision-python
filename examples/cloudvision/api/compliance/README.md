# Compliance API examples

These examples combine the inventory resource API with the Compliance gRPC
service. Inventory supplies the hostname and serial number for each matching
device, and the compliance client retrieves the requested status for those
serial numbers.

For now the scripts create two authenticated connections because the inventory API
uses the asynchronous `grpclib` bindings while the Compliance service uses the
synchronous `grpcio` bindings.

## Authentication and TLS

A CloudVision service-account token is required.
Service accounts can be created from the Settings page where a service token can be generated as seen below:

![serviceaccount1](../../../Connector/media/serviceaccount1.png)
![serviceaccount2](../../../Connector/media/serviceaccount2.png)
![serviceaccount3](../../../Connector/media/serviceaccount3.png)

Save the token in a file and
pass its path using `--token-file`.

| Deployment | TLS option |
| --- | --- |
| CVaaS or another publicly signed endpoint | No certificate option is needed; the system CA bundle is used. |
| On-premises with a private or self-signed CA | Pass the CA certificate or CA chain using `--cert-file`. |

The CA file should be PEM encoded and contain the issuing root plus any
required intermediates. The same CA file is used for both API connections.

## Common options

Both scripts accept these options:

| Option | Description |
| --- | --- |
| `--server` | CloudVision endpoint in `host` or `host:port` format. The default port is 443. |
| `--token-file` | Path to a file containing a service-account token. |
| `--cert-file` | Optional path to a private or self-signed CA certificate bundle. |
| `--hostname` | Only include the device with this hostname. |
| `--streaming-status` | Only include `active` or `inactive` devices. |
| `--concurrency` | Number of simultaneous compliance requests. The default is 10. |

When both inventory filters are supplied, a device must match both of them.
Compliance results are printed as requests complete, so concurrent output may
not follow inventory order. Reduce `--concurrency` if the CloudVision instance
needs a lower request rate.

## Configuration diff summaries

`get_all_config_diff_summaries.py` compares each device's designed and running
configurations and displays the compliance result and the number of added,
deleted, and changed lines.

CVaaS example:

```shell
uv run examples/cloudvision/api/compliance/get_all_config_diff_summaries.py \
  --server www.arista.io \
  --token-file /path/to/token \
  --streaming-status active \
  --concurrency 10
```

On-premises example:

```shell
uv run examples/cloudvision/api/compliance/get_all_config_diff_summaries.py \
  --server 192.0.2.10:443 \
  --token-file /path/to/token \
  --cert-file /path/to/internal-ca-chain.pem \
  --streaming-status active
```

An `ERROR` compliance value means CloudVision returned an error for that
device. The detailed service error is written to standard error.

## Device compliance status

`get_all_device_status.py` displays configuration, software-image, and
extension compliance. Peer-supervisor columns contain `n/a` for devices that
do not report dual-supervisor status.

```shell
uv run examples/cloudvision/api/compliance/get_all_device_status.py \
  --server 192.0.2.79 \
  --token-file /path/to/token \
  --streaming-status active \
  --concurrency 10
```

To query one device, add a hostname filter:

```shell
uv run examples/cloudvision/api/compliance/get_all_device_status.py \
  --server www.arista.io \
  --token-file /path/to/token \
  --hostname leaf1 \
  --streaming-status active
```
