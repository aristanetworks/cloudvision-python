# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from arista.endpointlocation.v1.services import gen_pb2 as arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2


class EndpointLocationServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetOne = channel.unary_unary(
                '/arista.endpointlocation.v1.EndpointLocationService/GetOne',
                request_serializer=arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationRequest.SerializeToString,
                response_deserializer=arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationResponse.FromString,
                )
        self.GetAll = channel.unary_stream(
                '/arista.endpointlocation.v1.EndpointLocationService/GetAll',
                request_serializer=arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationStreamRequest.SerializeToString,
                response_deserializer=arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationStreamResponse.FromString,
                )
        self.Subscribe = channel.unary_stream(
                '/arista.endpointlocation.v1.EndpointLocationService/Subscribe',
                request_serializer=arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationStreamRequest.SerializeToString,
                response_deserializer=arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationStreamResponse.FromString,
                )


class EndpointLocationServiceServicer(object):
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


def add_EndpointLocationServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetOne': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOne,
                    request_deserializer=arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationRequest.FromString,
                    response_serializer=arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationResponse.SerializeToString,
            ),
            'GetAll': grpc.unary_stream_rpc_method_handler(
                    servicer.GetAll,
                    request_deserializer=arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationStreamRequest.FromString,
                    response_serializer=arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationStreamResponse.SerializeToString,
            ),
            'Subscribe': grpc.unary_stream_rpc_method_handler(
                    servicer.Subscribe,
                    request_deserializer=arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationStreamRequest.FromString,
                    response_serializer=arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationStreamResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'arista.endpointlocation.v1.EndpointLocationService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class EndpointLocationService(object):
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
        return grpc.experimental.unary_unary(request, target, '/arista.endpointlocation.v1.EndpointLocationService/GetOne',
            arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationRequest.SerializeToString,
            arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationResponse.FromString,
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
        return grpc.experimental.unary_stream(request, target, '/arista.endpointlocation.v1.EndpointLocationService/GetAll',
            arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationStreamRequest.SerializeToString,
            arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationStreamResponse.FromString,
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
        return grpc.experimental.unary_stream(request, target, '/arista.endpointlocation.v1.EndpointLocationService/Subscribe',
            arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationStreamRequest.SerializeToString,
            arista_dot_endpointlocation_dot_v1_dot_services_dot_gen__pb2.EndpointLocationStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)