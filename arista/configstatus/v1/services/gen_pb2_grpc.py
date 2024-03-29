# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from arista.configstatus.v1.services import gen_pb2 as arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2


class ConfigDiffServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetOne = channel.unary_unary(
                '/arista.configstatus.v1.ConfigDiffService/GetOne',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffResponse.FromString,
                )
        self.GetAll = channel.unary_stream(
                '/arista.configstatus.v1.ConfigDiffService/GetAll',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffStreamRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffStreamResponse.FromString,
                )
        self.Subscribe = channel.unary_stream(
                '/arista.configstatus.v1.ConfigDiffService/Subscribe',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffStreamRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffStreamResponse.FromString,
                )


class ConfigDiffServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetOne(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAll(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Subscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ConfigDiffServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetOne': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOne,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffResponse.SerializeToString,
            ),
            'GetAll': grpc.unary_stream_rpc_method_handler(
                    servicer.GetAll,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffStreamRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffStreamResponse.SerializeToString,
            ),
            'Subscribe': grpc.unary_stream_rpc_method_handler(
                    servicer.Subscribe,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffStreamRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffStreamResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'arista.configstatus.v1.ConfigDiffService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ConfigDiffService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetOne(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/arista.configstatus.v1.ConfigDiffService/GetOne',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetAll(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/arista.configstatus.v1.ConfigDiffService/GetAll',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffStreamRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Subscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/arista.configstatus.v1.ConfigDiffService/Subscribe',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffStreamRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigDiffStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class ConfigurationServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetOne = channel.unary_unary(
                '/arista.configstatus.v1.ConfigurationService/GetOne',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationResponse.FromString,
                )
        self.GetAll = channel.unary_stream(
                '/arista.configstatus.v1.ConfigurationService/GetAll',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationStreamRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationStreamResponse.FromString,
                )
        self.Subscribe = channel.unary_stream(
                '/arista.configstatus.v1.ConfigurationService/Subscribe',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationStreamRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationStreamResponse.FromString,
                )


class ConfigurationServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetOne(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAll(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Subscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ConfigurationServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetOne': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOne,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationResponse.SerializeToString,
            ),
            'GetAll': grpc.unary_stream_rpc_method_handler(
                    servicer.GetAll,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationStreamRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationStreamResponse.SerializeToString,
            ),
            'Subscribe': grpc.unary_stream_rpc_method_handler(
                    servicer.Subscribe,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationStreamRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationStreamResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'arista.configstatus.v1.ConfigurationService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ConfigurationService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetOne(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/arista.configstatus.v1.ConfigurationService/GetOne',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetAll(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/arista.configstatus.v1.ConfigurationService/GetAll',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationStreamRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Subscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/arista.configstatus.v1.ConfigurationService/Subscribe',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationStreamRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.ConfigurationStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class SecurityProfileServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetOne = channel.unary_unary(
                '/arista.configstatus.v1.SecurityProfileService/GetOne',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileResponse.FromString,
                )
        self.GetAll = channel.unary_stream(
                '/arista.configstatus.v1.SecurityProfileService/GetAll',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileStreamRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileStreamResponse.FromString,
                )
        self.Subscribe = channel.unary_stream(
                '/arista.configstatus.v1.SecurityProfileService/Subscribe',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileStreamRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileStreamResponse.FromString,
                )


class SecurityProfileServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetOne(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAll(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Subscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SecurityProfileServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetOne': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOne,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileResponse.SerializeToString,
            ),
            'GetAll': grpc.unary_stream_rpc_method_handler(
                    servicer.GetAll,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileStreamRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileStreamResponse.SerializeToString,
            ),
            'Subscribe': grpc.unary_stream_rpc_method_handler(
                    servicer.Subscribe,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileStreamRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileStreamResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'arista.configstatus.v1.SecurityProfileService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SecurityProfileService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetOne(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/arista.configstatus.v1.SecurityProfileService/GetOne',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetAll(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/arista.configstatus.v1.SecurityProfileService/GetAll',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileStreamRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Subscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/arista.configstatus.v1.SecurityProfileService/Subscribe',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileStreamRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class SecurityProfileDiffServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetOne = channel.unary_unary(
                '/arista.configstatus.v1.SecurityProfileDiffService/GetOne',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffResponse.FromString,
                )
        self.GetAll = channel.unary_stream(
                '/arista.configstatus.v1.SecurityProfileDiffService/GetAll',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffStreamRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffStreamResponse.FromString,
                )
        self.Subscribe = channel.unary_stream(
                '/arista.configstatus.v1.SecurityProfileDiffService/Subscribe',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffStreamRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffStreamResponse.FromString,
                )


class SecurityProfileDiffServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetOne(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAll(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Subscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SecurityProfileDiffServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetOne': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOne,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffResponse.SerializeToString,
            ),
            'GetAll': grpc.unary_stream_rpc_method_handler(
                    servicer.GetAll,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffStreamRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffStreamResponse.SerializeToString,
            ),
            'Subscribe': grpc.unary_stream_rpc_method_handler(
                    servicer.Subscribe,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffStreamRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffStreamResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'arista.configstatus.v1.SecurityProfileDiffService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SecurityProfileDiffService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetOne(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/arista.configstatus.v1.SecurityProfileDiffService/GetOne',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetAll(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/arista.configstatus.v1.SecurityProfileDiffService/GetAll',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffStreamRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Subscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/arista.configstatus.v1.SecurityProfileDiffService/Subscribe',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffStreamRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class SecurityProfileDiffSummaryServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetOne = channel.unary_unary(
                '/arista.configstatus.v1.SecurityProfileDiffSummaryService/GetOne',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryResponse.FromString,
                )
        self.GetAll = channel.unary_stream(
                '/arista.configstatus.v1.SecurityProfileDiffSummaryService/GetAll',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryStreamRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryStreamResponse.FromString,
                )
        self.Subscribe = channel.unary_stream(
                '/arista.configstatus.v1.SecurityProfileDiffSummaryService/Subscribe',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryStreamRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryStreamResponse.FromString,
                )


class SecurityProfileDiffSummaryServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetOne(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAll(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Subscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SecurityProfileDiffSummaryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetOne': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOne,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryResponse.SerializeToString,
            ),
            'GetAll': grpc.unary_stream_rpc_method_handler(
                    servicer.GetAll,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryStreamRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryStreamResponse.SerializeToString,
            ),
            'Subscribe': grpc.unary_stream_rpc_method_handler(
                    servicer.Subscribe,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryStreamRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryStreamResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'arista.configstatus.v1.SecurityProfileDiffSummaryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SecurityProfileDiffSummaryService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetOne(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/arista.configstatus.v1.SecurityProfileDiffSummaryService/GetOne',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetAll(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/arista.configstatus.v1.SecurityProfileDiffSummaryService/GetAll',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryStreamRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Subscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/arista.configstatus.v1.SecurityProfileDiffSummaryService/Subscribe',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryStreamRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SecurityProfileDiffSummaryStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class SummaryServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetOne = channel.unary_unary(
                '/arista.configstatus.v1.SummaryService/GetOne',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryResponse.FromString,
                )
        self.GetAll = channel.unary_stream(
                '/arista.configstatus.v1.SummaryService/GetAll',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryStreamRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryStreamResponse.FromString,
                )
        self.Subscribe = channel.unary_stream(
                '/arista.configstatus.v1.SummaryService/Subscribe',
                request_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryStreamRequest.SerializeToString,
                response_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryStreamResponse.FromString,
                )


class SummaryServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetOne(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAll(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Subscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SummaryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetOne': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOne,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryResponse.SerializeToString,
            ),
            'GetAll': grpc.unary_stream_rpc_method_handler(
                    servicer.GetAll,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryStreamRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryStreamResponse.SerializeToString,
            ),
            'Subscribe': grpc.unary_stream_rpc_method_handler(
                    servicer.Subscribe,
                    request_deserializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryStreamRequest.FromString,
                    response_serializer=arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryStreamResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'arista.configstatus.v1.SummaryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SummaryService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetOne(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/arista.configstatus.v1.SummaryService/GetOne',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetAll(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/arista.configstatus.v1.SummaryService/GetAll',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryStreamRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Subscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/arista.configstatus.v1.SummaryService/Subscribe',
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryStreamRequest.SerializeToString,
            arista_dot_configstatus_dot_v1_dot_services_dot_gen__pb2.SummaryStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
