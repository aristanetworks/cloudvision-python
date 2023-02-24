# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Utility module."""


from typing import Any, Dict


def get_dict(whatever: Any, default: Dict[Any, Any] = {}) -> Dict[Any, Any]:
    """Get dictionary.

    :param whatever: Given object
    :param default: Given default object (default is empty dict)
    :return: A dictionary or the default value
    """

    if isinstance(whatever, dict):
        return whatever
    return default
