#!/usr/bin/env python3

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

"""DreamHost DNS Accessor Object"""

import ipaddress
import logging
import os
import sys

import http_access
import interfaces

class dhdns():
    api_key = ""
    local_hostname = ""

    def __init__(self, api_key, api_url, local_hostname, configured_interfaces):
        """Initialize dnsupdate"""
        # Pull configuration from config_settings
        self.api_key = api_key
        self.local_hostname = local_hostname 
        self.interface = interfaces.interfaces(configured_interfaces)
        # Set up http_accessor object.
        try:
            self.dreamhost_accessor = http_access.http_access(api_url)
        except KeyError as error:
            logging.critical("Could not set up DreamHost API communications. Error:  %s" % (error))

    def update_if_necessary(self):
        # TODO We really only want to update_addresses() if one or more of our
        # IP addresses have changed.
        self.update_addresses()
        logging.info(self.interface.addresses)

    def get_dh_dns_records(self):
        """Get the current DreamHost DNS records"""
        # Start by setting up a bit of data for the requests library.
        request_params = {"key":self.api_key, "cmd":"dns-list_records", "format":"json"}
        dns_records = self.dreamhost_accessor.request_get(request_params)
        dns_records = dns_records["data"]

        # Get the current DNS records for our configured hostname
        target_records=[]
        for entry in dns_records:
            # Only operate on editable entries...
            if entry["editable"] == "1":
                if "record" in entry:
                    # Verify if our entry has the hostname we're looking for.
                    # Multiple entries may, if we're using native dual-stack IPv4 &
                    # IPv6.
                    if entry["record"] == self.local_hostname:
                        target_records.append(entry)
            else: # read-only entry
                logging.debug("Non-editable value:  %s" % entry)
                if "record" in entry:
                    if entry["record"] == self.local_hostname:
                        # prevent a read-only record from being "added"
                        dh_addr = ipaddress.ip_address(entry["value"])
                        readonly_index = []
                        for addr in self.interface.addresses:
                            if addr.version == dh_addr.version:
                                logging.info("Not operating on %s, as it's read-only" % (entry["record"]))
                                readonly_index.append(self.interface.addresses.index(addr))
                        for index in readonly_index:
                            del self.interface.addresses[index]
        return target_records

    def remove_old_records(self, entry, matching_index):
        """Determine if the IP address at DreamHost is out of date vs the ip
        addresses determined by get_if_address(). If a local IP address isn't
        found for an interface, than the corresponding entry in DNS will be
        removed"""
        dh_addr = ipaddress.ip_address(entry["value"])
        for addr in self.interface.addresses:
            logging.debug(entry)
            logging.debug("dh_addr: %s - %s" % (dh_addr, dh_addr.version))
            logging.debug("addr: %s - %s" % (addr, addr.version))
            if addr.version == dh_addr.version:
                if addr == dh_addr:
                    logging.debug("match")
                    logging.info("DreamHost DNS entry matches our address:  %s"
                                 % (addr))
                    matching_index.append(self.interface.addresses.index(addr))
                else:
                    logging.debug("no match")
                    logging.info("DreamHost DNS entry %s does not match our address:  %s"
                                 % (dh_addr, addr))
                    self.remove_record(entry)
            else:
                logging.debug("addr_versions do not match")
        return matching_index

    def update_addresses(self):
        """Check if an address needs to be updated, and builds a list of
           entries to send off to DreamHost"""
        # matching_address_index is to store addresses which "match" on both sides
        # -- and don't need updating.
        matching_address_index= []
        # Remove editable entries that don't exist/are changing
        # They will be re-added (with new values) in a moment.
        for entry in self.get_dh_dns_records():
            matching_address_index = self.remove_old_records(entry, matching_address_index)
        # Remove addresses which do not need updating; reverse order or else
        # the indexes will be wrongthe next time around.
        for index in sorted(matching_address_index, reverse=True):
            del self.interface.addresses[index]

        # Add IP addresses detected from interfaces.
        # NOTE:  we can't do much about readonly entries that aren't listed
        # when we query DreamHost for DNS records. This means the shipping
        # configuration file will fail if you have an IPv6 address.
        for address in self.interface.addresses:
            self.add_record(address)

    def remove_record(self, entry):
        # We update the record by removing the old record, and adding a new one.
        # DreamHost only allows `record`, `type`. and `value` for DNS
        # record deletion; so we will create a new dict with those values.
        # Start with things from entry
        request_params={key: entry[key] for key in ("record", "type", "value")}
        # Add things we need - api.key, cmd, format...
        request_params["key"] = self.api_key
        request_params["cmd"] = "dns-remove_record"
        request_params["format"] = "json"
        logging.info("Removing DNS entry with parameters: %s" %(request_params))
        output = self.dreamhost_accessor.request_get(request_params)
        if output["result"] != "success":
            logging.error("Could not remove entry for address %s" % (request_params["value"]))

    def add_record(self, address):
        # Create the requst parameters to add for the entry & record type
        # Add has four fields:  record, type, value comment
        request_params={}
        request_params["key"] = self.api_key
        request_params["cmd"] = "dns-add_record"
        request_params["record"] = self.local_hostname
        request_params["comment"] = "Automated DNS update by dhdynupdate"
        request_params["format"] = "json"
        request_params["value"] = address.compressed
        if address.version == 4:
            request_params["type"] = "A"
        elif address.version == 6:
            request_params["type"] = "AAAA"
        else:
            logging.critical("Invalid address type %s ! Exiting!" % (address))
            sys.exit()
        logging.info("Adding DNS entry with parameters: %s" %(request_params))
        output = self.dreamhost_accessor.request_get(request_params)
        if output["result"] != "success":
            logging.error("Could not update entry for address %s" % (address))
# vim: ts=4 sw=4 et
