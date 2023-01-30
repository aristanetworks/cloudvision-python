# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: arista/identityprovider.v1/identityprovider.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from fmp import extensions_pb2 as fmp_dot_extensions__pb2
from fmp import wrappers_pb2 as fmp_dot_wrappers__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='arista/identityprovider.v1/identityprovider.proto',
  package='arista.identityprovider.v1',
  syntax='proto3',
  serialized_options=b'Z<arista/resources/arista/identityprovider.v1;identityprovider',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n1arista/identityprovider.v1/identityprovider.proto\x12\x1a\x61rista.identityprovider.v1\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x14\x66mp/extensions.proto\x1a\x12\x66mp/wrappers.proto\"C\n\x08OAuthKey\x12\x31\n\x0bprovider_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue:\x04\x80\x8e\x19\x01\"\xe2\x03\n\x0bOAuthConfig\x12\x31\n\x03key\x18\x01 \x01(\x0b\x32$.arista.identityprovider.v1.OAuthKey\x12.\n\x08\x65ndpoint\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\tclient_id\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x33\n\rclient_secret\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\'\n\nalgorithms\x18\x05 \x01(\x0b\x32\x13.fmp.RepeatedString\x12;\n\x17link_to_shared_provider\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12.\n\x08jwks_uri\x18\x07 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x17permitted_email_domains\x18\x08 \x01(\x0b\x32\x13.fmp.RepeatedString\x12\x36\n\x10roles_scope_name\x18\t \x01(\x0b\x32\x1c.google.protobuf.StringValue:\x06\xfa\x8d\x19\x02rw\"B\n\x07SAMLKey\x12\x31\n\x0bprovider_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue:\x04\x80\x8e\x19\x01\"\xd5\x03\n\nSAMLConfig\x12\x30\n\x03key\x18\x01 \x01(\x0b\x32#.arista.identityprovider.v1.SAMLKey\x12\x30\n\nidp_issuer\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x36\n\x10idp_metadata_url\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x44\n\x0f\x61uthreq_binding\x18\x04 \x01(\x0e\x32+.arista.identityprovider.v1.ProtocolBinding\x12\x34\n\x0e\x65mail_attrname\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12;\n\x17link_to_shared_provider\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x34\n\x17permitted_email_domains\x18\x07 \x01(\x0b\x32\x13.fmp.RepeatedString\x12\x34\n\x10\x66orce_saml_authn\x18\x08 \x01(\x0b\x32\x1a.google.protobuf.BoolValue:\x06\xfa\x8d\x19\x02rw*w\n\x0fProtocolBinding\x12 \n\x1cPROTOCOL_BINDING_UNSPECIFIED\x10\x00\x12\x1e\n\x1aPROTOCOL_BINDING_HTTP_POST\x10\x01\x12\"\n\x1ePROTOCOL_BINDING_HTTP_REDIRECT\x10\x02\x42>Z<arista/resources/arista/identityprovider.v1;identityproviderb\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_wrappers__pb2.DESCRIPTOR,fmp_dot_extensions__pb2.DESCRIPTOR,fmp_dot_wrappers__pb2.DESCRIPTOR,])

_PROTOCOLBINDING = _descriptor.EnumDescriptor(
  name='ProtocolBinding',
  full_name='arista.identityprovider.v1.ProtocolBinding',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='PROTOCOL_BINDING_UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='PROTOCOL_BINDING_HTTP_POST', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='PROTOCOL_BINDING_HTTP_REDIRECT', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1249,
  serialized_end=1368,
)
_sym_db.RegisterEnumDescriptor(_PROTOCOLBINDING)

ProtocolBinding = enum_type_wrapper.EnumTypeWrapper(_PROTOCOLBINDING)
PROTOCOL_BINDING_UNSPECIFIED = 0
PROTOCOL_BINDING_HTTP_POST = 1
PROTOCOL_BINDING_HTTP_REDIRECT = 2



_OAUTHKEY = _descriptor.Descriptor(
  name='OAuthKey',
  full_name='arista.identityprovider.v1.OAuthKey',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='provider_id', full_name='arista.identityprovider.v1.OAuthKey.provider_id', index=0,
      number=1, type=11, cpp_type=10, label=1,
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
  serialized_start=155,
  serialized_end=222,
)


_OAUTHCONFIG = _descriptor.Descriptor(
  name='OAuthConfig',
  full_name='arista.identityprovider.v1.OAuthConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='arista.identityprovider.v1.OAuthConfig.key', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='endpoint', full_name='arista.identityprovider.v1.OAuthConfig.endpoint', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='client_id', full_name='arista.identityprovider.v1.OAuthConfig.client_id', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='client_secret', full_name='arista.identityprovider.v1.OAuthConfig.client_secret', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='algorithms', full_name='arista.identityprovider.v1.OAuthConfig.algorithms', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='link_to_shared_provider', full_name='arista.identityprovider.v1.OAuthConfig.link_to_shared_provider', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='jwks_uri', full_name='arista.identityprovider.v1.OAuthConfig.jwks_uri', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='permitted_email_domains', full_name='arista.identityprovider.v1.OAuthConfig.permitted_email_domains', index=7,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='roles_scope_name', full_name='arista.identityprovider.v1.OAuthConfig.roles_scope_name', index=8,
      number=9, type=11, cpp_type=10, label=1,
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
  serialized_options=b'\372\215\031\002rw',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=225,
  serialized_end=707,
)


