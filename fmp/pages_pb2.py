# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: fmp/pages.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='fmp/pages.proto',
  package='fmp',
  syntax='proto3',
  serialized_options=b'Z0github.com/aristanetworks/cloudvision-go/api/fmp',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0f\x66mp/pages.proto\x12\x03\x66mp*l\n\rSortDirection\x12\x1e\n\x1aSORT_DIRECTION_UNSPECIFIED\x10\x00\x12\x1c\n\x18SORT_DIRECTION_ASCENDING\x10\x01\x12\x1d\n\x19SORT_DIRECTION_DESCENDING\x10\x02\x42\x32Z0github.com/aristanetworks/cloudvision-go/api/fmpb\x06proto3'
)

_SORTDIRECTION = _descriptor.EnumDescriptor(
  name='SortDirection',
  full_name='fmp.SortDirection',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SORT_DIRECTION_UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SORT_DIRECTION_ASCENDING', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SORT_DIRECTION_DESCENDING', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=24,
  serialized_end=132,
)
_sym_db.RegisterEnumDescriptor(_SORTDIRECTION)

SortDirection = enum_type_wrapper.EnumTypeWrapper(_SORTDIRECTION)
SORT_DIRECTION_UNSPECIFIED = 0
SORT_DIRECTION_ASCENDING = 1
SORT_DIRECTION_DESCENDING = 2


DESCRIPTOR.enum_types_by_name['SortDirection'] = _SORTDIRECTION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
