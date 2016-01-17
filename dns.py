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

import json
import datetime
import os
import netifaces
from http_access import http_access

def main():
    #-----Cheat until I have config file-----
    # DreamHost API key
    # Dreamhost "test" API key
    api_key='6SHU5P2HLDAYECUM'
    # DreamHost-controlled domain name 
    domain_name = 'sub.domain.com'
    # External IPv4 interface to use
    ipv4_if = 'eth1'
    # External IPv6 interface to use
    ipv6_if = 'eth0'
    # The DreamHost API URL; doubtful it'll change
    api_url = 'https://api.dreamhost.com/'
    #-----End of cheat-----
    
    # What time is now?
    current_date = datetime.datetime.now()

    # Set up http_accessor object
    dreamhost_accessor = http_access(api_url)
   
    # Use netifaces to provide a somewhat standardized method of getting
    # interface information, such as IP addresses.
    # This chooses the first address for the interface.
    # See [netifaces documentation](https://pypi.python.org/pypi/netifaces)
    # Technically, interfaces can have multiple IP addresses, but that's not
    # often the case with home users. Definitely not for me.
    current_ipv4 = netifaces.ifaddresses(ipv4_if)[2][0]['addr']
    current_ipv6 = netifaces.ifaddresses(ipv6_if)[10][0]['addr']

    print(current_ipv4)
    print(current_ipv6)

    # Query for the current DNS records
    # Start by setting up a bit of data for the requests library.
    dns_query = {'key':api_key, 'cmd':'dns-list_records', 'format':'json'}

    # Run the query
    DNS_RECORDS=dreamhost_accessor.request_get(dns_query)
    print(DNS_RECORDS.json())

if __name__ == '__main__':  main()


# vim: ts=4 sw=4 et
