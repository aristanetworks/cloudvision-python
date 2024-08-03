# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest
import re

from cloudvision.cvlib.iputils import (
    number_of_usable_addresses,
    first_usable_address,
    last_usable_address,
    get_number_subnets,
    get_subnet_by_index,
    get_ip_from_subnet,
    overlapping_networks_check,
)

from cloudvision.cvlib.exceptions import (
    IpSubnetIndexException,
    IpHostIndexException,
    IpNetworkOverlapException,
)

check_host_utils = [
    # name
    # ip_network
    # exp_num_hosts
    # exp_first_host
    # exp_last_host
    [
        'ipv4 host subnet case 1',
        '1.1.1.0/24',
        # expected outputs:
        254,
        '1.1.1.1',
        '1.1.1.254',
    ],
    [
        'ipv6 host subnet case 1',
        '1:1:1::0/64',
        # expected outputs:
        18446744073709551615,
        '1:1:1::1',
        '1:1:1:0:ffff:ffff:ffff:ffff',
    ],
    [
        'ipv4 host subnet case 2',
        '1.1.1.80/28',
        # expected outputs:
        14,
        '1.1.1.81',
        '1.1.1.94',
    ],
    [
        'ipv6 host subnet case 2',
        '1:1:1::50/124',
        # expected outputs:
        15,
        '1:1:1::51',
        '1:1:1::5f',
    ],
    [
        'ipv4 link subnet',
        '1.1.1.1/31',
        # expected outputs:
        2,
        '1.1.1.0',
        '1.1.1.1',
    ],
    [
        'ipv6 link subnet',
        '1:1:1::0/127',
        # expected outputs:
        2,
        '1:1:1::',
        '1:1:1::1',
    ],
    [
        'ipv4 host',
        '1.1.1.1/32',
        # expected outputs:
        1,
        '1.1.1.1',
        '1.1.1.1',
    ],
    [
        'ipv6 host',
        '1:1:1::0/128',
        # expected outputs:
        1,
        '1:1:1::',
        '1:1:1::',
    ],
]


@pytest.mark.parametrize('name, ip_network, exp_num_hosts, exp_first_host, '
                         + 'exp_last_host',
                         check_host_utils)
def test_host_utils(name, ip_network, exp_num_hosts, exp_first_host,
                    exp_last_host):
    nhosts = number_of_usable_addresses(ip_network)
    f_host = first_usable_address(ip_network)
    l_host = last_usable_address(ip_network)
    # print("\n", name, nhosts, f_host, l_host)
    # return
    assert nhosts == exp_num_hosts
    assert str(f_host) == exp_first_host
    assert str(l_host) == exp_last_host


