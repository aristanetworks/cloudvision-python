# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: arista/connectivitymonitor.v1/connectivitymonitor.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from fmp import extensions_pb2 as fmp_dot_extensions__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='arista/connectivitymonitor.v1/connectivitymonitor.proto',
  package='arista.connectivitymonitor.v1',
  syntax='proto3',
  serialized_options=b'Z^github.com/aristanetworks/cloudvision-go/api/arista/connectivitymonitor.v1;connectivitymonitor',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n7arista/connectivitymonitor.v1/connectivitymonitor.proto\x12\x1d\x61rista.connectivitymonitor.v1\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x14\x66mp/extensions.proto\"\x98\x01\n\x08ProbeKey\x12/\n\tdevice_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12*\n\x04host\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12)\n\x03vrf\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue:\x04\x80\x8e\x19\x01\"\xd0\x01\n\rProbeStatsKey\x12/\n\tdevice_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12*\n\x04host\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12)\n\x03vrf\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x31\n\x0bsource_intf\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue:\x04\x80\x8e\x19\x01\"\xd8\x01\n\x05Probe\x12\x34\n\x03key\x18\x01 \x01(\x0b\x32\'.arista.connectivitymonitor.v1.ProbeKey\x12-\n\x07ip_addr\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\thost_name\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x31\n\x0b\x64\x65scription\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue:\x06\xfa\x8d\x19\x02ro\"\xe2\x02\n\nProbeStats\x12\x39\n\x03key\x18\x01 \x01(\x0b\x32,.arista.connectivitymonitor.v1.ProbeStatsKey\x12\x34\n\x0elatency_millis\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\x12\x33\n\rjitter_millis\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\x12?\n\x19http_response_time_millis\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\x12\x38\n\x13packet_loss_percent\x18\x05 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12+\n\x05\x65rror\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.StringValue:\x06\xfa\x8d\x19\x02roB`Z^github.com/aristanetworks/cloudvision-go/api/arista/connectivitymonitor.v1;connectivitymonitorb\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_wrappers__pb2.DESCRIPTOR,fmp_dot_extensions__pb2.DESCRIPTOR,])




_PROBEKEY = _descriptor.Descriptor(
  name='ProbeKey',
  full_name='arista.connectivitymonitor.v1.ProbeKey',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='device_id', full_name='arista.connectivitymonitor.v1.ProbeKey.device_id', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='host', full_name='arista.connectivitymonitor.v1.ProbeKey.host', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='vrf', full_name='arista.connectivitymonitor.v1.ProbeKey.vrf', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'\200\216\031\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=145,
  serialized_end=297,
)


_PROBESTATSKEY = _descriptor.Descriptor(
  name='ProbeStatsKey',
  full_name='arista.connectivitymonitor.v1.ProbeStatsKey',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='device_id', full_name='arista.connectivitymonitor.v1.ProbeStatsKey.device_id', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='host', full_name='arista.connectivitymonitor.v1.ProbeStatsKey.host', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='vrf', full_name='arista.connectivitymonitor.v1.ProbeStatsKey.vrf', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='source_intf', full_name='arista.connectivitymonitor.v1.ProbeStatsKey.source_intf', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'\200\216\031\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=300,
  serialized_end=508,
)


_PROBE = _descriptor.Descriptor(
  name='Probe',
  full_name='arista.connectivitymonitor.v1.Probe',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='arista.connectivitymonitor.v1.Probe.key', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ip_addr', full_name='arista.connectivitymonitor.v1.Probe.ip_addr', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='host_name', full_name='arista.connectivitymonitor.v1.Probe.host_name', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='description', full_name='arista.connectivitymonitor.v1.Probe.description', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'\372\215\031\002ro',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=511,
  serialized_end=727,
)


