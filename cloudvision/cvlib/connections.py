# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import collections
import grpc
from typing import Dict, Optional


class AuthAndEndpoints:
    '''
    Object to store auth and endpoint information for use in the context object
    - apiserverAddr:     Address of the CloudVision apiserver
    - serviceAddr:       Address of the CloudVision service proxy server, e.g. ambassador address
    - cacert:            Path to local CA Cert, used for establishing CV grpc connections
    - commandEndpoint:   Service endpoint where command requests are posted to
    - logEndpoint:       Service endpoint where log requests are posted to
    - connectionTimeout: Timeout value for connections to endpoints in seconds
    - cliTimeout:        Timeout value for cli commands invoked by connections
    - testAddresses:     Api addresses to use when execution is in a test context
    '''

    def __init__(self,
                 apiserverAddr: Optional[str] = None,
                 serviceAddr: Optional[str] = None,
                 serviceCACert: Optional[str] = None,
                 aerisCACert: Optional[str] = None,
                 commandEndpoint: Optional[str] = None,
                 logEndpoint: Optional[str] = None,
                 connectionTimeout: Optional[int] = 250,
                 cliTimeout: Optional[int] = 200,
                 testAddresses: Optional[Dict[str, str]] = None):
        self.apiserverAddr = apiserverAddr
        self.serviceAddr = serviceAddr
        self.serviceCACert = serviceCACert
        self.aerisCACert = aerisCACert
        self.commandEndpoint = commandEndpoint
        self.logEndpoint = logEndpoint
        self.connectionTimeout = connectionTimeout
        self.cliTimeout = cliTimeout
        self.testAddresses = testAddresses


# The following code is sourced from:
# https://github.com/grpc/grpc/blob/master/examples/python/interceptors/headers/generic_client_interceptor.py

# ------------------------------------------------------------------------
# Copyright 2017 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class _GenericClientInterceptor(grpc.UnaryUnaryClientInterceptor,
                                grpc.UnaryStreamClientInterceptor,
                                grpc.StreamUnaryClientInterceptor,
                                grpc.StreamStreamClientInterceptor):
    """Base class for interceptors that operate on all RPC types."""

    def __init__(self, interceptor_function):
        self._fn = interceptor_function

    def intercept_unary_unary(self, continuation, client_call_details, request):
        new_details, new_request_iterator, postprocess = self._fn(
            client_call_details, iter((request,)), False, False)
        response = continuation(new_details, next(new_request_iterator))
        return postprocess(response) if postprocess else response

    def intercept_unary_stream(self, continuation, client_call_details,
                               request):
        new_details, new_request_iterator, postprocess = self._fn(
            client_call_details, iter((request,)), False, True)
        response_it = continuation(new_details, next(new_request_iterator))
        return postprocess(response_it) if postprocess else response_it

    def intercept_stream_unary(self, continuation, client_call_details,
                               request_iterator):
        new_details, new_request_iterator, postprocess = self._fn(
            client_call_details, request_iterator, True, False)
        response = continuation(new_details, new_request_iterator)
        return postprocess(response) if postprocess else response

    def intercept_stream_stream(self, continuation, client_call_details,
                                request_iterator):
        new_details, new_request_iterator, postprocess = self._fn(
            client_call_details, request_iterator, True, True)
        response_it = continuation(new_details, new_request_iterator)
        return postprocess(response_it) if postprocess else response_it


def create(intercept_call):
    return _GenericClientInterceptor(intercept_call)

# ------------------------------------------------------------------------

# Code to add an interceptor that sets the header, based on example code from
# https://github.com/grpc/grpc/tree/master/examples/python/interceptors/headers


class _ClientCallDetails(
        collections.namedtuple(
            '_ClientCallDetails',
            ('method', 'timeout', 'metadata', 'credentials')),
        grpc.ClientCallDetails):
    pass


def addHeaderInterceptor(header, value):
    def intercept_call(client_call_details, request_iterator, request_streaming, response_streaming):
        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)
        metadata.append((
            header,
            value,
        ))
        client_call_details = _ClientCallDetails(
            client_call_details.method, client_call_details.timeout, metadata,
            client_call_details.credentials)
        return client_call_details, request_iterator, None

    return create(intercept_call)
