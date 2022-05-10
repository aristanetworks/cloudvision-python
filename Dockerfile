# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

FROM python:3.10
LABEL maintainer="cvaas-dev@arista.com"

RUN python -m pip install --no-cache-dir \
    msgpack==1.0.3 \
    protobuf==3.20.1 \
    numpy==1.22.3 \
    pyyaml==5.4.1 \
    pytest==7.1.2 \
    grpcio==1.46.0 \
    grpcio-tools==1.46.0 \
    flake8==3.8.4 \
    mypy==0.950
