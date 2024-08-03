# Copyright (c) 2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
#
# The purpose of this file is to provide ip utilities that are
# safe for both ipv4 and ipv6
# DO NOT use network.subnets() due to performance impact.
# DO NOT use network.hosts() due to performance impact.

import ipaddress
import json
from typing import List

from .exceptions import (
    IpSubnetIndexException,
    IpHostIndexException,
    IpNetworkOverlapException,
)


def is_ipv4(ip):
    # Determine if the given network is IPv4
    try:
        ipaddress.IPv4Network(ip, strict=False)
        return True
    except ValueError:
        return False


def is_ipv6(ip):
    # Determine if the given network is IPv6
    try:
        ipaddress.IPv6Network(ip, strict=False)
        return True
    except ValueError:
        return False


def number_of_usable_addresses(network):
    net = ipaddress.ip_network(network, strict=False)
    if net.version == 4 and net.num_addresses > 2:
        # exclude addresses for identification (first)
        # and broadcast (last)
        return net.num_addresses - 2
    elif net.version == 6 and net.num_addresses > 2:
        # exclude anycast (first) address
        return net.num_addresses - 1
    else:
        # for a p2p-link network use all 2 addresses
        return net.num_addresses


def first_usable_address(network):
    net = ipaddress.ip_network(network, strict=False)
    if net.num_addresses < 3:
        return net[0]
    return str(net[1])


def last_usable_address(network):
    net = ipaddress.ip_network(network, strict=False)
    if net.num_addresses < 3:
        return net[-1]
    return str(net[-2]) if net.version == 4 else str(net[-1])


def get_number_subnets(network, subnet_mask: int):
    # Calculate the total number of subnets of the given mask
    # on the given network
    network = ipaddress.ip_network(network, strict=False)
    bit_difference = subnet_mask - network.prefixlen
    total_subnets = 2 ** bit_difference
    return total_subnets


def get_subnet_by_index(network, subnet_mask: int, index: int,
                        hostname: str = None, poolname: str = None):
    # Return the subnet at the specified index.
    # Input index is 0 based.
    total_subnets = get_number_subnets(network, subnet_mask)
    # Ensure the index is within the valid range
    if index < 0 or index >= total_subnets:
        raise IpSubnetIndexException(
            network, subnet_mask, total_subnets, index,
            hostname, poolname)
    # Calculate the offset for the subnet at the given index
    if is_ipv6(network):
        bit_length = 128
    else:
        bit_length = 32
    network = ipaddress.ip_network(network, strict=False)
    offset = index * (1 << (bit_length - subnet_mask))
    new_subnet_address = int(network.network_address) + offset
    subnet = ipaddress.ip_network(
        f"{ipaddress.ip_address(new_subnet_address)}/{subnet_mask}",
        strict=False)
    return subnet


def get_ip_from_subnet(network, index: int, hostname: str = None,
                       poolname: str = None):
    # Return the ip address at the specified index.
    # Input index is 0 based.
    num_addresses = number_of_usable_addresses(network)
    if (network.version == 4 and network.prefixlen < 31) or (
       network.version == 6 and network.prefixlen < 127):
        # When indexing directly into non p2p-link networks,
        # skip identification/anycast address
        index += 1
    if index > num_addresses:
        raise IpHostIndexException(
            network, num_addresses, index, hostname, poolname)
    return network[index]


def overlapping_networks_check(networks: List[str], hostname: str = None,
                               poolname: str = None):
    # Given a list of networks ensures they do not overlap
    for idx1 in range(len(networks)):
        if networks[idx1].strip() == "":
            continue
        network1 = ipaddress.ip_network(networks[idx1], strict=False)
        idx2 = idx1 + 1
        while idx2 < len(networks):
            network2 = ipaddress.ip_network(networks[idx2], strict=False)
            if network1.overlaps(network2):
                raise IpNetworkOverlapException(
                    network1, network2, hostname, poolname)
            idx2 += 1
