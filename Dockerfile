# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

FROM python:3.8
LABEL maintainer="Arista Networks support@arista.com"

RUN python -m pip install msgpack==0.6.2 protobuf==3.13.0 \
    numpy==1.17.4 pyyaml==5.3.1 pytest==4.6.9 \
    grpcio==1.33.2 grpcio-tools==1.33.2 flake8==3.8.3 mypy==0.782
