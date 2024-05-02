# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: arista/tag.v2/tag.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from fmp import extensions_pb2 as fmp_dot_extensions__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17\x61rista/tag.v2/tag.proto\x12\rarista.tag.v2\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x14\x66mp/extensions.proto\"\x87\x02\n\x06TagKey\x12\x32\n\x0cworkspace_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x30\n\x0c\x65lement_type\x18\x02 \x01(\x0e\x32\x1a.arista.tag.v2.ElementType\x12+\n\x05label\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12+\n\x05value\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x37\n\x10\x65lement_sub_type\x18\x05 \x01(\x0e\x32\x1d.arista.tag.v2.ElementSubType:\x04\x80\x8e\x19\x01\"c\n\tTagConfig\x12\"\n\x03key\x18\x01 \x01(\x0b\x32\x15.arista.tag.v2.TagKey\x12*\n\x06remove\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.BoolValue:\x06\xfa\x8d\x19\x02rw\"c\n\x03Tag\x12\"\n\x03key\x18\x01 \x01(\x0b\x32\x15.arista.tag.v2.TagKey\x12\x30\n\x0c\x63reator_type\x18\x02 \x01(\x0e\x32\x1a.arista.tag.v2.CreatorType:\x06\xfa\x8d\x19\x02ro\"\xf6\x02\n\x10TagAssignmentKey\x12\x32\n\x0cworkspace_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x30\n\x0c\x65lement_type\x18\x02 \x01(\x0e\x32\x1a.arista.tag.v2.ElementType\x12+\n\x05label\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12+\n\x05value\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\tdevice_id\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x32\n\x0cinterface_id\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x37\n\x10\x65lement_sub_type\x18\x07 \x01(\x0e\x32\x1d.arista.tag.v2.ElementSubType:\x04\x80\x8e\x19\x01\"w\n\x13TagAssignmentConfig\x12,\n\x03key\x18\x01 \x01(\x0b\x32\x1f.arista.tag.v2.TagAssignmentKey\x12*\n\x06remove\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.BoolValue:\x06\xfa\x8d\x19\x02rw\"{\n\rTagAssignment\x12,\n\x03key\x18\x01 \x01(\x0b\x32\x1f.arista.tag.v2.TagAssignmentKey\x12\x34\n\x10tag_creator_type\x18\x02 \x01(\x0e\x32\x1a.arista.tag.v2.CreatorType:\x06\xfa\x8d\x19\x02ro*`\n\x0b\x45lementType\x12\x1c\n\x18\x45LEMENT_TYPE_UNSPECIFIED\x10\x00\x12\x17\n\x13\x45LEMENT_TYPE_DEVICE\x10\x01\x12\x1a\n\x16\x45LEMENT_TYPE_INTERFACE\x10\x02*\xa8\x01\n\x0e\x45lementSubType\x12 \n\x1c\x45LEMENT_SUB_TYPE_UNSPECIFIED\x10\x00\x12\x1b\n\x17\x45LEMENT_SUB_TYPE_DEVICE\x10\x01\x12\x18\n\x14\x45LEMENT_SUB_TYPE_VDS\x10\x02\x12$\n ELEMENT_SUB_TYPE_WORKLOAD_SERVER\x10\x03\x12\x17\n\x13\x45LEMENT_SUB_TYPE_VM\x10\x04*v\n\x0b\x43reatorType\x12\x1c\n\x18\x43REATOR_TYPE_UNSPECIFIED\x10\x00\x12\x17\n\x13\x43REATOR_TYPE_SYSTEM\x10\x01\x12\x15\n\x11\x43REATOR_TYPE_USER\x10\x02\x12\x19\n\x15\x43REATOR_TYPE_EXTERNAL\x10\x03\x42@Z>github.com/aristanetworks/cloudvision-go/api/arista/tag.v2;tagb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'arista.tag.v2.tag_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z>github.com/aristanetworks/cloudvision-go/api/arista/tag.v2;tag'
  _globals['_TAGKEY']._options = None
  _globals['_TAGKEY']._serialized_options = b'\200\216\031\001'
  _globals['_TAGCONFIG']._options = None
  _globals['_TAGCONFIG']._serialized_options = b'\372\215\031\002rw'
  _globals['_TAG']._options = None
  _globals['_TAG']._serialized_options = b'\372\215\031\002ro'
  _globals['_TAGASSIGNMENTKEY']._options = None
  _globals['_TAGASSIGNMENTKEY']._serialized_options = b'\200\216\031\001'
  _globals['_TAGASSIGNMENTCONFIG']._options = None
  _globals['_TAGASSIGNMENTCONFIG']._serialized_options = b'\372\215\031\002rw'
  _globals['_TAGASSIGNMENT']._options = None
  _globals['_TAGASSIGNMENT']._serialized_options = b'\372\215\031\002ro'
  _globals['_ELEMENTTYPE']._serialized_start=1187
  _globals['_ELEMENTTYPE']._serialized_end=1283
  _globals['_ELEMENTSUBTYPE']._serialized_start=1286
  _globals['_ELEMENTSUBTYPE']._serialized_end=1454
  _globals['_CREATORTYPE']._serialized_start=1456
  _globals['_CREATORTYPE']._serialized_end=1574
  _globals['_TAGKEY']._serialized_start=97
  _globals['_TAGKEY']._serialized_end=360
  _globals['_TAGCONFIG']._serialized_start=362
  _globals['_TAGCONFIG']._serialized_end=461
  _globals['_TAG']._serialized_start=463
  _globals['_TAG']._serialized_end=562
  _globals['_TAGASSIGNMENTKEY']._serialized_start=565
  _globals['_TAGASSIGNMENTKEY']._serialized_end=939
  _globals['_TAGASSIGNMENTCONFIG']._serialized_start=941
  _globals['_TAGASSIGNMENTCONFIG']._serialized_end=1060
  _globals['_TAGASSIGNMENT']._serialized_start=1062
  _globals['_TAGASSIGNMENT']._serialized_end=1185
# @@protoc_insertion_point(module_scope)
