# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: arista/alert.v1/services.gen.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from arista.alert.v1 import alert_pb2 as arista_dot_alert_dot_v1_dot_alert__pb2
from arista.time import time_pb2 as arista_dot_time_dot_time__pb2
from arista.subscriptions import subscriptions_pb2 as arista_dot_subscriptions_dot_subscriptions__pb2
from fmp import deletes_pb2 as fmp_dot_deletes__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\"arista/alert.v1/services.gen.proto\x12\x0f\x61rista.alert.v1\x1a\x1b\x61rista/alert.v1/alert.proto\x1a\x16\x61rista/time/time.proto\x1a(arista/subscriptions/subscriptions.proto\x1a\x11\x66mp/deletes.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\"\x94\x01\n\x0cMetaResponse\x12(\n\x04time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x02 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\x12+\n\x05\x63ount\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\"8\n\x0c\x41lertRequest\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"`\n\rAlertResponse\x12%\n\x05value\x18\x01 \x01(\x0b\x32\x16.arista.alert.v1.Alert\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\";\n\x12\x41lertStreamRequest\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\"\x95\x01\n\x13\x41lertStreamResponse\x12%\n\x05value\x18\x01 \x01(\x0b\x32\x16.arista.alert.v1.Alert\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x03 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\">\n\x12\x41lertConfigRequest\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"l\n\x13\x41lertConfigResponse\x12+\n\x05value\x18\x01 \x01(\x0b\x32\x1c.arista.alert.v1.AlertConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"A\n\x18\x41lertConfigStreamRequest\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\"\xa1\x01\n\x19\x41lertConfigStreamResponse\x12+\n\x05value\x18\x01 \x01(\x0b\x32\x1c.arista.alert.v1.AlertConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x03 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\"D\n\x15\x41lertConfigSetRequest\x12+\n\x05value\x18\x01 \x01(\x0b\x32\x1c.arista.alert.v1.AlertConfig\"o\n\x16\x41lertConfigSetResponse\x12+\n\x05value\x18\x01 \x01(\x0b\x32\x1c.arista.alert.v1.AlertConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"m\n\x16\x44\x65\x66\x61ultTemplateRequest\x12)\n\x03key\x18\x01 \x01(\x0b\x32\x1c.arista.alert.v1.TemplateKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"t\n\x17\x44\x65\x66\x61ultTemplateResponse\x12/\n\x05value\x18\x01 \x01(\x0b\x32 .arista.alert.v1.DefaultTemplate\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"r\n\x1a\x44\x65\x66\x61ultTemplateSomeRequest\x12*\n\x04keys\x18\x01 \x03(\x0b\x32\x1c.arista.alert.v1.TemplateKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\xa5\x01\n\x1b\x44\x65\x66\x61ultTemplateSomeResponse\x12/\n\x05value\x18\x01 \x01(\x0b\x32 .arista.alert.v1.DefaultTemplate\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12(\n\x04time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"E\n\x1c\x44\x65\x66\x61ultTemplateStreamRequest\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\"\xa9\x01\n\x1d\x44\x65\x66\x61ultTemplateStreamResponse\x12/\n\x05value\x18\x01 \x01(\x0b\x32 .arista.alert.v1.DefaultTemplate\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x03 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\"\x80\x01\n#DefaultTemplateBatchedStreamRequest\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\x12\x32\n\x0cmax_messages\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\"i\n$DefaultTemplateBatchedStreamResponse\x12\x41\n\tresponses\x18\x01 \x03(\x0b\x32..arista.alert.v1.DefaultTemplateStreamResponse\"l\n\x15TemplateConfigRequest\x12)\n\x03key\x18\x01 \x01(\x0b\x32\x1c.arista.alert.v1.TemplateKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"r\n\x16TemplateConfigResponse\x12.\n\x05value\x18\x01 \x01(\x0b\x32\x1f.arista.alert.v1.TemplateConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"q\n\x19TemplateConfigSomeRequest\x12*\n\x04keys\x18\x01 \x03(\x0b\x32\x1c.arista.alert.v1.TemplateKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\xa3\x01\n\x1aTemplateConfigSomeResponse\x12.\n\x05value\x18\x01 \x01(\x0b\x32\x1f.arista.alert.v1.TemplateConfig\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12(\n\x04time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"D\n\x1bTemplateConfigStreamRequest\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\"\xa7\x01\n\x1cTemplateConfigStreamResponse\x12.\n\x05value\x18\x01 \x01(\x0b\x32\x1f.arista.alert.v1.TemplateConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x04type\x18\x03 \x01(\x0e\x32\x1f.arista.subscriptions.Operation\"\x7f\n\"TemplateConfigBatchedStreamRequest\x12%\n\x04time\x18\x03 \x01(\x0b\x32\x17.arista.time.TimeBounds\x12\x32\n\x0cmax_messages\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\"g\n#TemplateConfigBatchedStreamResponse\x12@\n\tresponses\x18\x01 \x03(\x0b\x32-.arista.alert.v1.TemplateConfigStreamResponse\"J\n\x18TemplateConfigSetRequest\x12.\n\x05value\x18\x01 \x01(\x0b\x32\x1f.arista.alert.v1.TemplateConfig\"u\n\x19TemplateConfigSetResponse\x12.\n\x05value\x18\x01 \x01(\x0b\x32\x1f.arista.alert.v1.TemplateConfig\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"O\n\x1cTemplateConfigSetSomeRequest\x12/\n\x06values\x18\x01 \x03(\x0b\x32\x1f.arista.alert.v1.TemplateConfig\"Y\n\x1dTemplateConfigSetSomeResponse\x12)\n\x03key\x18\x01 \x01(\x0b\x32\x1c.arista.alert.v1.TemplateKey\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"H\n\x1bTemplateConfigDeleteRequest\x12)\n\x03key\x18\x01 \x01(\x0b\x32\x1c.arista.alert.v1.TemplateKey\"s\n\x1cTemplateConfigDeleteResponse\x12)\n\x03key\x18\x01 \x01(\x0b\x32\x1c.arista.alert.v1.TemplateKey\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"M\n\x1fTemplateConfigDeleteSomeRequest\x12*\n\x04keys\x18\x01 \x03(\x0b\x32\x1c.arista.alert.v1.TemplateKey\"\\\n TemplateConfigDeleteSomeResponse\x12)\n\x03key\x18\x01 \x01(\x0b\x32\x1c.arista.alert.v1.TemplateKey\x12\r\n\x05\x65rror\x18\x02 \x01(\t\" \n\x1eTemplateConfigDeleteAllRequest\"\xc3\x01\n\x1fTemplateConfigDeleteAllResponse\x12\x1e\n\x04type\x18\x01 \x01(\x0e\x32\x10.fmp.DeleteError\x12+\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12)\n\x03key\x18\x03 \x01(\x0b\x32\x1c.arista.alert.v1.TemplateKey\x12(\n\x04time\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp2\xdf\x02\n\x0c\x41lertService\x12G\n\x06GetOne\x12\x1d.arista.alert.v1.AlertRequest\x1a\x1e.arista.alert.v1.AlertResponse\x12U\n\x06GetAll\x12#.arista.alert.v1.AlertStreamRequest\x1a$.arista.alert.v1.AlertStreamResponse0\x01\x12X\n\tSubscribe\x12#.arista.alert.v1.AlertStreamRequest\x1a$.arista.alert.v1.AlertStreamResponse0\x01\x12U\n\rSubscribeMeta\x12#.arista.alert.v1.AlertStreamRequest\x1a\x1d.arista.alert.v1.MetaResponse0\x01\x32\xe7\x03\n\x12\x41lertConfigService\x12S\n\x06GetOne\x12#.arista.alert.v1.AlertConfigRequest\x1a$.arista.alert.v1.AlertConfigResponse\x12\x61\n\x06GetAll\x12).arista.alert.v1.AlertConfigStreamRequest\x1a*.arista.alert.v1.AlertConfigStreamResponse0\x01\x12\x64\n\tSubscribe\x12).arista.alert.v1.AlertConfigStreamRequest\x1a*.arista.alert.v1.AlertConfigStreamResponse0\x01\x12[\n\rSubscribeMeta\x12).arista.alert.v1.AlertConfigStreamRequest\x1a\x1d.arista.alert.v1.MetaResponse0\x01\x12V\n\x03Set\x12&.arista.alert.v1.AlertConfigSetRequest\x1a\'.arista.alert.v1.AlertConfigSetResponse2\xf4\x06\n\x16\x44\x65\x66\x61ultTemplateService\x12[\n\x06GetOne\x12\'.arista.alert.v1.DefaultTemplateRequest\x1a(.arista.alert.v1.DefaultTemplateResponse\x12\x66\n\x07GetSome\x12+.arista.alert.v1.DefaultTemplateSomeRequest\x1a,.arista.alert.v1.DefaultTemplateSomeResponse0\x01\x12i\n\x06GetAll\x12-.arista.alert.v1.DefaultTemplateStreamRequest\x1a..arista.alert.v1.DefaultTemplateStreamResponse0\x01\x12l\n\tSubscribe\x12-.arista.alert.v1.DefaultTemplateStreamRequest\x1a..arista.alert.v1.DefaultTemplateStreamResponse0\x01\x12W\n\x07GetMeta\x12-.arista.alert.v1.DefaultTemplateStreamRequest\x1a\x1d.arista.alert.v1.MetaResponse\x12_\n\rSubscribeMeta\x12-.arista.alert.v1.DefaultTemplateStreamRequest\x1a\x1d.arista.alert.v1.MetaResponse0\x01\x12~\n\rGetAllBatched\x12\x34.arista.alert.v1.DefaultTemplateBatchedStreamRequest\x1a\x35.arista.alert.v1.DefaultTemplateBatchedStreamResponse0\x01\x12\x81\x01\n\x10SubscribeBatched\x12\x34.arista.alert.v1.DefaultTemplateBatchedStreamRequest\x1a\x35.arista.alert.v1.DefaultTemplateBatchedStreamResponse0\x01\x32\xfc\n\n\x15TemplateConfigService\x12Y\n\x06GetOne\x12&.arista.alert.v1.TemplateConfigRequest\x1a\'.arista.alert.v1.TemplateConfigResponse\x12\x64\n\x07GetSome\x12*.arista.alert.v1.TemplateConfigSomeRequest\x1a+.arista.alert.v1.TemplateConfigSomeResponse0\x01\x12g\n\x06GetAll\x12,.arista.alert.v1.TemplateConfigStreamRequest\x1a-.arista.alert.v1.TemplateConfigStreamResponse0\x01\x12j\n\tSubscribe\x12,.arista.alert.v1.TemplateConfigStreamRequest\x1a-.arista.alert.v1.TemplateConfigStreamResponse0\x01\x12V\n\x07GetMeta\x12,.arista.alert.v1.TemplateConfigStreamRequest\x1a\x1d.arista.alert.v1.MetaResponse\x12^\n\rSubscribeMeta\x12,.arista.alert.v1.TemplateConfigStreamRequest\x1a\x1d.arista.alert.v1.MetaResponse0\x01\x12\\\n\x03Set\x12).arista.alert.v1.TemplateConfigSetRequest\x1a*.arista.alert.v1.TemplateConfigSetResponse\x12j\n\x07SetSome\x12-.arista.alert.v1.TemplateConfigSetSomeRequest\x1a..arista.alert.v1.TemplateConfigSetSomeResponse0\x01\x12\x65\n\x06\x44\x65lete\x12,.arista.alert.v1.TemplateConfigDeleteRequest\x1a-.arista.alert.v1.TemplateConfigDeleteResponse\x12s\n\nDeleteSome\x12\x30.arista.alert.v1.TemplateConfigDeleteSomeRequest\x1a\x31.arista.alert.v1.TemplateConfigDeleteSomeResponse0\x01\x12p\n\tDeleteAll\x12/.arista.alert.v1.TemplateConfigDeleteAllRequest\x1a\x30.arista.alert.v1.TemplateConfigDeleteAllResponse0\x01\x12|\n\rGetAllBatched\x12\x33.arista.alert.v1.TemplateConfigBatchedStreamRequest\x1a\x34.arista.alert.v1.TemplateConfigBatchedStreamResponse0\x01\x12\x7f\n\x10SubscribeBatched\x12\x33.arista.alert.v1.TemplateConfigBatchedStreamRequest\x1a\x34.arista.alert.v1.TemplateConfigBatchedStreamResponse0\x01\x42\x44ZBgithub.com/aristanetworks/cloudvision-go/api/arista/alert.v1;alertb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'arista.alert.v1.services.gen_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'ZBgithub.com/aristanetworks/cloudvision-go/api/arista/alert.v1;alert'
  _globals['_METARESPONSE']._serialized_start=235
  _globals['_METARESPONSE']._serialized_end=383
  _globals['_ALERTREQUEST']._serialized_start=385
  _globals['_ALERTREQUEST']._serialized_end=441
  _globals['_ALERTRESPONSE']._serialized_start=443
  _globals['_ALERTRESPONSE']._serialized_end=539
  _globals['_ALERTSTREAMREQUEST']._serialized_start=541
  _globals['_ALERTSTREAMREQUEST']._serialized_end=600
  _globals['_ALERTSTREAMRESPONSE']._serialized_start=603
  _globals['_ALERTSTREAMRESPONSE']._serialized_end=752
  _globals['_ALERTCONFIGREQUEST']._serialized_start=754
  _globals['_ALERTCONFIGREQUEST']._serialized_end=816
  _globals['_ALERTCONFIGRESPONSE']._serialized_start=818
  _globals['_ALERTCONFIGRESPONSE']._serialized_end=926
  _globals['_ALERTCONFIGSTREAMREQUEST']._serialized_start=928
  _globals['_ALERTCONFIGSTREAMREQUEST']._serialized_end=993
  _globals['_ALERTCONFIGSTREAMRESPONSE']._serialized_start=996
  _globals['_ALERTCONFIGSTREAMRESPONSE']._serialized_end=1157
  _globals['_ALERTCONFIGSETREQUEST']._serialized_start=1159
  _globals['_ALERTCONFIGSETREQUEST']._serialized_end=1227
  _globals['_ALERTCONFIGSETRESPONSE']._serialized_start=1229
  _globals['_ALERTCONFIGSETRESPONSE']._serialized_end=1340
  _globals['_DEFAULTTEMPLATEREQUEST']._serialized_start=1342
  _globals['_DEFAULTTEMPLATEREQUEST']._serialized_end=1451
  _globals['_DEFAULTTEMPLATERESPONSE']._serialized_start=1453
  _globals['_DEFAULTTEMPLATERESPONSE']._serialized_end=1569
  _globals['_DEFAULTTEMPLATESOMEREQUEST']._serialized_start=1571
  _globals['_DEFAULTTEMPLATESOMEREQUEST']._serialized_end=1685
  _globals['_DEFAULTTEMPLATESOMERESPONSE']._serialized_start=1688
  _globals['_DEFAULTTEMPLATESOMERESPONSE']._serialized_end=1853
  _globals['_DEFAULTTEMPLATESTREAMREQUEST']._serialized_start=1855
  _globals['_DEFAULTTEMPLATESTREAMREQUEST']._serialized_end=1924
  _globals['_DEFAULTTEMPLATESTREAMRESPONSE']._serialized_start=1927
  _globals['_DEFAULTTEMPLATESTREAMRESPONSE']._serialized_end=2096
  _globals['_DEFAULTTEMPLATEBATCHEDSTREAMREQUEST']._serialized_start=2099
  _globals['_DEFAULTTEMPLATEBATCHEDSTREAMREQUEST']._serialized_end=2227
  _globals['_DEFAULTTEMPLATEBATCHEDSTREAMRESPONSE']._serialized_start=2229
  _globals['_DEFAULTTEMPLATEBATCHEDSTREAMRESPONSE']._serialized_end=2334
  _globals['_TEMPLATECONFIGREQUEST']._serialized_start=2336
  _globals['_TEMPLATECONFIGREQUEST']._serialized_end=2444
  _globals['_TEMPLATECONFIGRESPONSE']._serialized_start=2446
  _globals['_TEMPLATECONFIGRESPONSE']._serialized_end=2560
  _globals['_TEMPLATECONFIGSOMEREQUEST']._serialized_start=2562
  _globals['_TEMPLATECONFIGSOMEREQUEST']._serialized_end=2675
  _globals['_TEMPLATECONFIGSOMERESPONSE']._serialized_start=2678
  _globals['_TEMPLATECONFIGSOMERESPONSE']._serialized_end=2841
  _globals['_TEMPLATECONFIGSTREAMREQUEST']._serialized_start=2843
  _globals['_TEMPLATECONFIGSTREAMREQUEST']._serialized_end=2911
  _globals['_TEMPLATECONFIGSTREAMRESPONSE']._serialized_start=2914
  _globals['_TEMPLATECONFIGSTREAMRESPONSE']._serialized_end=3081
  _globals['_TEMPLATECONFIGBATCHEDSTREAMREQUEST']._serialized_start=3083
  _globals['_TEMPLATECONFIGBATCHEDSTREAMREQUEST']._serialized_end=3210
  _globals['_TEMPLATECONFIGBATCHEDSTREAMRESPONSE']._serialized_start=3212
  _globals['_TEMPLATECONFIGBATCHEDSTREAMRESPONSE']._serialized_end=3315
  _globals['_TEMPLATECONFIGSETREQUEST']._serialized_start=3317
  _globals['_TEMPLATECONFIGSETREQUEST']._serialized_end=3391
  _globals['_TEMPLATECONFIGSETRESPONSE']._serialized_start=3393
  _globals['_TEMPLATECONFIGSETRESPONSE']._serialized_end=3510
  _globals['_TEMPLATECONFIGSETSOMEREQUEST']._serialized_start=3512
  _globals['_TEMPLATECONFIGSETSOMEREQUEST']._serialized_end=3591
  _globals['_TEMPLATECONFIGSETSOMERESPONSE']._serialized_start=3593
  _globals['_TEMPLATECONFIGSETSOMERESPONSE']._serialized_end=3682
  _globals['_TEMPLATECONFIGDELETEREQUEST']._serialized_start=3684
  _globals['_TEMPLATECONFIGDELETEREQUEST']._serialized_end=3756
  _globals['_TEMPLATECONFIGDELETERESPONSE']._serialized_start=3758
  _globals['_TEMPLATECONFIGDELETERESPONSE']._serialized_end=3873
  _globals['_TEMPLATECONFIGDELETESOMEREQUEST']._serialized_start=3875
  _globals['_TEMPLATECONFIGDELETESOMEREQUEST']._serialized_end=3952
  _globals['_TEMPLATECONFIGDELETESOMERESPONSE']._serialized_start=3954
  _globals['_TEMPLATECONFIGDELETESOMERESPONSE']._serialized_end=4046
  _globals['_TEMPLATECONFIGDELETEALLREQUEST']._serialized_start=4048
  _globals['_TEMPLATECONFIGDELETEALLREQUEST']._serialized_end=4080
  _globals['_TEMPLATECONFIGDELETEALLRESPONSE']._serialized_start=4083
  _globals['_TEMPLATECONFIGDELETEALLRESPONSE']._serialized_end=4278
  _globals['_ALERTSERVICE']._serialized_start=4281
  _globals['_ALERTSERVICE']._serialized_end=4632
  _globals['_ALERTCONFIGSERVICE']._serialized_start=4635
  _globals['_ALERTCONFIGSERVICE']._serialized_end=5122
  _globals['_DEFAULTTEMPLATESERVICE']._serialized_start=5125
  _globals['_DEFAULTTEMPLATESERVICE']._serialized_end=6009
  _globals['_TEMPLATECONFIGSERVICE']._serialized_start=6012
  _globals['_TEMPLATECONFIGSERVICE']._serialized_end=7416
# @@protoc_insertion_point(module_scope)
