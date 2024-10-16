# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: arista/configlet.v1/configlet.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from fmp import extensions_pb2 as fmp_dot_extensions__pb2
from fmp import wrappers_pb2 as fmp_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#arista/configlet.v1/configlet.proto\x12\x13\x61rista.configlet.v1\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x14\x66mp/extensions.proto\x1a\x12\x66mp/wrappers.proto\"|\n\x0c\x43onfigletKey\x12\x32\n\x0cworkspace_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x32\n\x0c\x63onfiglet_id\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue:\x04\x80\x8e\x19\x01\":\n\x06\x46ilter\x12\x30\n\x0cinclude_body\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"\xbe\x04\n\tConfiglet\x12.\n\x03key\x18\x01 \x01(\x0b\x32!.arista.configlet.v1.ConfigletKey\x12\x32\n\x0c\x64isplay_name\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x31\n\x0b\x64\x65scription\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x33\n\rmigrated_from\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12*\n\x04\x62ody\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12.\n\ncreated_at\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x30\n\ncreated_by\x18\x07 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x10last_modified_at\x18\x08 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x36\n\x10last_modified_by\x18\t \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12,\n\x06\x64igest\x18\n \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12)\n\x04size\x18\x0b \x01(\x0b\x32\x1b.google.protobuf.Int64Value:\x10\xfa\x8d\x19\x02ro\x8a\x8e\x19\x06\x46ilter\"\xc7\x02\n\x0f\x43onfigletConfig\x12.\n\x03key\x18\x01 \x01(\x0b\x32!.arista.configlet.v1.ConfigletKey\x12*\n\x06remove\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x32\n\x0c\x64isplay_name\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x31\n\x0b\x64\x65scription\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x33\n\rmigrated_from\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12*\n\x04\x62ody\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.StringValue:\x10\xfa\x8d\x19\x02rw\x8a\x8e\x19\x06\x46ilter\"\x91\x01\n\x16\x43onfigletAssignmentKey\x12\x32\n\x0cworkspace_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12=\n\x17\x63onfiglet_assignment_id\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue:\x04\x80\x8e\x19\x01\"\xb4\x03\n\x19\x43onfigletAssignmentConfig\x12\x38\n\x03key\x18\x01 \x01(\x0b\x32+.arista.configlet.v1.ConfigletAssignmentKey\x12\x32\n\x0c\x64isplay_name\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x31\n\x0b\x64\x65scription\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12*\n\rconfiglet_ids\x18\x05 \x01(\x0b\x32\x13.fmp.RepeatedString\x12+\n\x05query\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12*\n\x06remove\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x36\n\x0cmatch_policy\x18\x08 \x01(\x0e\x32 .arista.configlet.v1.MatchPolicy\x12\x31\n\x14\x63hild_assignment_ids\x18\t \x01(\x0b\x32\x13.fmp.RepeatedString:\x06\xfa\x8d\x19\x02rw\"\xd2\x04\n\x13\x43onfigletAssignment\x12\x38\n\x03key\x18\x01 \x01(\x0b\x32+.arista.configlet.v1.ConfigletAssignmentKey\x12\x32\n\x0c\x64isplay_name\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x31\n\x0b\x64\x65scription\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12*\n\rconfiglet_ids\x18\x05 \x01(\x0b\x32\x13.fmp.RepeatedString\x12+\n\x05query\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x36\n\x0cmatch_policy\x18\x07 \x01(\x0e\x32 .arista.configlet.v1.MatchPolicy\x12\x31\n\x14\x63hild_assignment_ids\x18\x08 \x01(\x0b\x32\x13.fmp.RepeatedString\x12.\n\ncreated_at\x18\t \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x30\n\ncreated_by\x18\n \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x10last_modified_at\x18\x0b \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x36\n\x10last_modified_by\x18\x0c \x01(\x0b\x32\x1c.google.protobuf.StringValue:\x06\xfa\x8d\x19\x02ro*e\n\x0bMatchPolicy\x12\x1c\n\x18MATCH_POLICY_UNSPECIFIED\x10\x00\x12\x1c\n\x18MATCH_POLICY_MATCH_FIRST\x10\x01\x12\x1a\n\x16MATCH_POLICY_MATCH_ALL\x10\x02\x42LZJgithub.com/aristanetworks/cloudvision-go/api/arista/configlet.v1;configletb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'arista.configlet.v1.configlet_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'ZJgithub.com/aristanetworks/cloudvision-go/api/arista/configlet.v1;configlet'
  _globals['_CONFIGLETKEY']._options = None
  _globals['_CONFIGLETKEY']._serialized_options = b'\200\216\031\001'
  _globals['_CONFIGLET']._options = None
  _globals['_CONFIGLET']._serialized_options = b'\372\215\031\002ro\212\216\031\006Filter'
  _globals['_CONFIGLETCONFIG']._options = None
  _globals['_CONFIGLETCONFIG']._serialized_options = b'\372\215\031\002rw\212\216\031\006Filter'
  _globals['_CONFIGLETASSIGNMENTKEY']._options = None
  _globals['_CONFIGLETASSIGNMENTKEY']._serialized_options = b'\200\216\031\001'
  _globals['_CONFIGLETASSIGNMENTCONFIG']._options = None
  _globals['_CONFIGLETASSIGNMENTCONFIG']._serialized_options = b'\372\215\031\002rw'
  _globals['_CONFIGLETASSIGNMENT']._options = None
  _globals['_CONFIGLETASSIGNMENT']._serialized_options = b'\372\215\031\002ro'
  _globals['_MATCHPOLICY']._serialized_start=2444
  _globals['_MATCHPOLICY']._serialized_end=2545
  _globals['_CONFIGLETKEY']._serialized_start=167
  _globals['_CONFIGLETKEY']._serialized_end=291
  _globals['_FILTER']._serialized_start=293
  _globals['_FILTER']._serialized_end=351
  _globals['_CONFIGLET']._serialized_start=354
  _globals['_CONFIGLET']._serialized_end=928
  _globals['_CONFIGLETCONFIG']._serialized_start=931
  _globals['_CONFIGLETCONFIG']._serialized_end=1258
  _globals['_CONFIGLETASSIGNMENTKEY']._serialized_start=1261
  _globals['_CONFIGLETASSIGNMENTKEY']._serialized_end=1406
  _globals['_CONFIGLETASSIGNMENTCONFIG']._serialized_start=1409
  _globals['_CONFIGLETASSIGNMENTCONFIG']._serialized_end=1845
  _globals['_CONFIGLETASSIGNMENT']._serialized_start=1848
  _globals['_CONFIGLETASSIGNMENT']._serialized_end=2442
# @@protoc_insertion_point(module_scope)