_PROBESTATS = _descriptor.Descriptor(
  name='ProbeStats',
  full_name='arista.connectivitymonitor.v1.ProbeStats',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='arista.connectivitymonitor.v1.ProbeStats.key', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='latency_millis', full_name='arista.connectivitymonitor.v1.ProbeStats.latency_millis', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='jitter_millis', full_name='arista.connectivitymonitor.v1.ProbeStats.jitter_millis', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='http_response_time_millis', full_name='arista.connectivitymonitor.v1.ProbeStats.http_response_time_millis', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='packet_loss_percent', full_name='arista.connectivitymonitor.v1.ProbeStats.packet_loss_percent', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='error', full_name='arista.connectivitymonitor.v1.ProbeStats.error', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'\372\215\031\002ro',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=730,
  serialized_end=1084,
)

_PROBEKEY.fields_by_name['device_id'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_PROBEKEY.fields_by_name['host'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_PROBEKEY.fields_by_name['vrf'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_PROBESTATSKEY.fields_by_name['device_id'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_PROBESTATSKEY.fields_by_name['host'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_PROBESTATSKEY.fields_by_name['vrf'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_PROBESTATSKEY.fields_by_name['source_intf'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_PROBE.fields_by_name['key'].message_type = _PROBEKEY
_PROBE.fields_by_name['ip_addr'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_PROBE.fields_by_name['host_name'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_PROBE.fields_by_name['description'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_PROBESTATS.fields_by_name['key'].message_type = _PROBESTATSKEY
_PROBESTATS.fields_by_name['latency_millis'].message_type = google_dot_protobuf_dot_wrappers__pb2._DOUBLEVALUE
_PROBESTATS.fields_by_name['jitter_millis'].message_type = google_dot_protobuf_dot_wrappers__pb2._DOUBLEVALUE
_PROBESTATS.fields_by_name['http_response_time_millis'].message_type = google_dot_protobuf_dot_wrappers__pb2._DOUBLEVALUE
_PROBESTATS.fields_by_name['packet_loss_percent'].message_type = google_dot_protobuf_dot_wrappers__pb2._INT64VALUE
_PROBESTATS.fields_by_name['error'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
DESCRIPTOR.message_types_by_name['ProbeKey'] = _PROBEKEY
DESCRIPTOR.message_types_by_name['ProbeStatsKey'] = _PROBESTATSKEY
DESCRIPTOR.message_types_by_name['Probe'] = _PROBE
DESCRIPTOR.message_types_by_name['ProbeStats'] = _PROBESTATS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ProbeKey = _reflection.GeneratedProtocolMessageType('ProbeKey', (_message.Message,), {
  'DESCRIPTOR' : _PROBEKEY,
  '__module__' : 'arista.connectivitymonitor.v1.connectivitymonitor_pb2'
  # @@protoc_insertion_point(class_scope:arista.connectivitymonitor.v1.ProbeKey)
  })
_sym_db.RegisterMessage(ProbeKey)

ProbeStatsKey = _reflection.GeneratedProtocolMessageType('ProbeStatsKey', (_message.Message,), {
  'DESCRIPTOR' : _PROBESTATSKEY,
  '__module__' : 'arista.connectivitymonitor.v1.connectivitymonitor_pb2'
  # @@protoc_insertion_point(class_scope:arista.connectivitymonitor.v1.ProbeStatsKey)
  })
_sym_db.RegisterMessage(ProbeStatsKey)

Probe = _reflection.GeneratedProtocolMessageType('Probe', (_message.Message,), {
  'DESCRIPTOR' : _PROBE,
  '__module__' : 'arista.connectivitymonitor.v1.connectivitymonitor_pb2'
  # @@protoc_insertion_point(class_scope:arista.connectivitymonitor.v1.Probe)
  })
_sym_db.RegisterMessage(Probe)

ProbeStats = _reflection.GeneratedProtocolMessageType('ProbeStats', (_message.Message,), {
  'DESCRIPTOR' : _PROBESTATS,
  '__module__' : 'arista.connectivitymonitor.v1.connectivitymonitor_pb2'
  # @@protoc_insertion_point(class_scope:arista.connectivitymonitor.v1.ProbeStats)
  })
_sym_db.RegisterMessage(ProbeStats)


DESCRIPTOR._options = None
_PROBEKEY._options = None
_PROBESTATSKEY._options = None
_PROBE._options = None
_PROBESTATS._options = None
# @@protoc_insertion_point(module_scope)
