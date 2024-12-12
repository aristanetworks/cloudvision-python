# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

PCOMP = python -m grpc_tools.protoc # ensure we're using python's version and not some sys
PB_DIR = cloudvision/Connector/protobuf
GEN_DIR = cloudvision/Connector/gen
PCOMP_FLAGS = -I=$(PB_DIR) --python_out=$(GEN_DIR) --mypy_out=$(GEN_DIR) --grpc_python_out=$(GEN_DIR)

.PHONY: clean lint dist dev-setup
# re-generate python protobuf files
proto:
	$(PCOMP) $(PCOMP_FLAGS) $(PB_DIR)/*.proto

# clean all stuff related to dist-ing these packages
clean:
	rm -r cloudvision.egg-info build dist

dist:
	python3 -m build

dev-setup:
	pip3 install .[dev]

lint:
	flake8 .
	mypy --exclude build --exclude .venv .
	./check_copyright.sh
