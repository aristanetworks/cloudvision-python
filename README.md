# Arista CloudVision Python Library

The Arista CloudVision Python library provides access to Arista's CloudVision
APIs for use in Python applications.

## Documentation

Documentation for CloudVision's Resource APIs can be found [here](https://aristanetworks.github.io/cloudvision-apis).

Documentation for generic access to CloudVision can be found at [CloudVision Connector](#cloudvision-connector).

## Installation

Install via pip:

```sh
pip install --upgrade cloudvision
```

Or from source:

```sh
python setup.py install
```

### Requirements

- CloudVision Resource APIs: Python 2.7+ or Python 3.5+
- CloudVision Connector: Python 3.5+
- Examples: Python 3.5+

## CloudVision Connector

CloudVision Connector is a Python implementation of a GRPC client for CloudVision. It takes care
of getting and publishing data and datasets, and also provides utilities for data
representation.

### Getting started

This is a small example advertising a few of the GRPC client capabilities.
This example prints info from all devices streaming into CloudVision.

```python
targetDataset = "analytics"
path = ["DatasetInfo", "Devices"]
# No filtering done on keys, accept all
keys = []
ProtoBufQuery = CreateQuery([(path, keys)], targetDataset)
with GRPCClient("my-cv-host:9900") as client:
     for notifBatch in client.Get([query]):
         for notif in notifBatch["notifications"]:
             # Get timestamp for all update here with notif.Timestamp
             PrettyPrint(notif["updates"])
```
