# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: notification.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12notification.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"\xe6\x01\n\x0cNotification\x12-\n\ttimestamp\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x0c\n\x04path\x18\x02 \x01(\t\x12\x12\n\ndelete_all\x18\x03 \x01(\x08\x12\x0f\n\x07\x64\x65letes\x18\x04 \x03(\x0c\x12%\n\x07updates\x18\x05 \x03(\x0b\x32\x14.Notification.Update\x12\x10\n\x08retracts\x18\x06 \x03(\x0c\x12\x15\n\rpath_elements\x18\x07 \x03(\x0c\x1a$\n\x06Update\x12\x0b\n\x03key\x18\x01 \x01(\x0c\x12\r\n\x05value\x18\x02 \x01(\x0c\"?\n\x07\x44\x61taset\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x18\n\x06parent\x18\x03 \x01(\x0b\x32\x08.Dataset\"\xea\x01\n\x11NotificationBatch\x12\t\n\x01\x64\x18\x01 \x01(\t\x12$\n\rnotifications\x18\x02 \x03(\x0b\x32\r.Notification\x12\x19\n\x07\x64\x61taset\x18\x03 \x01(\x0b\x32\x08.Dataset\x12\x32\n\x08metadata\x18\x04 \x03(\x0b\x32 .NotificationBatch.MetadataEntry\x12$\n\treplicate\x18\x05 \x01(\x0e\x32\x11.ReplicationState\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01*J\n\x10ReplicationState\x12\x12\n\x0eNO_REPLICATION\x10\x00\x12\r\n\tREPLICATE\x10\x01\x12\x13\n\x0f\x43\x41\x43HE_REPLICATE\x10\x02\x42\x05Z\x03genb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'notification_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z\003gen'
  _NOTIFICATIONBATCH_METADATAENTRY._options = None
  _NOTIFICATIONBATCH_METADATAENTRY._serialized_options = b'8\001'
  _globals['_REPLICATIONSTATE']._serialized_start=590
  _globals['_REPLICATIONSTATE']._serialized_end=664
  _globals['_NOTIFICATION']._serialized_start=56
  _globals['_NOTIFICATION']._serialized_end=286
  _globals['_NOTIFICATION_UPDATE']._serialized_start=250
  _globals['_NOTIFICATION_UPDATE']._serialized_end=286
  _globals['_DATASET']._serialized_start=288
  _globals['_DATASET']._serialized_end=351
  _globals['_NOTIFICATIONBATCH']._serialized_start=354
  _globals['_NOTIFICATIONBATCH']._serialized_end=588
  _globals['_NOTIFICATIONBATCH_METADATAENTRY']._serialized_start=541
  _globals['_NOTIFICATIONBATCH_METADATAENTRY']._serialized_end=588
# @@protoc_insertion_point(module_scope)
