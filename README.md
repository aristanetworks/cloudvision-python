# Arista CloudVision Python Library

The Arista CloudVision Python library provides access to Arista's CloudVision
APIs for use in Python applications.

## Documentation

API Documentation for this library can be found [here](https://aristanetworks.github.io/cloudvision-python/).

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

- CloudVision Resource APIs: Python 2.7+ or Python 3.7+
- CloudVision Connector: Python 3.7+
- Examples: Python 3.7+

## Resource APIs

Cloudvision APIs are state based, resource-oriented APIs modeled in [Protobuf](https://developers.google.com/protocol-buffers) and accessed over [gRPC](https://grpc.io/) using a standardized set of RPC verbs.

CloudVision is a powerful platform that processes and stores tremendous amounts of network data. It knows the topology of the network, device configuration, interface activity and other network events. These APIs allow access to fleet-wide data access and control, forming a management-plane with consistent usage.

For example, consider the following script that gets all existing and then watches for new CloudVision events of critical severity and notifies an administrator when raised and notes it on the event:

```python
import time
import google.protobuf.wrappers_pb2
import grpc
from arista.event.v1 import models, services

# setup credentials as channelCredentials

with grpc.secure_channel("www.arista.io:443", channelCredentials) as channel:
    event_stub = services.EventServiceStub(channel)
    event_annotation_stub = services.EventAnnotationConfigServiceStub(channel)

    event_watch_request = services.EventStreamRequest(
        partial_eq_filter=[models.Event(severity=models.EVENT_SEVERITY_CRITICAL)],
    )
    for resp in event_stub.Subscribe(event_watch_request):
        print(f"Critical event {resp.title.value} raised at {resp.key.timestamp}")
        # send alert here via email, webhook, or incident reporting tool

        # then make a note on the event indicating an alert has been sent
        now_ms = int(time.time() * 1000)
        notes_to_set = {
            now_ms: models.EventNoteConfig(
                note=google.protobuf.wrappers_pb2.StringValue(
                    value="Administrator alerted",
                ),
            ),
        }
        annotation_config = models.EventAnnotationConfig(
            key=resp.key,
            notes=models.EventNotesConfig(
                notes=notes_to_set,
            ),
        )
        event_note_update = services.EventAnnotationConfigSetRequest(value=annotation_config)
        event_annotation_stub.Set(event_note_update)
```

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