check_subnet_utils = [
    # name
    # ip_network
    # subnet_mask
    # subnet_index
    # ip_address_index
    # exp_num_subnets
    # exp_subnet
    # exp_num_hosts
    # exp_ip_address
    # exp_error
    [
        'ipv4 first host from first subnet',
        '1.1.1.0/24',
        28,
        0,
        0,
        # expected outputs:
        16,
        '1.1.1.0/28',
        14,
        '1.1.1.1',
        None,
    ],
    [
        'ipv4 last host from first subnet',
        '1.1.1.0/24',
        28,
        0,
        13,
        # expected outputs:
        16,
        '1.1.1.0/28',
        14,
        '1.1.1.14',
        None,
    ],
    [
        'ipv6 first host from first subnet',
        '1:1:1::0/96',
        124,
        0,
        0,
        # expected outputs:
        268435456,
        '1:1:1::/124',
        15,
        '1:1:1::1',
        None,
    ],
    [
        'ipv6 last host from first subnet',
        '1:1:1::0/96',
        124,
        0,
        14,
        # expected outputs:
        268435456,
        '1:1:1::/124',
        15,
        '1:1:1::f',
        None,
    ],
    [
        'ipv4 middle host from middle subnet',
        '1.1.1.0/24',
        28,
        5,
        10,
        # expected outputs:
        16,
        '1.1.1.80/28',
        14,
        '1.1.1.91',
        None,
    ],
    [
        'ipv6 middle host from middle subnet',
        '1:1:1::0/96',
        124,
        5,
        10,
        # expected outputs:
        268435456,
        '1:1:1::50/124',
        15,
        '1:1:1::5b',
        None,
    ],
    [
        'ipv4 last host from last subnet',
        '1.1.1.0/24',
        28,
        15,
        13,
        # expected outputs:
        16,
        '1.1.1.240/28',
        14,
        '1.1.1.254',
        None,
    ],
    [
        'ipv6 last host from last subnet',
        '1:1:1::0/96',
        124,
        268435455,
        14,
        # expected outputs:
        268435456,
        '1:1:1::ffff:fff0/124',
        15,
        '1:1:1::ffff:ffff',
        None,
    ],
    [
        'ipv4 indexing one beyond last subnet',
        '1.1.1.0/24',
        28,
        16,
        12,
        # expected outputs:
        None,
        None,
        None,
        None,
        IpSubnetIndexException('1.1.1.0/24', 28, 16, 16, 'dev1'),
    ],
    [
        'ipv6 indexing one beyond last subnet',
        '1:1:1::0/96',
        124,
        268435456,
        14,
        # expected outputs:
        None,
        None,
        None,
        None,
        IpSubnetIndexException('1:1:1::0/96', 124, 268435456, 268435456, 'dev1'),
    ],
    [
        'ipv4 indexing one beyond last host in last subnet',
        '1.1.1.0/24',
        28,
        15,
        14,
        # expected outputs:
        None,
        None,
        None,
        None,
        IpHostIndexException('1.1.1.240/28', 14, 15, 'dev1'),
    ],
    [
        'ipv6 indexing one beyond last host in last subnet',
        '1:1:1::0/96',
        124,
        268435455,
        15,
        # expected outputs:
        None,
        None,
        None,
        None,
        IpHostIndexException('1:1:1::ffff:fff0/124', 15, 16, 'dev1'),
    ],
]


@pytest.mark.parametrize('name, ip_network, subnet_mask, subnet_index, '
                         + 'ip_index, exp_num_subnets, exp_subnet, '
                         + 'exp_num_hosts, exp_ip_address, exp_error',
                         check_subnet_utils)
def test_subnet_utils(name, ip_network, subnet_mask, subnet_index,
                      ip_index, exp_num_subnets, exp_subnet,
                      exp_num_hosts, exp_ip_address, exp_error):
    error = None
    try:
        nsubnets = get_number_subnets(ip_network, subnet_mask)
        subnet = get_subnet_by_index(
            ip_network, subnet_mask, subnet_index, 'dev1')
        nhosts = number_of_usable_addresses(subnet)
        ip_address = get_ip_from_subnet(subnet, ip_index, 'dev1')
    except Exception as e:
        error = e
    # print("\n", name, nsubnets, subnet, nhosts, ip_address)
    # return
    if error or exp_error:
        assert str(error) == str(exp_error)
    else:
        assert nsubnets == exp_num_subnets
        assert str(subnet) == exp_subnet
        assert nhosts == exp_num_hosts
        assert str(ip_address) == exp_ip_address


check_overlap_utils = [
    # name
    # list of networks
    # exp_error
    [
        'ipv4 non-overlapping networks',
        ['1.1.1.1/24', '1.1.2.0/24', '1.1.3.0/24'],
        None,
    ],
    [
        'ipv6 non-overlapping networks',
        ['1:1:1:1:1::1/124', '1:1:1:1:2::/124', '1:1:1:1:3::/124'],
        None,
    ],
    [
        'ipv4 overlapping networks',
        ['1.1.1.1/24', '1.1.2.0/24', '1.1.0.0/16'],
        IpNetworkOverlapException('1.1.1.0/24', '1.1.0.0/16'),
    ],
    [
        'ipv6 overlapping networks',
        ['1:1:1:1:1::1/124', '1:1:1:1:2::/124', '1:1:1:1::/64'],
        IpNetworkOverlapException('1:1:1:1:1::/124', '1:1:1:1::/64'),
    ],
]


@pytest.mark.parametrize('name, networks, exp_error',
                         check_overlap_utils)
def test_overlap_utils(name, networks, exp_error):
    error = None
    try:
        overlapping_networks_check(networks)
    except Exception as e:
        error = e
    if error or exp_error:
        assert str(error) == str(exp_error)
