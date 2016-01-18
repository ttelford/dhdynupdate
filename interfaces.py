#!/usr/bin/python3

# Copyright (c) 2016, Troy Telford
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied.

import ipaddress
import logging
import netifaces
import sys

"""
This module gets the current IPv4 and/or IPv6 addresses of the network
interfaces provided.

While we could get the full set of interface information using
netifaces, for this module, we are only interested in one IPv4 and one
IPv6 address, each having been provided by the configuration

See [netifaces documentation](https://pypi.python.org/pypi/netifaces)

netifaces provides a somewhat standardized method of getting interface
information, such as IP addresses.

Technically, interfaces can have multiple IP addresses, but multiple
addresses is not often the case with home users.
* This chooses the first address for the interface, which covers the use
  case of many users who only use one ip address per interface.

Also handles the case where an address family isn't used:
* Not everybody has IPv6.
* Maybe a user is behind a NAT on IPv4, and is only updating their IPv6
  address in DNS.
"""
class interfaces():

    def __init__(self,configured_interfaces):
        self.addresses = self.get_if_addresses(configured_interfaces)

    def get_if_addresses(self, interfaces):
        """Get IP addresses from configured interfaces"""

        addresses = []
        for addr_type in interfaces:
            address_retrieved = True
            # Netifaces has a lookup for address families. The index
            # number is os-dependent, so we look up the index using the
            # method provided by netifaces.
            if addr_type == "AF_INET6":
                address_family = netifaces.AF_INET6
            elif addr_type == "AF_INET":
                address_family = netifaces.AF_INET
            interface_addresses = netifaces.ifaddresses(interfaces[addr_type])
            try:
                if addr_type == "AF_INET6":
                    # I'm not counting on IPv6 to only have one address;
                    # mulitple is common as there's always link-local in
                    # addition to an internet-routable address.
                    # Make sure we don't get a link-local IPv6 Address.
                    # These are in the subnet fe80:://10
                    for address in interface_addresses[address_family]:
                        address_retrieved = True
                        if address["addr"].split(':')[0] != "fe80":
                            new_address = address["addr"]
                            break
                        # We haven't found a non-link-local IPv6 Address
                        address_retrieved = False
                else:
                    new_address = interface_addresses[address_family][0]["addr"]
            except ValueError as exception:
                logging.warning("Could not get %s address from interface %s." % (addr_type, interfaces[addr_type]))
                logging.warning("Exception: %s" % (exception))
                address_retrieved = False
            except KeyError as index:
                if str(index) == str(address_family):
                    logging.warning("No %s address is assigned to interface %s." % (addr_type, interfaces[addr_type]))
                else:
                    logging.error("Unknown KeyError %s in finding %s address" % (index, addr_type))
                address_retrieved = False
            if address_retrieved:
                new_address = ipaddress.ip_address(new_address)
                addresses.append(new_address)
                logging.info("The current %s Address on %s is: %s" % (addr_type, interfaces[addr_type], new_address))
        return addresses

# vim: ts=4 sw=4 et
