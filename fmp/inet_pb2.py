# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: fmp/inet.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='fmp/inet.proto',
  package='fmp',
  syntax='proto3',
  serialized_options=b'Z0github.com/aristanetworks/cloudvision-go/api/fmp',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0e\x66mp/inet.proto\x12\x03\x66mp\"\x1a\n\tIPAddress\x12\r\n\x05value\x18\x01 \x01(\t\"3\n\x11RepeatedIPAddress\x12\x1e\n\x06values\x18\x01 \x03(\x0b\x32\x0e.fmp.IPAddress\"\x1c\n\x0bIPv4Address\x12\r\n\x05value\x18\x01 \x01(\t\"7\n\x13RepeatedIPv4Address\x12 \n\x06values\x18\x01 \x03(\x0b\x32\x10.fmp.IPv4Address\"\x1c\n\x0bIPv6Address\x12\r\n\x05value\x18\x01 \x01(\t\"7\n\x13RepeatedIPv6Address\x12 \n\x06values\x18\x01 \x03(\x0b\x32\x10.fmp.IPv6Address\"\x19\n\x08IPPrefix\x12\r\n\x05value\x18\x01 \x01(\t\"\x1b\n\nIPv4Prefix\x12\r\n\x05value\x18\x01 \x01(\t\"\x1b\n\nIPv6Prefix\x12\r\n\x05value\x18\x01 \x01(\t\"\x15\n\x04Port\x12\r\n\x05value\x18\x01 \x01(\rB2Z0github.com/aristanetworks/cloudvision-go/api/fmpb\x06proto3'
)




_IPADDRESS = _descriptor.Descriptor(
  name='IPAddress',
  full_name='fmp.IPAddress',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='fmp.IPAddress.value', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=23,
  serialized_end=49,
)


_REPEATEDIPADDRESS = _descriptor.Descriptor(
  name='RepeatedIPAddress',
  full_name='fmp.RepeatedIPAddress',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='values', full_name='fmp.RepeatedIPAddress.values', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=51,
  serialized_end=102,
)


_IPV4ADDRESS = _descriptor.Descriptor(
  name='IPv4Address',
  full_name='fmp.IPv4Address',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='fmp.IPv4Address.value', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=104,
  serialized_end=132,
)


_REPEATEDIPV4ADDRESS = _descriptor.Descriptor(
  name='RepeatedIPv4Address',
  full_name='fmp.RepeatedIPv4Address',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='values', full_name='fmp.RepeatedIPv4Address.values', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=134,
  serialized_end=189,
)


_IPV6ADDRESS = _descriptor.Descriptor(
  name='IPv6Address',
  full_name='fmp.IPv6Address',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='fmp.IPv6Address.value', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=191,
  serialized_end=219,
)


_REPEATEDIPV6ADDRESS = _descriptor.Descriptor(
  name='RepeatedIPv6Address',
  full_name='fmp.RepeatedIPv6Address',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='values', full_name='fmp.RepeatedIPv6Address.values', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=221,
  serialized_end=276,
)


_IPPREFIX = _descriptor.Descriptor(
  name='IPPrefix',
  full_name='fmp.IPPrefix',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='fmp.IPPrefix.value', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=278,
  serialized_end=303,
)


_IPV4PREFIX = _descriptor.Descriptor(
  name='IPv4Prefix',
  full_name='fmp.IPv4Prefix',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='fmp.IPv4Prefix.value', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=305,
  serialized_end=332,
)


_IPV6PREFIX = _descriptor.Descriptor(
  name='IPv6Prefix',
  full_name='fmp.IPv6Prefix',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='fmp.IPv6Prefix.value', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=334,
  serialized_end=361,
)


_PORT = _descriptor.Descriptor(
  name='Port',
  full_name='fmp.Port',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='fmp.Port.value', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=363,
  serialized_end=384,
)

