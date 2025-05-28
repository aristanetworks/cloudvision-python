# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest
import re

from cloudvision.cvlib.device import (
    device_capabilities,
)

testPlatformMatchCases = [
    # test name
    # model_name
    # expected regexes
    # expected error
    [
        'trident fixed variant',
        'DCS-7050SX3-48YC8',
        device_capabilities['trident3x5|7-fixed'].get('regexes'),
        None
    ],
    [
        'trident fixed variant',
        'DCS-7050SX3-24YC4C',
        device_capabilities['trident3x5|7-fixed'].get('regexes'),
        None
    ],
    [
        'jericho fixed variant',
        'DCS-7020SR-24C2',
        device_capabilities['jericho-fixed'].get('regexes'),
        None
    ],
    [
        'generic capabilities',
        'DCS-7388-16CD',
        device_capabilities['default'].get('regexes'),
        None
    ],
    [
        'generic capabilities',
        'DCS-7300X-32Q-LC',
        device_capabilities['default'].get('regexes'),
        None
    ],
    [
        'unspecified platform',
        '',
        device_capabilities['default'].get('regexes'),
        None
    ],
    [
        'trident fixed variant',
        'DCS-7050TX-96-F',
        device_capabilities['trident2-fixed'].get('regexes'),
        None
    ],
    [
        'jericho fixed variant',
        'DCS-7280SR2K-48C6-M-F',
        device_capabilities['jericho-fixed'].get('regexes'),
        None
    ],
    [
        'jericho2 fixed variant',
        'DCS-7280SR3-40YC6',
        device_capabilities['jericho2-fixed'].get('regexes'),
        None
    ],
    [
        'jericho2 chassis variant',
        'DCS-7808',
        device_capabilities['jericho2-chassis'].get('regexes'),
        None
    ],
    [
        'trident fixed variant',
        'CCS-720XP-48ZC2',
        device_capabilities['trident3x3-fixed-poe'].get('regexes'),
        None
    ],
    [
        'trident fixed variant',
        'CCS-710P-16',
        device_capabilities['trident3x1-fixed-poe'].get('regexes'),
        None
    ],
    [
        'trident fixed variant',
        'CCS-720DP-24S',
        device_capabilities['trident3x1-fixed-poe'].get('regexes'),
        None
    ],
    [
        'trident3 chassis variant',
        'CCS-755',
        device_capabilities['trident3x4-chassis'].get('regexes'),
        None
    ],
    [
        'trident4 chassis variant',
        'DCS-7358X4-BND-F',
        device_capabilities['trident4-chassis'].get('regexes'),
        None
    ],
]


@pytest.mark.parametrize('name, modelName, expRegexes, expError',
                         testPlatformMatchCases)
def test_getPlatformSettings(name, modelName, expRegexes, expError):
    error = None
    matching_settings = None
    try:
        for platform, settings in device_capabilities.items():
            if platform == "default":
                continue
            for regex in settings['regexes']:
                if re.search(regex, modelName, re.IGNORECASE):
                    matching_settings = settings
        if matching_settings is None:
            matching_settings = device_capabilities['default']
    except Exception as e:
        error = e
    if error or expError:
        assert str(error) == str(expError)
    else:
        assert matching_settings.get('regexes') == expRegexes
