# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

FROM python:3.11
LABEL maintainer="cvaas-dev@arista.com"

# Workaround for https://github.com/yaml/pyyaml/issues/724
RUN python -m pip install --no-cache-dir "cython<3.0.0" && \
    pip install --no-cache-dir --no-build-isolation pyyaml==6.0.1

# hadolint ignore=DL3059
RUN python -m pip install --no-cache-dir \
    msgpack==1.0.3 \
    cryptography==42.0.4 \
    protobuf==4.22.5 \
    numpy==1.22.3 \
    pytest==7.1.2 \
    grpcio==1.53.0 \
    grpcio-tools==1.53.0 \
    flake8==3.8.4 \
    mypy==0.981