_SAMLKEY = _descriptor.Descriptor(
  name='SAMLKey',
  full_name='arista.identityprovider.v1.SAMLKey',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='provider_id', full_name='arista.identityprovider.v1.SAMLKey.provider_id', index=0,
      number=1, type=11, cpp_type=10, label=1,
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
  serialized_start=709,
  serialized_end=775,
)


_SAMLCONFIG = _descriptor.Descriptor(
  name='SAMLConfig',
  full_name='arista.identityprovider.v1.SAMLConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='arista.identityprovider.v1.SAMLConfig.key', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='idp_issuer', full_name='arista.identityprovider.v1.SAMLConfig.idp_issuer', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='idp_metadata_url', full_name='arista.identityprovider.v1.SAMLConfig.idp_metadata_url', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='authreq_binding', full_name='arista.identityprovider.v1.SAMLConfig.authreq_binding', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='email_attrname', full_name='arista.identityprovider.v1.SAMLConfig.email_attrname', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='link_to_shared_provider', full_name='arista.identityprovider.v1.SAMLConfig.link_to_shared_provider', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='permitted_email_domains', full_name='arista.identityprovider.v1.SAMLConfig.permitted_email_domains', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='force_saml_authn', full_name='arista.identityprovider.v1.SAMLConfig.force_saml_authn', index=7,
      number=8, type=11, cpp_type=10, label=1,
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
  serialized_options=b'\372\215\031\002rw',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=778,
  serialized_end=1247,
)

_OAUTHKEY.fields_by_name['provider_id'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_OAUTHCONFIG.fields_by_name['key'].message_type = _OAUTHKEY
_OAUTHCONFIG.fields_by_name['endpoint'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_OAUTHCONFIG.fields_by_name['client_id'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_OAUTHCONFIG.fields_by_name['client_secret'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_OAUTHCONFIG.fields_by_name['algorithms'].message_type = fmp_dot_wrappers__pb2._REPEATEDSTRING
_OAUTHCONFIG.fields_by_name['link_to_shared_provider'].message_type = google_dot_protobuf_dot_wrappers__pb2._BOOLVALUE
_OAUTHCONFIG.fields_by_name['jwks_uri'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_OAUTHCONFIG.fields_by_name['permitted_email_domains'].message_type = fmp_dot_wrappers__pb2._REPEATEDSTRING
_OAUTHCONFIG.fields_by_name['roles_scope_name'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_SAMLKEY.fields_by_name['provider_id'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_SAMLCONFIG.fields_by_name['key'].message_type = _SAMLKEY
_SAMLCONFIG.fields_by_name['idp_issuer'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_SAMLCONFIG.fields_by_name['idp_metadata_url'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_SAMLCONFIG.fields_by_name['authreq_binding'].enum_type = _PROTOCOLBINDING
_SAMLCONFIG.fields_by_name['email_attrname'].message_type = google_dot_protobuf_dot_wrappers__pb2._STRINGVALUE
_SAMLCONFIG.fields_by_name['link_to_shared_provider'].message_type = google_dot_protobuf_dot_wrappers__pb2._BOOLVALUE
_SAMLCONFIG.fields_by_name['permitted_email_domains'].message_type = fmp_dot_wrappers__pb2._REPEATEDSTRING
_SAMLCONFIG.fields_by_name['force_saml_authn'].message_type = google_dot_protobuf_dot_wrappers__pb2._BOOLVALUE
DESCRIPTOR.message_types_by_name['OAuthKey'] = _OAUTHKEY
DESCRIPTOR.message_types_by_name['OAuthConfig'] = _OAUTHCONFIG
DESCRIPTOR.message_types_by_name['SAMLKey'] = _SAMLKEY
DESCRIPTOR.message_types_by_name['SAMLConfig'] = _SAMLCONFIG
DESCRIPTOR.enum_types_by_name['ProtocolBinding'] = _PROTOCOLBINDING
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

OAuthKey = _reflection.GeneratedProtocolMessageType('OAuthKey', (_message.Message,), {
  'DESCRIPTOR' : _OAUTHKEY,
  '__module__' : 'arista.identityprovider.v1.identityprovider_pb2'
  # @@protoc_insertion_point(class_scope:arista.identityprovider.v1.OAuthKey)
  })
_sym_db.RegisterMessage(OAuthKey)

OAuthConfig = _reflection.GeneratedProtocolMessageType('OAuthConfig', (_message.Message,), {
  'DESCRIPTOR' : _OAUTHCONFIG,
  '__module__' : 'arista.identityprovider.v1.identityprovider_pb2'
  # @@protoc_insertion_point(class_scope:arista.identityprovider.v1.OAuthConfig)
  })
_sym_db.RegisterMessage(OAuthConfig)

SAMLKey = _reflection.GeneratedProtocolMessageType('SAMLKey', (_message.Message,), {
  'DESCRIPTOR' : _SAMLKEY,
  '__module__' : 'arista.identityprovider.v1.identityprovider_pb2'
  # @@protoc_insertion_point(class_scope:arista.identityprovider.v1.SAMLKey)
  })
_sym_db.RegisterMessage(SAMLKey)

SAMLConfig = _reflection.GeneratedProtocolMessageType('SAMLConfig', (_message.Message,), {
  'DESCRIPTOR' : _SAMLCONFIG,
  '__module__' : 'arista.identityprovider.v1.identityprovider_pb2'
  # @@protoc_insertion_point(class_scope:arista.identityprovider.v1.SAMLConfig)
  })
_sym_db.RegisterMessage(SAMLConfig)


DESCRIPTOR._options = None
_OAUTHKEY._options = None
_OAUTHCONFIG._options = None
_SAMLKEY._options = None
_SAMLCONFIG._options = None
# @@protoc_insertion_point(module_scope)
