# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: arista/configlet.v1/services.gen.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from arista.configlet.v1 import configlet_pb2 as arista_dot_configlet_dot_v1_dot_configlet__pb2
from arista.time import time_pb2 as arista_dot_time_dot_time__pb2
from arista.subscriptions import subscriptions_pb2 as arista_dot_subscriptions_dot_subscriptions__pb2
from fmp import deletes_pb2 as fmp_dot_deletes__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n&arista/configlet.v1/services.gen.proto\x12\x13\x61rista.configlet.v1\x1a#arista/configlet.v1/configlet.proto\x1a\x16\x61rista/time/time.proto\x1a(arista/subscriptions/subscriptions.proto\x1a\x11\x66mp/deletes.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\"\x94\x01\n\x0cMetaResponse\x12(\n\x04time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x02 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\x12+\n\x05\x63ount\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\"l\n\x10\x43onfigletRequest\x12.\n\x03key\x18\x01 \x01(\x0b\x32!.arista.configlet.v1.ConfigletKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"l\n\x11\x43onfigletResponse\x12-\n\x05value\x18\x01 \x01(\x0b\x32\x1e.arista.configlet.v1.Configlet\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"q\n\x14\x43onfigletSomeRequest\x12/\n\x04keys\x18\x01 \x03(\x0b\x32!.arista.configlet.v1.ConfigletKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x9d\x01\n\x15\x43onfigletSomeResponse\x12-\n\x05value\x18\x01 \x01(\x0b\x32\x1e.arista.configlet.v1.Configlet\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12(\n\x04time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"z\n\x16\x43onfigletStreamRequest\x12\x39\n\x11partial_eq_filter\x18\x01 \x03(\x0b\x32\x1e.arista.configlet.v1.Configlet\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\"\xa1\x01\n\x17\x43onfigletStreamResponse\x12-\n\x05value\x18\x01 \x01(\x0b\x32\x1e.arista.configlet.v1.Configlet\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x03 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\"\x80\x01\n\x1a\x43onfigletAssignmentRequest\x12\x38\n\x03key\x18\x01 \x01(\x0b\x32+.arista.configlet.v1.ConfigletAssignmentKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x80\x01\n\x1b\x43onfigletAssignmentResponse\x12\x37\n\x05value\x18\x01 \x01(\x0b\x32(.arista.configlet.v1.ConfigletAssignment\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x85\x01\n\x1e\x43onfigletAssignmentSomeRequest\x12\x39\n\x04keys\x18\x01 \x03(\x0b\x32+.arista.configlet.v1.ConfigletAssignmentKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\xb1\x01\n\x1f\x43onfigletAssignmentSomeResponse\x12\x37\n\x05value\x18\x01 \x01(\x0b\x32(.arista.configlet.v1.ConfigletAssignment\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12(\n\x04time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x8e\x01\n ConfigletAssignmentStreamRequest\x12\x43\n\x11partial_eq_filter\x18\x01 \x03(\x0b\x32(.arista.configlet.v1.ConfigletAssignment\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\"\xb5\x01\n!ConfigletAssignmentStreamResponse\x12\x37\n\x05value\x18\x01 \x01(\x0b\x32(.arista.configlet.v1.ConfigletAssignment\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x03 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\"\x86\x01\n ConfigletAssignmentConfigRequest\x12\x38\n\x03key\x18\x01 \x01(\x0b\x32+.arista.configlet.v1.ConfigletAssignmentKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x8c\x01\n!ConfigletAssignmentConfigResponse\x12=\n\x05value\x18\x01 \x01(\x0b\x32..arista.configlet.v1.ConfigletAssignmentConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x8b\x01\n$ConfigletAssignmentConfigSomeRequest\x12\x39\n\x04keys\x18\x01 \x03(\x0b\x32+.arista.configlet.v1.ConfigletAssignmentKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\xbd\x01\n%ConfigletAssignmentConfigSomeResponse\x12=\n\x05value\x18\x01 \x01(\x0b\x32..arista.configlet.v1.ConfigletAssignmentConfig\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12(\n\x04time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x9a\x01\n&ConfigletAssignmentConfigStreamRequest\x12I\n\x11partial_eq_filter\x18\x01 \x03(\x0b\x32..arista.configlet.v1.ConfigletAssignmentConfig\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\"\xc1\x01\n\'ConfigletAssignmentConfigStreamResponse\x12=\n\x05value\x18\x01 \x01(\x0b\x32..arista.configlet.v1.ConfigletAssignmentConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x03 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\"d\n#ConfigletAssignmentConfigSetRequest\x12=\n\x05value\x18\x01 \x01(\x0b\x32..arista.configlet.v1.ConfigletAssignmentConfig\"\x8f\x01\n$ConfigletAssignmentConfigSetResponse\x12=\n\x05value\x18\x01 \x01(\x0b\x32..arista.configlet.v1.ConfigletAssignmentConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"i\n\'ConfigletAssignmentConfigSetSomeRequest\x12>\n\x06values\x18\x01 \x03(\x0b\x32..arista.configlet.v1.ConfigletAssignmentConfig\"s\n(ConfigletAssignmentConfigSetSomeResponse\x12\x38\n\x03key\x18\x01 \x01(\x0b\x32+.arista.configlet.v1.ConfigletAssignmentKey\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"b\n&ConfigletAssignmentConfigDeleteRequest\x12\x38\n\x03key\x18\x01 \x01(\x0b\x32+.arista.configlet.v1.ConfigletAssignmentKey\"\x8d\x01\n\'ConfigletAssignmentConfigDeleteResponse\x12\x38\n\x03key\x18\x01 \x01(\x0b\x32+.arista.configlet.v1.ConfigletAssignmentKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"g\n*ConfigletAssignmentConfigDeleteSomeRequest\x12\x39\n\x04keys\x18\x01 \x03(\x0b\x32+.arista.configlet.v1.ConfigletAssignmentKey\"v\n+ConfigletAssignmentConfigDeleteSomeResponse\x12\x38\n\x03key\x18\x01 \x01(\x0b\x32+.arista.configlet.v1.ConfigletAssignmentKey\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"+\n)ConfigletAssignmentConfigDeleteAllRequest\"\xdd\x01\n*ConfigletAssignmentConfigDeleteAllResponse\x12\x1e\n\x04type\x18\x01 \x01(\x0e\x32\x10.fmp.DeleteError\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x38\n\x03key\x18\x03 \x01(\x0b\x32+.arista.configlet.v1.ConfigletAssignmentKey\x12(\n\x04time\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"r\n\x16\x43onfigletConfigRequest\x12.\n\x03key\x18\x01 \x01(\x0b\x32!.arista.configlet.v1.ConfigletKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"x\n\x17\x43onfigletConfigResponse\x12\x33\n\x05value\x18\x01 \x01(\x0b\x32$.arista.configlet.v1.ConfigletConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"w\n\x1a\x43onfigletConfigSomeRequest\x12/\n\x04keys\x18\x01 \x03(\x0b\x32!.arista.configlet.v1.ConfigletKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\xa9\x01\n\x1b\x43onfigletConfigSomeResponse\x12\x33\n\x05value\x18\x01 \x01(\x0b\x32$.arista.configlet.v1.ConfigletConfig\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12(\n\x04time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x86\x01\n\x1c\x43onfigletConfigStreamRequest\x12?\n\x11partial_eq_filter\x18\x01 \x03(\x0b\x32$.arista.configlet.v1.ConfigletConfig\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\"\xad\x01\n\x1d\x43onfigletConfigStreamResponse\x12\x33\n\x05value\x18\x01 \x01(\x0b\x32$.arista.configlet.v1.ConfigletConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x03 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\"P\n\x19\x43onfigletConfigSetRequest\x12\x33\n\x05value\x18\x01 \x01(\x0b\x32$.arista.configlet.v1.ConfigletConfig\"{\n\x1a\x43onfigletConfigSetResponse\x12\x33\n\x05value\x18\x01 \x01(\x0b\x32$.arista.configlet.v1.ConfigletConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"U\n\x1d\x43onfigletConfigSetSomeRequest\x12\x34\n\x06values\x18\x01 \x03(\x0b\x32$.arista.configlet.v1.ConfigletConfig\"_\n\x1e\x43onfigletConfigSetSomeResponse\x12.\n\x03key\x18\x01 \x01(\x0b\x32!.arista.configlet.v1.ConfigletKey\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"N\n\x1c\x43onfigletConfigDeleteRequest\x12.\n\x03key\x18\x01 \x01(\x0b\x32!.arista.configlet.v1.ConfigletKey\"y\n\x1d\x43onfigletConfigDeleteResponse\x12.\n\x03key\x18\x01 \x01(\x0b\x32!.arista.configlet.v1.ConfigletKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"S\n ConfigletConfigDeleteSomeRequest\x12/\n\x04keys\x18\x01 \x03(\x0b\x32!.arista.configlet.v1.ConfigletKey\"b\n!ConfigletConfigDeleteSomeResponse\x12.\n\x03key\x18\x01 \x01(\x0b\x32!.arista.configlet.v1.ConfigletKey\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"!\n\x1f\x43onfigletConfigDeleteAllRequest\"\xc9\x01\n ConfigletConfigDeleteAllResponse\x12\x1e\n\x04type\x18\x01 \x01(\x0e\x32\x10.fmp.DeleteError\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12.\n\x03key\x18\x03 \x01(\x0b\x32!.arista.configlet.v1.ConfigletKey\x12(\n\x04time\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp2\xde\x04\n\x10\x43onfigletService\x12W\n\x06GetOne\x12%.arista.configlet.v1.ConfigletRequest\x1a&.arista.configlet.v1.ConfigletResponse\x12\x62\n\x07GetSome\x12).arista.configlet.v1.ConfigletSomeRequest\x1a*.arista.configlet.v1.ConfigletSomeResponse0\x01\x12\x65\n\x06GetAll\x12+.arista.configlet.v1.ConfigletStreamRequest\x1a,.arista.configlet.v1.ConfigletStreamResponse0\x01\x12h\n\tSubscribe\x12+.arista.configlet.v1.ConfigletStreamRequest\x1a,.arista.configlet.v1.ConfigletStreamResponse0\x01\x12Y\n\x07GetMeta\x12+.arista.configlet.v1.ConfigletStreamRequest\x1a!.arista.configlet.v1.MetaResponse\x12\x61\n\rSubscribeMeta\x12+.arista.configlet.v1.ConfigletStreamRequest\x1a!.arista.configlet.v1.MetaResponse0\x01\x32\xcc\x05\n\x1a\x43onfigletAssignmentService\x12k\n\x06GetOne\x12/.arista.configlet.v1.ConfigletAssignmentRequest\x1a\x30.arista.configlet.v1.ConfigletAssignmentResponse\x12v\n\x07GetSome\x12\x33.arista.configlet.v1.ConfigletAssignmentSomeRequest\x1a\x34.arista.configlet.v1.ConfigletAssignmentSomeResponse0\x01\x12y\n\x06GetAll\x12\x35.arista.configlet.v1.ConfigletAssignmentStreamRequest\x1a\x36.arista.configlet.v1.ConfigletAssignmentStreamResponse0\x01\x12|\n\tSubscribe\x12\x35.arista.configlet.v1.ConfigletAssignmentStreamRequest\x1a\x36.arista.configlet.v1.ConfigletAssignmentStreamResponse0\x01\x12\x63\n\x07GetMeta\x12\x35.arista.configlet.v1.ConfigletAssignmentStreamRequest\x1a!.arista.configlet.v1.MetaResponse\x12k\n\rSubscribeMeta\x12\x35.arista.configlet.v1.ConfigletAssignmentStreamRequest\x1a!.arista.configlet.v1.MetaResponse0\x01\x32\xc3\x0b\n ConfigletAssignmentConfigService\x12w\n\x06GetOne\x12\x35.arista.configlet.v1.ConfigletAssignmentConfigRequest\x1a\x36.arista.configlet.v1.ConfigletAssignmentConfigResponse\x12\x82\x01\n\x07GetSome\x12\x39.arista.configlet.v1.ConfigletAssignmentConfigSomeRequest\x1a:.arista.configlet.v1.ConfigletAssignmentConfigSomeResponse0\x01\x12\x85\x01\n\x06GetAll\x12;.arista.configlet.v1.ConfigletAssignmentConfigStreamRequest\x1a<.arista.configlet.v1.ConfigletAssignmentConfigStreamResponse0\x01\x12\x88\x01\n\tSubscribe\x12;.arista.configlet.v1.ConfigletAssignmentConfigStreamRequest\x1a<.arista.configlet.v1.ConfigletAssignmentConfigStreamResponse0\x01\x12i\n\x07GetMeta\x12;.arista.configlet.v1.ConfigletAssignmentConfigStreamRequest\x1a!.arista.configlet.v1.MetaResponse\x12q\n\rSubscribeMeta\x12;.arista.configlet.v1.ConfigletAssignmentConfigStreamRequest\x1a!.arista.configlet.v1.MetaResponse0\x01\x12z\n\x03Set\x12\x38.arista.configlet.v1.ConfigletAssignmentConfigSetRequest\x1a\x39.arista.configlet.v1.ConfigletAssignmentConfigSetResponse\x12\x88\x01\n\x07SetSome\x12<.arista.configlet.v1.ConfigletAssignmentConfigSetSomeRequest\x1a=.arista.configlet.v1.ConfigletAssignmentConfigSetSomeResponse0\x01\x12\x83\x01\n\x06\x44\x65lete\x12;.arista.configlet.v1.ConfigletAssignmentConfigDeleteRequest\x1a<.arista.configlet.v1.ConfigletAssignmentConfigDeleteResponse\x12\x91\x01\n\nDeleteSome\x12?.arista.configlet.v1.ConfigletAssignmentConfigDeleteSomeRequest\x1a@.arista.configlet.v1.ConfigletAssignmentConfigDeleteSomeResponse0\x01\x12\x8e\x01\n\tDeleteAll\x12>.arista.configlet.v1.ConfigletAssignmentConfigDeleteAllRequest\x1a?.arista.configlet.v1.ConfigletAssignmentConfigDeleteAllResponse0\x01\x32\xea\t\n\x16\x43onfigletConfigService\x12\x63\n\x06GetOne\x12+.arista.configlet.v1.ConfigletConfigRequest\x1a,.arista.configlet.v1.ConfigletConfigResponse\x12n\n\x07GetSome\x12/.arista.configlet.v1.ConfigletConfigSomeRequest\x1a\x30.arista.configlet.v1.ConfigletConfigSomeResponse0\x01\x12q\n\x06GetAll\x12\x31.arista.configlet.v1.ConfigletConfigStreamRequest\x1a\x32.arista.configlet.v1.ConfigletConfigStreamResponse0\x01\x12t\n\tSubscribe\x12\x31.arista.configlet.v1.ConfigletConfigStreamRequest\x1a\x32.arista.configlet.v1.ConfigletConfigStreamResponse0\x01\x12_\n\x07GetMeta\x12\x31.arista.configlet.v1.ConfigletConfigStreamRequest\x1a!.arista.configlet.v1.MetaResponse\x12g\n\rSubscribeMeta\x12\x31.arista.configlet.v1.ConfigletConfigStreamRequest\x1a!.arista.configlet.v1.MetaResponse0\x01\x12\x66\n\x03Set\x12..arista.configlet.v1.ConfigletConfigSetRequest\x1a/.arista.configlet.v1.ConfigletConfigSetResponse\x12t\n\x07SetSome\x12\x32.arista.configlet.v1.ConfigletConfigSetSomeRequest\x1a\x33.arista.configlet.v1.ConfigletConfigSetSomeResponse0\x01\x12o\n\x06\x44\x65lete\x12\x31.arista.configlet.v1.ConfigletConfigDeleteRequest\x1a\x32.arista.configlet.v1.ConfigletConfigDeleteResponse\x12}\n\nDeleteSome\x12\x35.arista.configlet.v1.ConfigletConfigDeleteSomeRequest\x1a\x36.arista.configlet.v1.ConfigletConfigDeleteSomeResponse0\x01\x12z\n\tDeleteAll\x12\x34.arista.configlet.v1.ConfigletConfigDeleteAllRequest\x1a\x35.arista.configlet.v1.ConfigletConfigDeleteAllResponse0\x01\x42LZJgithub.com/aristanetworks/cloudvision-go/api/arista/configlet.v1;configletb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'arista.configlet.v1.services.gen_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'ZJgithub.com/aristanetworks/cloudvision-go/api/arista/configlet.v1;configlet'
  _globals['_METARESPONSE']._serialized_start=251
  _globals['_METARESPONSE']._serialized_end=399
  _globals['_CONFIGLETREQUEST']._serialized_start=401
  _globals['_CONFIGLETREQUEST']._serialized_end=509
  _globals['_CONFIGLETRESPONSE']._serialized_start=511
  _globals['_CONFIGLETRESPONSE']._serialized_end=619
  _globals['_CONFIGLETSOMEREQUEST']._serialized_start=621
  _globals['_CONFIGLETSOMEREQUEST']._serialized_end=734
  _globals['_CONFIGLETSOMERESPONSE']._serialized_start=737
  _globals['_CONFIGLETSOMERESPONSE']._serialized_end=894
  _globals['_CONFIGLETSTREAMREQUEST']._serialized_start=896
  _globals['_CONFIGLETSTREAMREQUEST']._serialized_end=1018
  _globals['_CONFIGLETSTREAMRESPONSE']._serialized_start=1021
  _globals['_CONFIGLETSTREAMRESPONSE']._serialized_end=1182
  _globals['_CONFIGLETASSIGNMENTREQUEST']._serialized_start=1185
  _globals['_CONFIGLETASSIGNMENTREQUEST']._serialized_end=1313
  _globals['_CONFIGLETASSIGNMENTRESPONSE']._serialized_start=1316
  _globals['_CONFIGLETASSIGNMENTRESPONSE']._serialized_end=1444
  _globals['_CONFIGLETASSIGNMENTSOMEREQUEST']._serialized_start=1447
  _globals['_CONFIGLETASSIGNMENTSOMEREQUEST']._serialized_end=1580
  _globals['_CONFIGLETASSIGNMENTSOMERESPONSE']._serialized_start=1583
  _globals['_CONFIGLETASSIGNMENTSOMERESPONSE']._serialized_end=1760
  _globals['_CONFIGLETASSIGNMENTSTREAMREQUEST']._serialized_start=1763
  _globals['_CONFIGLETASSIGNMENTSTREAMREQUEST']._serialized_end=1905
  _globals['_CONFIGLETASSIGNMENTSTREAMRESPONSE']._serialized_start=1908
  _globals['_CONFIGLETASSIGNMENTSTREAMRESPONSE']._serialized_end=2089
  _globals['_CONFIGLETASSIGNMENTCONFIGREQUEST']._serialized_start=2092
  _globals['_CONFIGLETASSIGNMENTCONFIGREQUEST']._serialized_end=2226
  _globals['_CONFIGLETASSIGNMENTCONFIGRESPONSE']._serialized_start=2229
  _globals['_CONFIGLETASSIGNMENTCONFIGRESPONSE']._serialized_end=2369
  _globals['_CONFIGLETASSIGNMENTCONFIGSOMEREQUEST']._serialized_start=2372
  _globals['_CONFIGLETASSIGNMENTCONFIGSOMEREQUEST']._serialized_end=2511
  _globals['_CONFIGLETASSIGNMENTCONFIGSOMERESPONSE']._serialized_start=2514
  _globals['_CONFIGLETASSIGNMENTCONFIGSOMERESPONSE']._serialized_end=2703
  _globals['_CONFIGLETASSIGNMENTCONFIGSTREAMREQUEST']._serialized_start=2706
  _globals['_CONFIGLETASSIGNMENTCONFIGSTREAMREQUEST']._serialized_end=2860
  _globals['_CONFIGLETASSIGNMENTCONFIGSTREAMRESPONSE']._serialized_start=2863
  _globals['_CONFIGLETASSIGNMENTCONFIGSTREAMRESPONSE']._serialized_end=3056
  _globals['_CONFIGLETASSIGNMENTCONFIGSETREQUEST']._serialized_start=3058
  _globals['_CONFIGLETASSIGNMENTCONFIGSETREQUEST']._serialized_end=3158
  _globals['_CONFIGLETASSIGNMENTCONFIGSETRESPONSE']._serialized_start=3161
  _globals['_CONFIGLETASSIGNMENTCONFIGSETRESPONSE']._serialized_end=3304
  _globals['_CONFIGLETASSIGNMENTCONFIGSETSOMEREQUEST']._serialized_start=3306
  _globals['_CONFIGLETASSIGNMENTCONFIGSETSOMEREQUEST']._serialized_end=3411
  _globals['_CONFIGLETASSIGNMENTCONFIGSETSOMERESPONSE']._serialized_start=3413
  _globals['_CONFIGLETASSIGNMENTCONFIGSETSOMERESPONSE']._serialized_end=3528
  _globals['_CONFIGLETASSIGNMENTCONFIGDELETEREQUEST']._serialized_start=3530
  _globals['_CONFIGLETASSIGNMENTCONFIGDELETEREQUEST']._serialized_end=3628
  _globals['_CONFIGLETASSIGNMENTCONFIGDELETERESPONSE']._serialized_start=3631
  _globals['_CONFIGLETASSIGNMENTCONFIGDELETERESPONSE']._serialized_end=3772
  _globals['_CONFIGLETASSIGNMENTCONFIGDELETESOMEREQUEST']._serialized_start=3774
  _globals['_CONFIGLETASSIGNMENTCONFIGDELETESOMEREQUEST']._serialized_end=3877
  _globals['_CONFIGLETASSIGNMENTCONFIGDELETESOMERESPONSE']._serialized_start=3879
  _globals['_CONFIGLETASSIGNMENTCONFIGDELETESOMERESPONSE']._serialized_end=3997
  _globals['_CONFIGLETASSIGNMENTCONFIGDELETEALLREQUEST']._serialized_start=3999
  _globals['_CONFIGLETASSIGNMENTCONFIGDELETEALLREQUEST']._serialized_end=4042
  _globals['_CONFIGLETASSIGNMENTCONFIGDELETEALLRESPONSE']._serialized_start=4045
  _globals['_CONFIGLETASSIGNMENTCONFIGDELETEALLRESPONSE']._serialized_end=4266
  _globals['_CONFIGLETCONFIGREQUEST']._serialized_start=4268
  _globals['_CONFIGLETCONFIGREQUEST']._serialized_end=4382
  _globals['_CONFIGLETCONFIGRESPONSE']._serialized_start=4384
  _globals['_CONFIGLETCONFIGRESPONSE']._serialized_end=4504
  _globals['_CONFIGLETCONFIGSOMEREQUEST']._serialized_start=4506
  _globals['_CONFIGLETCONFIGSOMEREQUEST']._serialized_end=4625
  _globals['_CONFIGLETCONFIGSOMERESPONSE']._serialized_start=4628
  _globals['_CONFIGLETCONFIGSOMERESPONSE']._serialized_end=4797
  _globals['_CONFIGLETCONFIGSTREAMREQUEST']._serialized_start=4800
  _globals['_CONFIGLETCONFIGSTREAMREQUEST']._serialized_end=4934
  _globals['_CONFIGLETCONFIGSTREAMRESPONSE']._serialized_start=4937
  _globals['_CONFIGLETCONFIGSTREAMRESPONSE']._serialized_end=5110
  _globals['_CONFIGLETCONFIGSETREQUEST']._serialized_start=5112
  _globals['_CONFIGLETCONFIGSETREQUEST']._serialized_end=5192
  _globals['_CONFIGLETCONFIGSETRESPONSE']._serialized_start=5194
  _globals['_CONFIGLETCONFIGSETRESPONSE']._serialized_end=5317
  _globals['_CONFIGLETCONFIGSETSOMEREQUEST']._serialized_start=5319
  _globals['_CONFIGLETCONFIGSETSOMEREQUEST']._serialized_end=5404
  _globals['_CONFIGLETCONFIGSETSOMERESPONSE']._serialized_start=5406
  _globals['_CONFIGLETCONFIGSETSOMERESPONSE']._serialized_end=5501
  _globals['_CONFIGLETCONFIGDELETEREQUEST']._serialized_start=5503
  _globals['_CONFIGLETCONFIGDELETEREQUEST']._serialized_end=5581
  _globals['_CONFIGLETCONFIGDELETERESPONSE']._serialized_start=5583
  _globals['_CONFIGLETCONFIGDELETERESPONSE']._serialized_end=5704
  _globals['_CONFIGLETCONFIGDELETESOMEREQUEST']._serialized_start=5706
  _globals['_CONFIGLETCONFIGDELETESOMEREQUEST']._serialized_end=5789
  _globals['_CONFIGLETCONFIGDELETESOMERESPONSE']._serialized_start=5791
  _globals['_CONFIGLETCONFIGDELETESOMERESPONSE']._serialized_end=5889
  _globals['_CONFIGLETCONFIGDELETEALLREQUEST']._serialized_start=5891
  _globals['_CONFIGLETCONFIGDELETEALLREQUEST']._serialized_end=5924
  _globals['_CONFIGLETCONFIGDELETEALLRESPONSE']._serialized_start=5927
  _globals['_CONFIGLETCONFIGDELETEALLRESPONSE']._serialized_end=6128
  _globals['_CONFIGLETSERVICE']._serialized_start=6131
  _globals['_CONFIGLETSERVICE']._serialized_end=6737
  _globals['_CONFIGLETASSIGNMENTSERVICE']._serialized_start=6740
  _globals['_CONFIGLETASSIGNMENTSERVICE']._serialized_end=7456
  _globals['_CONFIGLETASSIGNMENTCONFIGSERVICE']._serialized_start=7459
  _globals['_CONFIGLETASSIGNMENTCONFIGSERVICE']._serialized_end=8934
  _globals['_CONFIGLETCONFIGSERVICE']._serialized_start=8937
  _globals['_CONFIGLETCONFIGSERVICE']._serialized_end=10195
# @@protoc_insertion_point(module_scope)
