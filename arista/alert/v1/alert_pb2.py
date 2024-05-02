# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: arista/alert.v1/alert.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1b\x61rista/alert.v1/alert.proto\x12\x0f\x61rista.alert.v1\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x14\x66mp/extensions.proto\x1a\x12\x66mp/wrappers.proto\"\xa9\x01\n\x0b\x41lertConfig\x12+\n\x08settings\x18\x01 \x01(\x0b\x32\x19.arista.alert.v1.Settings\x12%\n\x05rules\x18\x02 \x01(\x0b\x32\x16.arista.alert.v1.Rules\x12:\n\x10\x62roadcast_groups\x18\x03 \x01(\x0b\x32 .arista.alert.v1.BroadcastGroups:\n\x90\x8e\x19\x01\xa2\x8e\x19\x02rw\"\xf8\x01\n\x05\x41lert\x12;\n\x14\x63onfiguration_errors\x18\x01 \x01(\x0b\x32\x1d.arista.alert.v1.ConfigErrors\x12\x38\n\x0f\x65ndpoint_errors\x18\x02 \x01(\x0b\x32\x1f.arista.alert.v1.EndpointErrors\x12\x34\n\x10last_modified_at\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x36\n\x10last_modified_by\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue:\n\x90\x8e\x19\x01\xa2\x8e\x19\x02ro\"<\n\x0c\x43onfigErrors\x12,\n\x06values\x18\x01 \x03(\x0b\x32\x1c.arista.alert.v1.ConfigError\"\x9c\x01\n\x0b\x43onfigError\x12*\n\x04path\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\nerror_type\x18\x02 \x01(\x0e\x32 .arista.alert.v1.ConfigErrorType\x12+\n\x05\x65rror\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"@\n\x0e\x45ndpointErrors\x12.\n\x06values\x18\x01 \x03(\x0b\x32\x1e.arista.alert.v1.EndpointError\"\x98\x02\n\rEndpointError\x12\x33\n\rendpoint_type\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12:\n\x14\x62roadcast_group_name\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x31\n\x0c\x63onfig_index\x18\x03 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\x12\x36\n\nerror_type\x18\x04 \x01(\x0e\x32\".arista.alert.v1.EndpointErrorType\x12+\n\x05\x65rror\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xcf\x07\n\x08Settings\x12-\n\x05\x65mail\x18\x01 \x01(\x0b\x32\x1e.arista.alert.v1.EmailSettings\x12+\n\x04http\x18\x02 \x01(\x0b\x32\x1d.arista.alert.v1.HttpSettings\x12-\n\x05slack\x18\x03 \x01(\x0b\x32\x1e.arista.alert.v1.SlackSettings\x12\x35\n\tvictorops\x18\x04 \x01(\x0b\x32\".arista.alert.v1.VictoropsSettings\x12\x35\n\tpagerduty\x18\x05 \x01(\x0b\x32\".arista.alert.v1.PagerdutySettings\x12\x33\n\x08opsgenie\x18\x06 \x01(\x0b\x32!.arista.alert.v1.OpsgenieSettings\x12\x32\n\x05gchat\x18\x07 \x01(\x0b\x32#.arista.alert.v1.GoogleChatSettings\x12\x31\n\x07msteams\x18\x08 \x01(\x0b\x32 .arista.alert.v1.MsTeamsSettings\x12\x37\n\ninhibition\x18\t \x01(\x0b\x32#.arista.alert.v1.InhibitionSettings\x12.\n\x08\x62\x61se_url\x18\n \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12.\n\x08timezone\x18\x0b \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\x06syslog\x18\x0c \x01(\x0b\x32\x1f.arista.alert.v1.SyslogSettings\x12+\n\x04snmp\x18\r \x01(\x0b\x32\x1d.arista.alert.v1.SNMPSettings\x12\x33\n\x08sendgrid\x18\x0e \x01(\x0b\x32!.arista.alert.v1.SendgridSettings\x12\x36\n\ncue_syslog\x18\x0f \x01(\x0b\x32\".arista.alert.v1.CueSyslogSettings\x12\x32\n\x08\x63ue_snmp\x18\x10 \x01(\x0b\x32 .arista.alert.v1.CueSNMPSettings\x12:\n\x0c\x63ue_sendgrid\x18\x11 \x01(\x0b\x32$.arista.alert.v1.CueSendgridSettings\x12-\n\thide_tags\x18\x12 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12+\n\x04zoom\x18\x13 \x01(\x0b\x32\x1d.arista.alert.v1.ZoomSettings\"\xf6\x02\n\rEmailSettings\x12*\n\x04\x66rom\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\tsmarthost\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x33\n\rauth_username\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x33\n\rauth_password\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\x0brequire_tls\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12:\n\x16single_alert_per_email\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x31\n\x0c\x61zure_o_auth\x18\x07 \x01(\x0b\x32\x1b.arista.alert.v1.AzureOAuth\"\xd3\x01\n\nAzureOAuth\x12/\n\tclient_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\ttenant_id\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x33\n\rclient_secret\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12.\n\x08\x61uth_uri\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xd5\x01\n\x0cHttpSettings\x12.\n\x08username\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12.\n\x08password\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\tproxy_url\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x0e\x63ustom_headers\x18\x04 \x01(\x0b\x32\x1c.arista.alert.v1.HttpHeaders\"\x95\x01\n\x0bHttpHeaders\x12\x38\n\x06values\x18\x01 \x03(\x0b\x32(.arista.alert.v1.HttpHeaders.ValuesEntry\x1aL\n\x0bValuesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12,\n\x05value\x18\x02 \x01(\x0b\x32\x1d.arista.alert.v1.HeaderValues:\x02\x38\x01\"\x1e\n\x0cHeaderValues\x12\x0e\n\x06values\x18\x01 \x03(\t\":\n\rSlackSettings\x12)\n\x03url\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"i\n\x11VictoropsSettings\x12)\n\x03key\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12)\n\x03url\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\">\n\x11PagerdutySettings\x12)\n\x03url\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"h\n\x10OpsgenieSettings\x12)\n\x03key\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12)\n\x03url\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"?\n\x12GoogleChatSettings\x12)\n\x03url\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"<\n\x0fMsTeamsSettings\x12)\n\x03url\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xd6\x02\n\x0eSyslogSettings\x12-\n\x07network\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12-\n\x07\x61\x64\x64ress\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12-\n\x08\x66\x61\x63ility\x18\x03 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\x12/\n\npriorities\x18\x04 \x01(\x0b\x32\x1b.arista.alert.v1.Priorities\x12)\n\x03tag\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12.\n\nper_device\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12+\n\x07use_tls\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"\xbd\x01\n\nPriorities\x12-\n\x08\x63ritical\x18\x01 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\x12*\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\x12)\n\x04warn\x18\x03 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\x12)\n\x04info\x18\x04 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\"n\n\x07\x43ueData\x12\x34\n\x06values\x18\x01 \x03(\x0b\x32$.arista.alert.v1.CueData.ValuesEntry\x1a-\n\x0bValuesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\xbc\x02\n\x11\x43ueSyslogSettings\x12-\n\x07network\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12-\n\x07\x61\x64\x64ress\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12)\n\x04port\x18\x03 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\x12?\n\x0emessage_format\x18\x04 \x01(\x0e\x32\'.arista.alert.v1.CueSyslogMessageFormat\x12\x35\n\x11\x61ppend_bom_header\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12&\n\x04\x64\x61ta\x18\x06 \x01(\x0b\x32\x18.arista.alert.v1.CueData\"\xa0\x02\n\x0cSNMPSettings\x12,\n\x06target\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12)\n\x04port\x18\x02 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\x12/\n\ttransport\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12,\n\x07version\x18\x04 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\x12\'\n\x04\x61uth\x18\x05 \x01(\x0b\x32\x19.arista.alert.v1.SNMPAuth\x12/\n\tengine_id\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xa3\x03\n\x08SNMPAuth\x12/\n\tcommunity\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12.\n\x08username\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12:\n\x0esecurity_level\x18\x03 \x01(\x0e\x32\".arista.alert.v1.SNMPSecurityLevel\x12\x42\n\x17\x61uthentication_protocol\x18\x04 \x01(\x0e\x32!.arista.alert.v1.SNMPAuthProtocol\x12?\n\x19\x61uthentication_passphrase\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12;\n\x10privacy_protocol\x18\x06 \x01(\x0e\x32!.arista.alert.v1.SNMPPrivProtocol\x12\x38\n\x12privacy_passphrase\x18\x07 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xac\x03\n\x0b\x43ueSNMPAuth\x12/\n\tcommunity\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12.\n\x08username\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12:\n\x0esecurity_level\x18\x03 \x01(\x0e\x32\".arista.alert.v1.SNMPSecurityLevel\x12\x45\n\x17\x61uthentication_protocol\x18\x04 \x01(\x0e\x32$.arista.alert.v1.CueSNMPAuthProtocol\x12?\n\x19\x61uthentication_passphrase\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12>\n\x10privacy_protocol\x18\x06 \x01(\x0e\x32$.arista.alert.v1.CueSNMPPrivProtocol\x12\x38\n\x12privacy_passphrase\x18\x07 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\x9d\x02\n\x0f\x43ueSNMPSettings\x12,\n\x06target\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12)\n\x04port\x18\x02 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\x12/\n\ttransport\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12,\n\x07version\x18\x04 \x01(\x0b\x32\x1b.google.protobuf.Int32Value\x12*\n\x04\x61uth\x18\x05 \x01(\x0b\x32\x1c.arista.alert.v1.CueSNMPAuth\x12&\n\x04\x64\x61ta\x18\x06 \x01(\x0b\x32\x18.arista.alert.v1.CueData\"m\n\x10SendgridSettings\x12-\n\x07\x61pi_key\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12*\n\x04\x66rom\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"p\n\x13\x43ueSendgridSettings\x12-\n\x07\x61pi_key\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12*\n\x04\x66rom\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"s\n\x0cZoomSettings\x12)\n\x03url\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x38\n\x12verification_token\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xa0\x01\n\x12InhibitionSettings\x12?\n\x06values\x18\x01 \x03(\x0b\x32/.arista.alert.v1.InhibitionSettings.ValuesEntry\x1aI\n\x0bValuesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12)\n\x05value\x18\x02 \x01(\x0b\x32\x1a.arista.alert.v1.EventList:\x02\x38\x01\"5\n\tEventList\x12(\n\x0b\x65vent_types\x18\x01 \x01(\x0b\x32\x13.fmp.RepeatedString\".\n\x05Rules\x12%\n\x06values\x18\x01 \x03(\x0b\x32\x15.arista.alert.v1.Rule\"\xcc\x01\n\x04Rule\x12.\n\x08sends_to\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x30\n\x0ematch_criteria\x18\x02 \x01(\x0b\x32\x18.arista.alert.v1.Matches\x12\x33\n\x0f\x63ontinue_checks\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12-\n\x07\x63omment\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\x8d\x02\n\x07Matches\x12\'\n\nseverities\x18\x01 \x01(\x0b\x32\x13.fmp.RepeatedString\x12$\n\x07\x64\x65vices\x18\x02 \x01(\x0b\x32\x13.fmp.RepeatedString\x12(\n\x0b\x65vent_types\x18\x03 \x01(\x0b\x32\x13.fmp.RepeatedString\x12\x31\n\x0b\x64\x65vice_tags\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\tintf_tags\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12%\n\x08rule_ids\x18\x06 \x01(\x0b\x32\x13.fmp.RepeatedString\"\x9f\x01\n\x0f\x42roadcastGroups\x12<\n\x06values\x18\x01 \x03(\x0b\x32,.arista.alert.v1.BroadcastGroups.ValuesEntry\x1aN\n\x0bValuesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12.\n\x05value\x18\x02 \x01(\x0b\x32\x1f.arista.alert.v1.BroadcastGroup:\x02\x38\x01\"\xd8\x06\n\x0e\x42roadcastGroup\x12.\n\x05\x65mail\x18\x01 \x01(\x0b\x32\x1f.arista.alert.v1.EmailEndpoints\x12\x32\n\x07webhook\x18\x02 \x01(\x0b\x32!.arista.alert.v1.WebhookEndpoints\x12.\n\x05slack\x18\x03 \x01(\x0b\x32\x1f.arista.alert.v1.SlackEndpoints\x12\x34\n\x08opsgenie\x18\x04 \x01(\x0b\x32\".arista.alert.v1.OpsgenieEndpoints\x12\x34\n\x08pushover\x18\x05 \x01(\x0b\x32\".arista.alert.v1.PushoverEndpoints\x12\x36\n\tpagerduty\x18\x06 \x01(\x0b\x32#.arista.alert.v1.PagerdutyEndpoints\x12\x36\n\tvictorops\x18\x07 \x01(\x0b\x32#.arista.alert.v1.VictorOpsEndpoints\x12\x33\n\x05gchat\x18\x08 \x01(\x0b\x32$.arista.alert.v1.GoogleChatEndpoints\x12\x32\n\x07msteams\x18\t \x01(\x0b\x32!.arista.alert.v1.MsTeamsEndpoints\x12\x34\n\x08sendgrid\x18\n \x01(\x0b\x32\".arista.alert.v1.SendgridEndpoints\x12\x30\n\x06syslog\x18\x0b \x01(\x0b\x32 .arista.alert.v1.SyslogEndpoints\x12,\n\x04snmp\x18\x0c \x01(\x0b\x32\x1e.arista.alert.v1.SNMPEndpoints\x12\x37\n\ncue_syslog\x18\r \x01(\x0b\x32#.arista.alert.v1.CueSyslogEndpoints\x12\x33\n\x08\x63ue_snmp\x18\x0e \x01(\x0b\x32!.arista.alert.v1.CueSnmpEndpoints\x12;\n\x0c\x63ue_sendgrid\x18\x0f \x01(\x0b\x32%.arista.alert.v1.CueSendgridEndpoints\x12,\n\x04zoom\x18\x10 \x01(\x0b\x32\x1e.arista.alert.v1.ZoomEndpoints\"@\n\x0e\x45mailEndpoints\x12.\n\x06values\x18\x01 \x03(\x0b\x32\x1e.arista.alert.v1.EmailEndpoint\"D\n\x10WebhookEndpoints\x12\x30\n\x06values\x18\x01 \x03(\x0b\x32 .arista.alert.v1.WebhookEndpoint\"@\n\x0eSlackEndpoints\x12.\n\x06values\x18\x01 \x03(\x0b\x32\x1e.arista.alert.v1.SlackEndpoint\"F\n\x11OpsgenieEndpoints\x12\x31\n\x06values\x18\x01 \x03(\x0b\x32!.arista.alert.v1.OpsgenieEndpoint\"F\n\x11PushoverEndpoints\x12\x31\n\x06values\x18\x01 \x03(\x0b\x32!.arista.alert.v1.PushoverEndpoint\"H\n\x12PagerdutyEndpoints\x12\x32\n\x06values\x18\x01 \x03(\x0b\x32\".arista.alert.v1.PagerdutyEndpoint\"H\n\x12VictorOpsEndpoints\x12\x32\n\x06values\x18\x01 \x03(\x0b\x32\".arista.alert.v1.VictorOpsEndpoint\"J\n\x13GoogleChatEndpoints\x12\x33\n\x06values\x18\x01 \x03(\x0b\x32#.arista.alert.v1.GoogleChatEndpoint\"D\n\x10MsTeamsEndpoints\x12\x30\n\x06values\x18\x01 \x03(\x0b\x32 .arista.alert.v1.MsTeamsEndpoint\"F\n\x11SendgridEndpoints\x12\x31\n\x06values\x18\x01 \x03(\x0b\x32!.arista.alert.v1.SendgridEndpoint\"L\n\x14\x43ueSendgridEndpoints\x12\x34\n\x06values\x18\x01 \x03(\x0b\x32$.arista.alert.v1.CueSendgridEndpoint\"B\n\x0fSyslogEndpoints\x12/\n\x06values\x18\x01 \x03(\x0b\x32\x1f.arista.alert.v1.SyslogEndpoint\"H\n\x12\x43ueSyslogEndpoints\x12\x32\n\x06values\x18\x01 \x03(\x0b\x32\".arista.alert.v1.CueSyslogEndpoint\">\n\rSNMPEndpoints\x12-\n\x06values\x18\x01 \x03(\x0b\x32\x1d.arista.alert.v1.SNMPEndpoint\"D\n\x10\x43ueSnmpEndpoints\x12\x30\n\x06values\x18\x01 \x03(\x0b\x32 .arista.alert.v1.CueSNMPEndpoint\">\n\rZoomEndpoints\x12-\n\x06values\x18\x01 \x03(\x0b\x32\x1d.arista.alert.v1.ZoomEndpoint\"l\n\rEmailEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12(\n\x02to\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\x8a\x02\n\x0fWebhookEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12)\n\x03url\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\rhttp_override\x18\x03 \x01(\x0b\x32\x1d.arista.alert.v1.HttpSettings\x12\x31\n\rsimple_output\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x30\n\x0csingle_alert\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"\xb3\x01\n\rSlackEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x34\n\rhttp_override\x18\x02 \x01(\x0b\x32\x1d.arista.alert.v1.HttpSettings\x12\x39\n\x11settings_override\x18\x03 \x01(\x0b\x32\x1e.arista.alert.v1.SlackSettings\"\xb9\x01\n\x10OpsgenieEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x34\n\rhttp_override\x18\x02 \x01(\x0b\x32\x1d.arista.alert.v1.HttpSettings\x12<\n\x11settings_override\x18\x03 \x01(\x0b\x32!.arista.alert.v1.OpsgenieSettings\"\xd8\x01\n\x10PushoverEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12+\n\x05token\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12.\n\x08user_key\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\rhttp_override\x18\x04 \x01(\x0b\x32\x1d.arista.alert.v1.HttpSettings\"\xee\x01\n\x11PagerdutyEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x31\n\x0brouting_key\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\rhttp_override\x18\x03 \x01(\x0b\x32\x1d.arista.alert.v1.HttpSettings\x12=\n\x11settings_override\x18\x04 \x01(\x0b\x32\".arista.alert.v1.PagerdutySettings\"\xee\x01\n\x11VictorOpsEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x31\n\x0brouting_key\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\rhttp_override\x18\x03 \x01(\x0b\x32\x1d.arista.alert.v1.HttpSettings\x12=\n\x11settings_override\x18\x04 \x01(\x0b\x32\".arista.alert.v1.VictoropsSettings\"\xbd\x01\n\x12GoogleChatEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x34\n\rhttp_override\x18\x02 \x01(\x0b\x32\x1d.arista.alert.v1.HttpSettings\x12>\n\x11settings_override\x18\x03 \x01(\x0b\x32#.arista.alert.v1.GoogleChatSettings\"\xb7\x01\n\x0fMsTeamsEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x34\n\rhttp_override\x18\x02 \x01(\x0b\x32\x1d.arista.alert.v1.HttpSettings\x12;\n\x11settings_override\x18\x03 \x01(\x0b\x32 .arista.alert.v1.MsTeamsSettings\"\xa5\x01\n\x10SendgridEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12(\n\x02to\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\rhttp_override\x18\x03 \x01(\x0b\x32\x1d.arista.alert.v1.HttpSettings\"\xa8\x01\n\x13\x43ueSendgridEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12(\n\x02to\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\rhttp_override\x18\x03 \x01(\x0b\x32\x1d.arista.alert.v1.HttpSettings\"\x7f\n\x0eSyslogEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12:\n\x11settings_override\x18\x02 \x01(\x0b\x32\x1f.arista.alert.v1.SyslogSettings\"\x85\x01\n\x11\x43ueSyslogEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12=\n\x11settings_override\x18\x02 \x01(\x0b\x32\".arista.alert.v1.CueSyslogSettings\"{\n\x0cSNMPEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x38\n\x11settings_override\x18\x02 \x01(\x0b\x32\x1d.arista.alert.v1.SNMPSettings\"\x81\x01\n\x0f\x43ueSNMPEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12;\n\x11settings_override\x18\x02 \x01(\x0b\x32 .arista.alert.v1.CueSNMPSettings\"\xb1\x01\n\x0cZoomEndpoint\x12\x31\n\rsend_resolved\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x34\n\rhttp_override\x18\x02 \x01(\x0b\x32\x1d.arista.alert.v1.HttpSettings\x12\x38\n\x11settings_override\x18\x03 \x01(\x0b\x32\x1d.arista.alert.v1.ZoomSettings\"I\n\x0bTemplateKey\x12\x34\n\rtemplate_type\x18\x01 \x01(\x0e\x32\x1d.arista.alert.v1.TemplateType:\x04\x80\x8e\x19\x01\"w\n\x0eTemplateConfig\x12)\n\x03key\x18\x01 \x01(\x0b\x32\x1c.arista.alert.v1.TemplateKey\x12.\n\x08template\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue:\n\xfa\x8d\x19\x02rw\x90\x8e\x19\x01\"\x86\x03\n\x0f\x44\x65\x66\x61ultTemplate\x12)\n\x03key\x18\x01 \x01(\x0b\x32\x1c.arista.alert.v1.TemplateKey\x12.\n\x08template\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\x0bmulti_alert\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x31\n\x0b\x64\x65scription\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12<\n\x16\x65xternal_documentation\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x36\n\routput_format\x18\x06 \x01(\x0e\x32\x1f.arista.alert.v1.TemplateOutput\x12\x32\n\x0c\x64isplay_name\x18\x07 \x01(\x0b\x32\x1c.google.protobuf.StringValue:\n\xfa\x8d\x19\x02ro\x90\x8e\x19\x01*\x99\x02\n\x0f\x43onfigErrorType\x12!\n\x1d\x43ONFIG_ERROR_TYPE_UNSPECIFIED\x10\x00\x12$\n CONFIG_ERROR_TYPE_INVALID_FORMAT\x10\x02\x12$\n CONFIG_ERROR_TYPE_INVALID_SYNTAX\x10\x03\x12&\n\"CONFIG_ERROR_TYPE_TEMPLATE_INVALID\x10\x04\x12#\n\x1f\x43ONFIG_ERROR_TYPE_ILLEGAL_VALUE\x10\x05\x12&\n\"CONFIG_ERROR_TYPE_MISSING_REQUIRED\x10\x06\x12\"\n\x1e\x43ONFIG_ERROR_TYPE_INVALID_TYPE\x10\x07*\xfd\x03\n\x11\x45ndpointErrorType\x12#\n\x1f\x45NDPOINT_ERROR_TYPE_UNSPECIFIED\x10\x00\x12\'\n#ENDPOINT_ERROR_TYPE_HTTP_POST_ERROR\x10\x01\x12*\n&ENDPOINT_ERROR_TYPE_JSON_MARSHAL_ERROR\x10\x02\x12,\n(ENDPOINT_ERROR_TYPE_INVALID_CONFIG_ERROR\x10\x03\x12&\n\"ENDPOINT_ERROR_TYPE_TEMPLATE_ERROR\x10\x04\x12*\n&ENDPOINT_ERROR_TYPE_BAD_RESPONSE_ERROR\x10\x05\x12\"\n\x1e\x45NDPOINT_ERROR_TYPE_SMTP_ERROR\x10\x06\x12(\n$ENDPOINT_ERROR_TYPE_CONNECTION_ERROR\x10\x07\x12%\n!ENDPOINT_ERROR_TYPE_TIMEOUT_ERROR\x10\x08\x12(\n$ENDPOINT_ERROR_TYPE_RATE_LIMIT_ERROR\x10\t\x12\'\n#ENDPOINT_ERROR_TYPE_ALERT_CAP_ERROR\x10\n\x12$\n ENDPOINT_ERROR_TYPE_O_AUTH_ERROR\x10\x0b*\x8d\x01\n\x16\x43ueSyslogMessageFormat\x12)\n%CUE_SYSLOG_MESSAGE_FORMAT_UNSPECIFIED\x10\x00\x12#\n\x1f\x43UE_SYSLOG_MESSAGE_FORMAT_PLAIN\x10\x01\x12#\n\x1f\x43UE_SYSLOG_MESSAGE_FORMAT_IDMEF\x10\x02*\xaa\x01\n\x11SNMPSecurityLevel\x12#\n\x1fSNMP_SECURITY_LEVEL_UNSPECIFIED\x10\x00\x12\'\n#SNMP_SECURITY_LEVEL_NO_AUTH_NO_PRIV\x10\x01\x12$\n SNMP_SECURITY_LEVEL_AUTH_NO_PRIV\x10\x02\x12!\n\x1dSNMP_SECURITY_LEVEL_AUTH_PRIV\x10\x03*\xee\x01\n\x10SNMPAuthProtocol\x12\"\n\x1eSNMP_AUTH_PROTOCOL_UNSPECIFIED\x10\x00\x12\x1a\n\x16SNMP_AUTH_PROTOCOL_MD5\x10\x01\x12\x1a\n\x16SNMP_AUTH_PROTOCOL_SHA\x10\x02\x12\x1e\n\x1aSNMP_AUTH_PROTOCOL_SHA_224\x10\x03\x12\x1e\n\x1aSNMP_AUTH_PROTOCOL_SHA_256\x10\x04\x12\x1e\n\x1aSNMP_AUTH_PROTOCOL_SHA_384\x10\x05\x12\x1e\n\x1aSNMP_AUTH_PROTOCOL_SHA_512\x10\x06*\xf0\x01\n\x10SNMPPrivProtocol\x12\"\n\x1eSNMP_PRIV_PROTOCOL_UNSPECIFIED\x10\x00\x12\x1a\n\x16SNMP_PRIV_PROTOCOL_DES\x10\x01\x12\x1a\n\x16SNMP_PRIV_PROTOCOL_AES\x10\x02\x12\x1e\n\x1aSNMP_PRIV_PROTOCOL_AES_192\x10\x03\x12\x1e\n\x1aSNMP_PRIV_PROTOCOL_AES_256\x10\x04\x12\x1f\n\x1bSNMP_PRIV_PROTOCOL_AES_192C\x10\x05\x12\x1f\n\x1bSNMP_PRIV_PROTOCOL_AES_256C\x10\x06*}\n\x13\x43ueSNMPAuthProtocol\x12&\n\"CUE_SNMP_AUTH_PROTOCOL_UNSPECIFIED\x10\x00\x12\x1e\n\x1a\x43UE_SNMP_AUTH_PROTOCOL_MD5\x10\x01\x12\x1e\n\x1a\x43UE_SNMP_AUTH_PROTOCOL_SHA\x10\x02*}\n\x13\x43ueSNMPPrivProtocol\x12&\n\"CUE_SNMP_PRIV_PROTOCOL_UNSPECIFIED\x10\x00\x12\x1e\n\x1a\x43UE_SNMP_PRIV_PROTOCOL_DES\x10\x01\x12\x1e\n\x1a\x43UE_SNMP_PRIV_PROTOCOL_AES\x10\x02*\xb9\x05\n\x0cTemplateType\x12\x1d\n\x19TEMPLATE_TYPE_UNSPECIFIED\x10\x00\x12\x1c\n\x18TEMPLATE_TYPE_EMAIL_HTML\x10\x01\x12\x1c\n\x18TEMPLATE_TYPE_EMAIL_TEXT\x10\x02\x12\x1f\n\x1bTEMPLATE_TYPE_SLACK_MESSAGE\x10\x03\x12\"\n\x1eTEMPLATE_TYPE_PUSHOVER_MESSAGE\x10\x04\x12#\n\x1fTEMPLATE_TYPE_PAGERDUTY_SUMMARY\x10\x05\x12(\n$TEMPLATE_TYPE_VICTOROPS_DISPLAY_NAME\x10\x06\x12)\n%TEMPLATE_TYPE_VICTOROPS_STATE_MESSAGE\x10\x07\x12%\n!TEMPLATE_TYPE_GOOGLE_CHAT_MESSAGE\x10\x08\x12)\n%TEMPLATE_TYPE_MICROSOFT_TEAMS_MESSAGE\x10\t\x12\x1f\n\x1bTEMPLATE_TYPE_EMAIL_SUBJECT\x10\n\x12 \n\x1cTEMPLATE_TYPE_SYSLOG_MESSAGE\x10\x0b\x12\"\n\x1eTEMPLATE_TYPE_OPSGENIE_MESSAGE\x10\x0c\x12\x1e\n\x1aTEMPLATE_TYPE_ZOOM_MESSAGE\x10\r\x12#\n\x1fTEMPLATE_TYPE_EMAIL_SINGLE_HTML\x10\x0e\x12#\n\x1fTEMPLATE_TYPE_EMAIL_SINGLE_TEXT\x10\x0f\x12&\n\"TEMPLATE_TYPE_EMAIL_SINGLE_SUBJECT\x10\x10\x12 \n\x1cTEMPLATE_TYPE_WEBHOOK_SINGLE\x10\x11\x12\"\n\x1eTEMPLATE_TYPE_WEBHOOK_MULTIPLE\x10\x12*\x7f\n\x0eTemplateOutput\x12\x1f\n\x1bTEMPLATE_OUTPUT_UNSPECIFIED\x10\x00\x12\x18\n\x14TEMPLATE_OUTPUT_TEXT\x10\x01\x12\x18\n\x14TEMPLATE_OUTPUT_JSON\x10\x02\x12\x18\n\x14TEMPLATE_OUTPUT_HTML\x10\x03\x42(Z&arista/resources/arista/alert.v1;alertb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'arista.alert.v1.alert_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z&arista/resources/arista/alert.v1;alert'
  _globals['_ALERTCONFIG']._options = None
  _globals['_ALERTCONFIG']._serialized_options = b'\220\216\031\001\242\216\031\002rw'
  _globals['_ALERT']._options = None
  _globals['_ALERT']._serialized_options = b'\220\216\031\001\242\216\031\002ro'
  _globals['_HTTPHEADERS_VALUESENTRY']._options = None
  _globals['_HTTPHEADERS_VALUESENTRY']._serialized_options = b'8\001'
  _globals['_CUEDATA_VALUESENTRY']._options = None
  _globals['_CUEDATA_VALUESENTRY']._serialized_options = b'8\001'
  _globals['_INHIBITIONSETTINGS_VALUESENTRY']._options = None
  _globals['_INHIBITIONSETTINGS_VALUESENTRY']._serialized_options = b'8\001'
  _globals['_BROADCASTGROUPS_VALUESENTRY']._options = None
  _globals['_BROADCASTGROUPS_VALUESENTRY']._serialized_options = b'8\001'
  _globals['_TEMPLATEKEY']._options = None
  _globals['_TEMPLATEKEY']._serialized_options = b'\200\216\031\001'
  _globals['_TEMPLATECONFIG']._options = None
  _globals['_TEMPLATECONFIG']._serialized_options = b'\372\215\031\002rw\220\216\031\001'
  _globals['_DEFAULTTEMPLATE']._options = None
  _globals['_DEFAULTTEMPLATE']._serialized_options = b'\372\215\031\002ro\220\216\031\001'
  _globals['_CONFIGERRORTYPE']._serialized_start=12678
  _globals['_CONFIGERRORTYPE']._serialized_end=12959
  _globals['_ENDPOINTERRORTYPE']._serialized_start=12962
  _globals['_ENDPOINTERRORTYPE']._serialized_end=13471
  _globals['_CUESYSLOGMESSAGEFORMAT']._serialized_start=13474
  _globals['_CUESYSLOGMESSAGEFORMAT']._serialized_end=13615
  _globals['_SNMPSECURITYLEVEL']._serialized_start=13618
  _globals['_SNMPSECURITYLEVEL']._serialized_end=13788
  _globals['_SNMPAUTHPROTOCOL']._serialized_start=13791
  _globals['_SNMPAUTHPROTOCOL']._serialized_end=14029
  _globals['_SNMPPRIVPROTOCOL']._serialized_start=14032
  _globals['_SNMPPRIVPROTOCOL']._serialized_end=14272
  _globals['_CUESNMPAUTHPROTOCOL']._serialized_start=14274
  _globals['_CUESNMPAUTHPROTOCOL']._serialized_end=14399
  _globals['_CUESNMPPRIVPROTOCOL']._serialized_start=14401
  _globals['_CUESNMPPRIVPROTOCOL']._serialized_end=14526
  _globals['_TEMPLATETYPE']._serialized_start=14529
  _globals['_TEMPLATETYPE']._serialized_end=15226
  _globals['_TEMPLATEOUTPUT']._serialized_start=15228
  _globals['_TEMPLATEOUTPUT']._serialized_end=15355
  _globals['_ALERTCONFIG']._serialized_start=156
  _globals['_ALERTCONFIG']._serialized_end=325
  _globals['_ALERT']._serialized_start=328
  _globals['_ALERT']._serialized_end=576
  _globals['_CONFIGERRORS']._serialized_start=578
  _globals['_CONFIGERRORS']._serialized_end=638
  _globals['_CONFIGERROR']._serialized_start=641
  _globals['_CONFIGERROR']._serialized_end=797
  _globals['_ENDPOINTERRORS']._serialized_start=799
  _globals['_ENDPOINTERRORS']._serialized_end=863
  _globals['_ENDPOINTERROR']._serialized_start=866
  _globals['_ENDPOINTERROR']._serialized_end=1146
  _globals['_SETTINGS']._serialized_start=1149
  _globals['_SETTINGS']._serialized_end=2124
  _globals['_EMAILSETTINGS']._serialized_start=2127
  _globals['_EMAILSETTINGS']._serialized_end=2501
  _globals['_AZUREOAUTH']._serialized_start=2504
  _globals['_AZUREOAUTH']._serialized_end=2715
  _globals['_HTTPSETTINGS']._serialized_start=2718
  _globals['_HTTPSETTINGS']._serialized_end=2931
  _globals['_HTTPHEADERS']._serialized_start=2934
  _globals['_HTTPHEADERS']._serialized_end=3083
  _globals['_HTTPHEADERS_VALUESENTRY']._serialized_start=3007
  _globals['_HTTPHEADERS_VALUESENTRY']._serialized_end=3083
  _globals['_HEADERVALUES']._serialized_start=3085
  _globals['_HEADERVALUES']._serialized_end=3115
  _globals['_SLACKSETTINGS']._serialized_start=3117
  _globals['_SLACKSETTINGS']._serialized_end=3175
  _globals['_VICTOROPSSETTINGS']._serialized_start=3177
  _globals['_VICTOROPSSETTINGS']._serialized_end=3282
  _globals['_PAGERDUTYSETTINGS']._serialized_start=3284
  _globals['_PAGERDUTYSETTINGS']._serialized_end=3346
  _globals['_OPSGENIESETTINGS']._serialized_start=3348
  _globals['_OPSGENIESETTINGS']._serialized_end=3452
  _globals['_GOOGLECHATSETTINGS']._serialized_start=3454
  _globals['_GOOGLECHATSETTINGS']._serialized_end=3517
  _globals['_MSTEAMSSETTINGS']._serialized_start=3519
  _globals['_MSTEAMSSETTINGS']._serialized_end=3579
  _globals['_SYSLOGSETTINGS']._serialized_start=3582
  _globals['_SYSLOGSETTINGS']._serialized_end=3924
  _globals['_PRIORITIES']._serialized_start=3927
  _globals['_PRIORITIES']._serialized_end=4116
  _globals['_CUEDATA']._serialized_start=4118
  _globals['_CUEDATA']._serialized_end=4228
  _globals['_CUEDATA_VALUESENTRY']._serialized_start=4183
  _globals['_CUEDATA_VALUESENTRY']._serialized_end=4228
  _globals['_CUESYSLOGSETTINGS']._serialized_start=4231
  _globals['_CUESYSLOGSETTINGS']._serialized_end=4547
  _globals['_SNMPSETTINGS']._serialized_start=4550
  _globals['_SNMPSETTINGS']._serialized_end=4838
  _globals['_SNMPAUTH']._serialized_start=4841
  _globals['_SNMPAUTH']._serialized_end=5260
  _globals['_CUESNMPAUTH']._serialized_start=5263
  _globals['_CUESNMPAUTH']._serialized_end=5691
  _globals['_CUESNMPSETTINGS']._serialized_start=5694
  _globals['_CUESNMPSETTINGS']._serialized_end=5979
  _globals['_SENDGRIDSETTINGS']._serialized_start=5981
  _globals['_SENDGRIDSETTINGS']._serialized_end=6090
  _globals['_CUESENDGRIDSETTINGS']._serialized_start=6092
  _globals['_CUESENDGRIDSETTINGS']._serialized_end=6204
  _globals['_ZOOMSETTINGS']._serialized_start=6206
  _globals['_ZOOMSETTINGS']._serialized_end=6321
  _globals['_INHIBITIONSETTINGS']._serialized_start=6324
  _globals['_INHIBITIONSETTINGS']._serialized_end=6484
  _globals['_INHIBITIONSETTINGS_VALUESENTRY']._serialized_start=6411
  _globals['_INHIBITIONSETTINGS_VALUESENTRY']._serialized_end=6484
  _globals['_EVENTLIST']._serialized_start=6486
  _globals['_EVENTLIST']._serialized_end=6539
  _globals['_RULES']._serialized_start=6541
  _globals['_RULES']._serialized_end=6587
  _globals['_RULE']._serialized_start=6590
  _globals['_RULE']._serialized_end=6794
  _globals['_MATCHES']._serialized_start=6797
  _globals['_MATCHES']._serialized_end=7066
  _globals['_BROADCASTGROUPS']._serialized_start=7069
  _globals['_BROADCASTGROUPS']._serialized_end=7228
  _globals['_BROADCASTGROUPS_VALUESENTRY']._serialized_start=7150
  _globals['_BROADCASTGROUPS_VALUESENTRY']._serialized_end=7228
  _globals['_BROADCASTGROUP']._serialized_start=7231
  _globals['_BROADCASTGROUP']._serialized_end=8087
  _globals['_EMAILENDPOINTS']._serialized_start=8089
  _globals['_EMAILENDPOINTS']._serialized_end=8153
  _globals['_WEBHOOKENDPOINTS']._serialized_start=8155
  _globals['_WEBHOOKENDPOINTS']._serialized_end=8223
  _globals['_SLACKENDPOINTS']._serialized_start=8225
  _globals['_SLACKENDPOINTS']._serialized_end=8289
  _globals['_OPSGENIEENDPOINTS']._serialized_start=8291
  _globals['_OPSGENIEENDPOINTS']._serialized_end=8361
  _globals['_PUSHOVERENDPOINTS']._serialized_start=8363
  _globals['_PUSHOVERENDPOINTS']._serialized_end=8433
  _globals['_PAGERDUTYENDPOINTS']._serialized_start=8435
  _globals['_PAGERDUTYENDPOINTS']._serialized_end=8507
  _globals['_VICTOROPSENDPOINTS']._serialized_start=8509
  _globals['_VICTOROPSENDPOINTS']._serialized_end=8581
  _globals['_GOOGLECHATENDPOINTS']._serialized_start=8583
  _globals['_GOOGLECHATENDPOINTS']._serialized_end=8657
  _globals['_MSTEAMSENDPOINTS']._serialized_start=8659
  _globals['_MSTEAMSENDPOINTS']._serialized_end=8727
  _globals['_SENDGRIDENDPOINTS']._serialized_start=8729
  _globals['_SENDGRIDENDPOINTS']._serialized_end=8799
  _globals['_CUESENDGRIDENDPOINTS']._serialized_start=8801
  _globals['_CUESENDGRIDENDPOINTS']._serialized_end=8877
  _globals['_SYSLOGENDPOINTS']._serialized_start=8879
  _globals['_SYSLOGENDPOINTS']._serialized_end=8945
  _globals['_CUESYSLOGENDPOINTS']._serialized_start=8947
  _globals['_CUESYSLOGENDPOINTS']._serialized_end=9019
  _globals['_SNMPENDPOINTS']._serialized_start=9021
  _globals['_SNMPENDPOINTS']._serialized_end=9083
  _globals['_CUESNMPENDPOINTS']._serialized_start=9085
  _globals['_CUESNMPENDPOINTS']._serialized_end=9153
  _globals['_ZOOMENDPOINTS']._serialized_start=9155
  _globals['_ZOOMENDPOINTS']._serialized_end=9217
  _globals['_EMAILENDPOINT']._serialized_start=9219
  _globals['_EMAILENDPOINT']._serialized_end=9327
  _globals['_WEBHOOKENDPOINT']._serialized_start=9330
  _globals['_WEBHOOKENDPOINT']._serialized_end=9596
  _globals['_SLACKENDPOINT']._serialized_start=9599
  _globals['_SLACKENDPOINT']._serialized_end=9778
  _globals['_OPSGENIEENDPOINT']._serialized_start=9781
  _globals['_OPSGENIEENDPOINT']._serialized_end=9966
  _globals['_PUSHOVERENDPOINT']._serialized_start=9969
  _globals['_PUSHOVERENDPOINT']._serialized_end=10185
  _globals['_PAGERDUTYENDPOINT']._serialized_start=10188
  _globals['_PAGERDUTYENDPOINT']._serialized_end=10426
  _globals['_VICTOROPSENDPOINT']._serialized_start=10429
  _globals['_VICTOROPSENDPOINT']._serialized_end=10667
  _globals['_GOOGLECHATENDPOINT']._serialized_start=10670
  _globals['_GOOGLECHATENDPOINT']._serialized_end=10859
  _globals['_MSTEAMSENDPOINT']._serialized_start=10862
  _globals['_MSTEAMSENDPOINT']._serialized_end=11045
  _globals['_SENDGRIDENDPOINT']._serialized_start=11048
  _globals['_SENDGRIDENDPOINT']._serialized_end=11213
  _globals['_CUESENDGRIDENDPOINT']._serialized_start=11216
  _globals['_CUESENDGRIDENDPOINT']._serialized_end=11384
  _globals['_SYSLOGENDPOINT']._serialized_start=11386
  _globals['_SYSLOGENDPOINT']._serialized_end=11513
  _globals['_CUESYSLOGENDPOINT']._serialized_start=11516
  _globals['_CUESYSLOGENDPOINT']._serialized_end=11649
  _globals['_SNMPENDPOINT']._serialized_start=11651
  _globals['_SNMPENDPOINT']._serialized_end=11774
  _globals['_CUESNMPENDPOINT']._serialized_start=11777
  _globals['_CUESNMPENDPOINT']._serialized_end=11906
  _globals['_ZOOMENDPOINT']._serialized_start=11909
  _globals['_ZOOMENDPOINT']._serialized_end=12086
  _globals['_TEMPLATEKEY']._serialized_start=12088
  _globals['_TEMPLATEKEY']._serialized_end=12161
  _globals['_TEMPLATECONFIG']._serialized_start=12163
  _globals['_TEMPLATECONFIG']._serialized_end=12282
  _globals['_DEFAULTTEMPLATE']._serialized_start=12285
  _globals['_DEFAULTTEMPLATE']._serialized_end=12675
# @@protoc_insertion_point(module_scope)
