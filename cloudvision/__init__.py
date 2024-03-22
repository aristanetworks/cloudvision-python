# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import importlib.metadata

__path__ = __import__('pkgutil').extend_path(__path__, __name__)  # type: ignore  # mypy issue #1422

__version__ = importlib.metadata.version("cloudvision")
