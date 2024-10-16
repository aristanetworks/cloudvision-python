# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: arista/event.v1/services.gen.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from arista.event.v1 import event_pb2 as arista_dot_event_dot_v1_dot_event__pb2
from arista.time import time_pb2 as arista_dot_time_dot_time__pb2
from arista.subscriptions import subscriptions_pb2 as arista_dot_subscriptions_dot_subscriptions__pb2
from fmp import deletes_pb2 as fmp_dot_deletes__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\"arista/event.v1/services.gen.proto\x12\x0f\x61rista.event.v1\x1a\x1b\x61rista/event.v1/event.proto\x1a\x16\x61rista/time/time.proto\x1a(arista/subscriptions/subscriptions.proto\x1a\x11\x66mp/deletes.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\"\x94\x01\n\x0cMetaResponse\x12(\n\x04time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x02 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\x12+\n\x05\x63ount\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\"`\n\x0c\x45ventRequest\x12&\n\x03key\x18\x01 \x01(\x0b\x32\x19.arista.event.v1.EventKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"`\n\rEventResponse\x12%\n\x05value\x18\x01 \x01(\x0b\x32\x16.arista.event.v1.Event\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"e\n\x10\x45ventSomeRequest\x12\'\n\x04keys\x18\x01 \x03(\x0b\x32\x19.arista.event.v1.EventKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x91\x01\n\x11\x45ventSomeResponse\x12%\n\x05value\x18\x01 \x01(\x0b\x32\x16.arista.event.v1.Event\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12(\n\x04time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"n\n\x12\x45ventStreamRequest\x12\x31\n\x11partial_eq_filter\x18\x01 \x03(\x0b\x32\x16.arista.event.v1.Event\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\"\x95\x01\n\x13\x45ventStreamResponse\x12%\n\x05value\x18\x01 \x01(\x0b\x32\x16.arista.event.v1.Event\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x03 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\"p\n\x1c\x45ventAnnotationConfigRequest\x12&\n\x03key\x18\x01 \x01(\x0b\x32\x19.arista.event.v1.EventKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x80\x01\n\x1d\x45ventAnnotationConfigResponse\x12\x35\n\x05value\x18\x01 \x01(\x0b\x32&.arista.event.v1.EventAnnotationConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"u\n EventAnnotationConfigSomeRequest\x12\'\n\x04keys\x18\x01 \x03(\x0b\x32\x19.arista.event.v1.EventKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\xb1\x01\n!EventAnnotationConfigSomeResponse\x12\x35\n\x05value\x18\x01 \x01(\x0b\x32&.arista.event.v1.EventAnnotationConfig\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12(\n\x04time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x8e\x01\n\"EventAnnotationConfigStreamRequest\x12\x41\n\x11partial_eq_filter\x18\x01 \x03(\x0b\x32&.arista.event.v1.EventAnnotationConfig\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\"\xb5\x01\n#EventAnnotationConfigStreamResponse\x12\x35\n\x05value\x18\x01 \x01(\x0b\x32&.arista.event.v1.EventAnnotationConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x03 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\"X\n\x1f\x45ventAnnotationConfigSetRequest\x12\x35\n\x05value\x18\x01 \x01(\x0b\x32&.arista.event.v1.EventAnnotationConfig\"\x83\x01\n EventAnnotationConfigSetResponse\x12\x35\n\x05value\x18\x01 \x01(\x0b\x32&.arista.event.v1.EventAnnotationConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"]\n#EventAnnotationConfigSetSomeRequest\x12\x36\n\x06values\x18\x01 \x03(\x0b\x32&.arista.event.v1.EventAnnotationConfig\"]\n$EventAnnotationConfigSetSomeResponse\x12&\n\x03key\x18\x01 \x01(\x0b\x32\x19.arista.event.v1.EventKey\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"L\n\"EventAnnotationConfigDeleteRequest\x12&\n\x03key\x18\x01 \x01(\x0b\x32\x19.arista.event.v1.EventKey\"w\n#EventAnnotationConfigDeleteResponse\x12&\n\x03key\x18\x01 \x01(\x0b\x32\x19.arista.event.v1.EventKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"Q\n&EventAnnotationConfigDeleteSomeRequest\x12\'\n\x04keys\x18\x01 \x03(\x0b\x32\x19.arista.event.v1.EventKey\"`\n\'EventAnnotationConfigDeleteSomeResponse\x12&\n\x03key\x18\x01 \x01(\x0b\x32\x19.arista.event.v1.EventKey\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"j\n%EventAnnotationConfigDeleteAllRequest\x12\x41\n\x11partial_eq_filter\x18\x01 \x03(\x0b\x32&.arista.event.v1.EventAnnotationConfig\"\xc7\x01\n&EventAnnotationConfigDeleteAllResponse\x12\x1e\n\x04type\x18\x01 \x01(\x0e\x32\x10.fmp.DeleteError\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12&\n\x03key\x18\x03 \x01(\x0b\x32\x19.arista.event.v1.EventKey\x12(\n\x04time\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"~\n\x1eUserEventCreationConfigRequest\x12\x32\n\x03key\x18\x01 \x01(\x0b\x32%.arista.event.v1.UserEventCreationKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x84\x01\n\x1fUserEventCreationConfigResponse\x12\x37\n\x05value\x18\x01 \x01(\x0b\x32(.arista.event.v1.UserEventCreationConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x83\x01\n\"UserEventCreationConfigSomeRequest\x12\x33\n\x04keys\x18\x01 \x03(\x0b\x32%.arista.event.v1.UserEventCreationKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\xb5\x01\n#UserEventCreationConfigSomeResponse\x12\x37\n\x05value\x18\x01 \x01(\x0b\x32(.arista.event.v1.UserEventCreationConfig\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12(\n\x04time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x92\x01\n$UserEventCreationConfigStreamRequest\x12\x43\n\x11partial_eq_filter\x18\x01 \x03(\x0b\x32(.arista.event.v1.UserEventCreationConfig\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\"\xb9\x01\n%UserEventCreationConfigStreamResponse\x12\x37\n\x05value\x18\x01 \x01(\x0b\x32(.arista.event.v1.UserEventCreationConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x03 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\"\\\n!UserEventCreationConfigSetRequest\x12\x37\n\x05value\x18\x01 \x01(\x0b\x32(.arista.event.v1.UserEventCreationConfig\"\x87\x01\n\"UserEventCreationConfigSetResponse\x12\x37\n\x05value\x18\x01 \x01(\x0b\x32(.arista.event.v1.UserEventCreationConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"a\n%UserEventCreationConfigSetSomeRequest\x12\x38\n\x06values\x18\x01 \x03(\x0b\x32(.arista.event.v1.UserEventCreationConfig\"k\n&UserEventCreationConfigSetSomeResponse\x12\x32\n\x03key\x18\x01 \x01(\x0b\x32%.arista.event.v1.UserEventCreationKey\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"Z\n$UserEventCreationConfigDeleteRequest\x12\x32\n\x03key\x18\x01 \x01(\x0b\x32%.arista.event.v1.UserEventCreationKey\"\x85\x01\n%UserEventCreationConfigDeleteResponse\x12\x32\n\x03key\x18\x01 \x01(\x0b\x32%.arista.event.v1.UserEventCreationKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"_\n(UserEventCreationConfigDeleteSomeRequest\x12\x33\n\x04keys\x18\x01 \x03(\x0b\x32%.arista.event.v1.UserEventCreationKey\"n\n)UserEventCreationConfigDeleteSomeResponse\x12\x32\n\x03key\x18\x01 \x01(\x0b\x32%.arista.event.v1.UserEventCreationKey\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"n\n\'UserEventCreationConfigDeleteAllRequest\x12\x43\n\x11partial_eq_filter\x18\x01 \x03(\x0b\x32(.arista.event.v1.UserEventCreationConfig\"\xd5\x01\n(UserEventCreationConfigDeleteAllResponse\x12\x1e\n\x04type\x18\x01 \x01(\x0e\x32\x10.fmp.DeleteError\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x32\n\x03key\x18\x03 \x01(\x0b\x32%.arista.event.v1.UserEventCreationKey\x12(\n\x04time\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp2\x82\x04\n\x0c\x45ventService\x12G\n\x06GetOne\x12\x1d.arista.event.v1.EventRequest\x1a\x1e.arista.event.v1.EventResponse\x12R\n\x07GetSome\x12!.arista.event.v1.EventSomeRequest\x1a\".arista.event.v1.EventSomeResponse0\x01\x12U\n\x06GetAll\x12#.arista.event.v1.EventStreamRequest\x1a$.arista.event.v1.EventStreamResponse0\x01\x12X\n\tSubscribe\x12#.arista.event.v1.EventStreamRequest\x1a$.arista.event.v1.EventStreamResponse0\x01\x12M\n\x07GetMeta\x12#.arista.event.v1.EventStreamRequest\x1a\x1d.arista.event.v1.MetaResponse\x12U\n\rSubscribeMeta\x12#.arista.event.v1.EventStreamRequest\x1a\x1d.arista.event.v1.MetaResponse0\x01\x32\x91\n\n\x1c\x45ventAnnotationConfigService\x12g\n\x06GetOne\x12-.arista.event.v1.EventAnnotationConfigRequest\x1a..arista.event.v1.EventAnnotationConfigResponse\x12r\n\x07GetSome\x12\x31.arista.event.v1.EventAnnotationConfigSomeRequest\x1a\x32.arista.event.v1.EventAnnotationConfigSomeResponse0\x01\x12u\n\x06GetAll\x12\x33.arista.event.v1.EventAnnotationConfigStreamRequest\x1a\x34.arista.event.v1.EventAnnotationConfigStreamResponse0\x01\x12x\n\tSubscribe\x12\x33.arista.event.v1.EventAnnotationConfigStreamRequest\x1a\x34.arista.event.v1.EventAnnotationConfigStreamResponse0\x01\x12]\n\x07GetMeta\x12\x33.arista.event.v1.EventAnnotationConfigStreamRequest\x1a\x1d.arista.event.v1.MetaResponse\x12\x65\n\rSubscribeMeta\x12\x33.arista.event.v1.EventAnnotationConfigStreamRequest\x1a\x1d.arista.event.v1.MetaResponse0\x01\x12j\n\x03Set\x12\x30.arista.event.v1.EventAnnotationConfigSetRequest\x1a\x31.arista.event.v1.EventAnnotationConfigSetResponse\x12x\n\x07SetSome\x12\x34.arista.event.v1.EventAnnotationConfigSetSomeRequest\x1a\x35.arista.event.v1.EventAnnotationConfigSetSomeResponse0\x01\x12s\n\x06\x44\x65lete\x12\x33.arista.event.v1.EventAnnotationConfigDeleteRequest\x1a\x34.arista.event.v1.EventAnnotationConfigDeleteResponse\x12\x81\x01\n\nDeleteSome\x12\x37.arista.event.v1.EventAnnotationConfigDeleteSomeRequest\x1a\x38.arista.event.v1.EventAnnotationConfigDeleteSomeResponse0\x01\x12~\n\tDeleteAll\x12\x36.arista.event.v1.EventAnnotationConfigDeleteAllRequest\x1a\x37.arista.event.v1.EventAnnotationConfigDeleteAllResponse0\x01\x32\xbc\n\n\x1eUserEventCreationConfigService\x12k\n\x06GetOne\x12/.arista.event.v1.UserEventCreationConfigRequest\x1a\x30.arista.event.v1.UserEventCreationConfigResponse\x12v\n\x07GetSome\x12\x33.arista.event.v1.UserEventCreationConfigSomeRequest\x1a\x34.arista.event.v1.UserEventCreationConfigSomeResponse0\x01\x12y\n\x06GetAll\x12\x35.arista.event.v1.UserEventCreationConfigStreamRequest\x1a\x36.arista.event.v1.UserEventCreationConfigStreamResponse0\x01\x12|\n\tSubscribe\x12\x35.arista.event.v1.UserEventCreationConfigStreamRequest\x1a\x36.arista.event.v1.UserEventCreationConfigStreamResponse0\x01\x12_\n\x07GetMeta\x12\x35.arista.event.v1.UserEventCreationConfigStreamRequest\x1a\x1d.arista.event.v1.MetaResponse\x12g\n\rSubscribeMeta\x12\x35.arista.event.v1.UserEventCreationConfigStreamRequest\x1a\x1d.arista.event.v1.MetaResponse0\x01\x12n\n\x03Set\x12\x32.arista.event.v1.UserEventCreationConfigSetRequest\x1a\x33.arista.event.v1.UserEventCreationConfigSetResponse\x12|\n\x07SetSome\x12\x36.arista.event.v1.UserEventCreationConfigSetSomeRequest\x1a\x37.arista.event.v1.UserEventCreationConfigSetSomeResponse0\x01\x12w\n\x06\x44\x65lete\x12\x35.arista.event.v1.UserEventCreationConfigDeleteRequest\x1a\x36.arista.event.v1.UserEventCreationConfigDeleteResponse\x12\x85\x01\n\nDeleteSome\x12\x39.arista.event.v1.UserEventCreationConfigDeleteSomeRequest\x1a:.arista.event.v1.UserEventCreationConfigDeleteSomeResponse0\x01\x12\x82\x01\n\tDeleteAll\x12\x38.arista.event.v1.UserEventCreationConfigDeleteAllRequest\x1a\x39.arista.event.v1.UserEventCreationConfigDeleteAllResponse0\x01\x42\x44ZBgithub.com/aristanetworks/cloudvision-go/api/arista/event.v1;eventb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'arista.event.v1.services.gen_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'ZBgithub.com/aristanetworks/cloudvision-go/api/arista/event.v1;event'
  _globals['_METARESPONSE']._serialized_start=235
  _globals['_METARESPONSE']._serialized_end=383
  _globals['_EVENTREQUEST']._serialized_start=385
  _globals['_EVENTREQUEST']._serialized_end=481
  _globals['_EVENTRESPONSE']._serialized_start=483
  _globals['_EVENTRESPONSE']._serialized_end=579
  _globals['_EVENTSOMEREQUEST']._serialized_start=581
  _globals['_EVENTSOMEREQUEST']._serialized_end=682
  _globals['_EVENTSOMERESPONSE']._serialized_start=685
  _globals['_EVENTSOMERESPONSE']._serialized_end=830
  _globals['_EVENTSTREAMREQUEST']._serialized_start=832
  _globals['_EVENTSTREAMREQUEST']._serialized_end=942
  _globals['_EVENTSTREAMRESPONSE']._serialized_start=945
  _globals['_EVENTSTREAMRESPONSE']._serialized_end=1094
  _globals['_EVENTANNOTATIONCONFIGREQUEST']._serialized_start=1096
  _globals['_EVENTANNOTATIONCONFIGREQUEST']._serialized_end=1208
  _globals['_EVENTANNOTATIONCONFIGRESPONSE']._serialized_start=1211
  _globals['_EVENTANNOTATIONCONFIGRESPONSE']._serialized_end=1339
  _globals['_EVENTANNOTATIONCONFIGSOMEREQUEST']._serialized_start=1341
  _globals['_EVENTANNOTATIONCONFIGSOMEREQUEST']._serialized_end=1458
  _globals['_EVENTANNOTATIONCONFIGSOMERESPONSE']._serialized_start=1461
  _globals['_EVENTANNOTATIONCONFIGSOMERESPONSE']._serialized_end=1638
  _globals['_EVENTANNOTATIONCONFIGSTREAMREQUEST']._serialized_start=1641
  _globals['_EVENTANNOTATIONCONFIGSTREAMREQUEST']._serialized_end=1783
  _globals['_EVENTANNOTATIONCONFIGSTREAMRESPONSE']._serialized_start=1786
  _globals['_EVENTANNOTATIONCONFIGSTREAMRESPONSE']._serialized_end=1967
  _globals['_EVENTANNOTATIONCONFIGSETREQUEST']._serialized_start=1969
  _globals['_EVENTANNOTATIONCONFIGSETREQUEST']._serialized_end=2057
  _globals['_EVENTANNOTATIONCONFIGSETRESPONSE']._serialized_start=2060
  _globals['_EVENTANNOTATIONCONFIGSETRESPONSE']._serialized_end=2191
  _globals['_EVENTANNOTATIONCONFIGSETSOMEREQUEST']._serialized_start=2193
  _globals['_EVENTANNOTATIONCONFIGSETSOMEREQUEST']._serialized_end=2286
  _globals['_EVENTANNOTATIONCONFIGSETSOMERESPONSE']._serialized_start=2288
  _globals['_EVENTANNOTATIONCONFIGSETSOMERESPONSE']._serialized_end=2381
  _globals['_EVENTANNOTATIONCONFIGDELETEREQUEST']._serialized_start=2383
  _globals['_EVENTANNOTATIONCONFIGDELETEREQUEST']._serialized_end=2459
  _globals['_EVENTANNOTATIONCONFIGDELETERESPONSE']._serialized_start=2461
  _globals['_EVENTANNOTATIONCONFIGDELETERESPONSE']._serialized_end=2580
  _globals['_EVENTANNOTATIONCONFIGDELETESOMEREQUEST']._serialized_start=2582
  _globals['_EVENTANNOTATIONCONFIGDELETESOMEREQUEST']._serialized_end=2663
  _globals['_EVENTANNOTATIONCONFIGDELETESOMERESPONSE']._serialized_start=2665
  _globals['_EVENTANNOTATIONCONFIGDELETESOMERESPONSE']._serialized_end=2761
  _globals['_EVENTANNOTATIONCONFIGDELETEALLREQUEST']._serialized_start=2763
  _globals['_EVENTANNOTATIONCONFIGDELETEALLREQUEST']._serialized_end=2869
  _globals['_EVENTANNOTATIONCONFIGDELETEALLRESPONSE']._serialized_start=2872
  _globals['_EVENTANNOTATIONCONFIGDELETEALLRESPONSE']._serialized_end=3071
  _globals['_USEREVENTCREATIONCONFIGREQUEST']._serialized_start=3073
  _globals['_USEREVENTCREATIONCONFIGREQUEST']._serialized_end=3199
  _globals['_USEREVENTCREATIONCONFIGRESPONSE']._serialized_start=3202
  _globals['_USEREVENTCREATIONCONFIGRESPONSE']._serialized_end=3334
  _globals['_USEREVENTCREATIONCONFIGSOMEREQUEST']._serialized_start=3337
  _globals['_USEREVENTCREATIONCONFIGSOMEREQUEST']._serialized_end=3468
  _globals['_USEREVENTCREATIONCONFIGSOMERESPONSE']._serialized_start=3471
  _globals['_USEREVENTCREATIONCONFIGSOMERESPONSE']._serialized_end=3652
  _globals['_USEREVENTCREATIONCONFIGSTREAMREQUEST']._serialized_start=3655
  _globals['_USEREVENTCREATIONCONFIGSTREAMREQUEST']._serialized_end=3801
  _globals['_USEREVENTCREATIONCONFIGSTREAMRESPONSE']._serialized_start=3804
  _globals['_USEREVENTCREATIONCONFIGSTREAMRESPONSE']._serialized_end=3989
  _globals['_USEREVENTCREATIONCONFIGSETREQUEST']._serialized_start=3991
  _globals['_USEREVENTCREATIONCONFIGSETREQUEST']._serialized_end=4083
  _globals['_USEREVENTCREATIONCONFIGSETRESPONSE']._serialized_start=4086
  _globals['_USEREVENTCREATIONCONFIGSETRESPONSE']._serialized_end=4221
  _globals['_USEREVENTCREATIONCONFIGSETSOMEREQUEST']._serialized_start=4223
  _globals['_USEREVENTCREATIONCONFIGSETSOMEREQUEST']._serialized_end=4320
  _globals['_USEREVENTCREATIONCONFIGSETSOMERESPONSE']._serialized_start=4322
  _globals['_USEREVENTCREATIONCONFIGSETSOMERESPONSE']._serialized_end=4429
  _globals['_USEREVENTCREATIONCONFIGDELETEREQUEST']._serialized_start=4431
  _globals['_USEREVENTCREATIONCONFIGDELETEREQUEST']._serialized_end=4521
  _globals['_USEREVENTCREATIONCONFIGDELETERESPONSE']._serialized_start=4524
  _globals['_USEREVENTCREATIONCONFIGDELETERESPONSE']._serialized_end=4657
  _globals['_USEREVENTCREATIONCONFIGDELETESOMEREQUEST']._serialized_start=4659
  _globals['_USEREVENTCREATIONCONFIGDELETESOMEREQUEST']._serialized_end=4754
  _globals['_USEREVENTCREATIONCONFIGDELETESOMERESPONSE']._serialized_start=4756
  _globals['_USEREVENTCREATIONCONFIGDELETESOMERESPONSE']._serialized_end=4866
  _globals['_USEREVENTCREATIONCONFIGDELETEALLREQUEST']._serialized_start=4868
  _globals['_USEREVENTCREATIONCONFIGDELETEALLREQUEST']._serialized_end=4978
  _globals['_USEREVENTCREATIONCONFIGDELETEALLRESPONSE']._serialized_start=4981
  _globals['_USEREVENTCREATIONCONFIGDELETEALLRESPONSE']._serialized_end=5194
  _globals['_EVENTSERVICE']._serialized_start=5197
  _globals['_EVENTSERVICE']._serialized_end=5711
  _globals['_EVENTANNOTATIONCONFIGSERVICE']._serialized_start=5714
  _globals['_EVENTANNOTATIONCONFIGSERVICE']._serialized_end=7011
  _globals['_USEREVENTCREATIONCONFIGSERVICE']._serialized_start=7014
  _globals['_USEREVENTCREATIONCONFIGSERVICE']._serialized_end=8354
# @@protoc_insertion_point(module_scope)
