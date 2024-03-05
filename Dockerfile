# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

FROM python:3.11
LABEL maintainer="cvaas-dev@arista.com"

WORKDIR /
COPY ./requirements*.txt .

# Workaround for https://github.com/yaml/pyyaml/issues/724
RUN python -m pip install --no-cache-dir "cython<3.0.0"

# hadolint ignore=DL3059
RUN python -m pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
