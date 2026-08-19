# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

PCOMP = python3 -m grpc_tools.protoc # ensure we're using python's version and not some sys
PROTO_DIRS = cloudvision/compliance cloudvision/Connector
BUILD_ARTIFACTS := cloudvision.egg-info build dist _build docsrc/arista*.rst \
	docsrc/cloudvision*.rst docsrc/fmp*.rst .pytest_cache

.PHONY: clean lint dist dev-setup docs
# re-generate python protobuf files
proto:
	@for dir in $(PROTO_DIRS); do \
		$(PCOMP) -I=$$dir/protobuf --python_out=$$dir/gen \
			--mypy_out=$$dir/gen --grpc_python_out=$$dir/gen \
			$$dir/protobuf/*.proto || exit; \
	done

# clean all stuff related to dist-ing these packages
clean:
	@for artifact in ${BUILD_ARTIFACTS} ; do \
		rm -r $$artifact && echo "$$artifact removed" ; \
	done || exit 0

dist: clean
	python3 -m build

dev-setup:
	pip3 install .[dev]

lint:
	flake8 .
	mypy --namespace-packages --exclude build --exclude .venv .
	./check_copyright.sh

docs:
	sphinx-apidoc -o docsrc arista
	sphinx-apidoc -o docsrc cloudvision
	sphinx-apidoc -o docsrc fmp
	sphinx-build docsrc _build