_REPEATEDIPADDRESS.fields_by_name['values'].message_type = _IPADDRESS
_REPEATEDIPV4ADDRESS.fields_by_name['values'].message_type = _IPV4ADDRESS
_REPEATEDIPV6ADDRESS.fields_by_name['values'].message_type = _IPV6ADDRESS
DESCRIPTOR.message_types_by_name['IPAddress'] = _IPADDRESS
DESCRIPTOR.message_types_by_name['RepeatedIPAddress'] = _REPEATEDIPADDRESS
DESCRIPTOR.message_types_by_name['IPv4Address'] = _IPV4ADDRESS
DESCRIPTOR.message_types_by_name['RepeatedIPv4Address'] = _REPEATEDIPV4ADDRESS
DESCRIPTOR.message_types_by_name['IPv6Address'] = _IPV6ADDRESS
DESCRIPTOR.message_types_by_name['RepeatedIPv6Address'] = _REPEATEDIPV6ADDRESS
DESCRIPTOR.message_types_by_name['IPPrefix'] = _IPPREFIX
DESCRIPTOR.message_types_by_name['IPv4Prefix'] = _IPV4PREFIX
DESCRIPTOR.message_types_by_name['IPv6Prefix'] = _IPV6PREFIX
DESCRIPTOR.message_types_by_name['Port'] = _PORT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

IPAddress = _reflection.GeneratedProtocolMessageType('IPAddress', (_message.Message,), {
  'DESCRIPTOR' : _IPADDRESS,
  '__module__' : 'fmp.inet_pb2'
  # @@protoc_insertion_point(class_scope:fmp.IPAddress)
  })
_sym_db.RegisterMessage(IPAddress)

RepeatedIPAddress = _reflection.GeneratedProtocolMessageType('RepeatedIPAddress', (_message.Message,), {
  'DESCRIPTOR' : _REPEATEDIPADDRESS,
  '__module__' : 'fmp.inet_pb2'
  # @@protoc_insertion_point(class_scope:fmp.RepeatedIPAddress)
  })
_sym_db.RegisterMessage(RepeatedIPAddress)

IPv4Address = _reflection.GeneratedProtocolMessageType('IPv4Address', (_message.Message,), {
  'DESCRIPTOR' : _IPV4ADDRESS,
  '__module__' : 'fmp.inet_pb2'
  # @@protoc_insertion_point(class_scope:fmp.IPv4Address)
  })
_sym_db.RegisterMessage(IPv4Address)

RepeatedIPv4Address = _reflection.GeneratedProtocolMessageType('RepeatedIPv4Address', (_message.Message,), {
  'DESCRIPTOR' : _REPEATEDIPV4ADDRESS,
  '__module__' : 'fmp.inet_pb2'
  # @@protoc_insertion_point(class_scope:fmp.RepeatedIPv4Address)
  })
_sym_db.RegisterMessage(RepeatedIPv4Address)

IPv6Address = _reflection.GeneratedProtocolMessageType('IPv6Address', (_message.Message,), {
  'DESCRIPTOR' : _IPV6ADDRESS,
  '__module__' : 'fmp.inet_pb2'
  # @@protoc_insertion_point(class_scope:fmp.IPv6Address)
  })
_sym_db.RegisterMessage(IPv6Address)

RepeatedIPv6Address = _reflection.GeneratedProtocolMessageType('RepeatedIPv6Address', (_message.Message,), {
  'DESCRIPTOR' : _REPEATEDIPV6ADDRESS,
  '__module__' : 'fmp.inet_pb2'
  # @@protoc_insertion_point(class_scope:fmp.RepeatedIPv6Address)
  })
_sym_db.RegisterMessage(RepeatedIPv6Address)

IPPrefix = _reflection.GeneratedProtocolMessageType('IPPrefix', (_message.Message,), {
  'DESCRIPTOR' : _IPPREFIX,
  '__module__' : 'fmp.inet_pb2'
  # @@protoc_insertion_point(class_scope:fmp.IPPrefix)
  })
_sym_db.RegisterMessage(IPPrefix)

IPv4Prefix = _reflection.GeneratedProtocolMessageType('IPv4Prefix', (_message.Message,), {
  'DESCRIPTOR' : _IPV4PREFIX,
  '__module__' : 'fmp.inet_pb2'
  # @@protoc_insertion_point(class_scope:fmp.IPv4Prefix)
  })
_sym_db.RegisterMessage(IPv4Prefix)

IPv6Prefix = _reflection.GeneratedProtocolMessageType('IPv6Prefix', (_message.Message,), {
  'DESCRIPTOR' : _IPV6PREFIX,
  '__module__' : 'fmp.inet_pb2'
  # @@protoc_insertion_point(class_scope:fmp.IPv6Prefix)
  })
_sym_db.RegisterMessage(IPv6Prefix)

Port = _reflection.GeneratedProtocolMessageType('Port', (_message.Message,), {
  'DESCRIPTOR' : _PORT,
  '__module__' : 'fmp.inet_pb2'
  # @@protoc_insertion_point(class_scope:fmp.Port)
  })
_sym_db.RegisterMessage(Port)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
