# DreamHost Dynamic DNS Record Update

`dhdynupdate` is a Python utility for Linux.

Its purpose is to update DNS records with IP addresses for your local
machine for a domain hosted by DreamHost, using the DreamHost API.

It supports updating both IPv4 and IPv6 addresses.

# Configuration
Configuration goes in `dhdynupdate.conf`, and is in the [Python 'config' file format.](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure)

The default config has a couple of sections:

##`Global`
This section has global configuration options:

* Network interfaces to update the DNS records for
* [The DreamHost Web API URL](http://wiki.dreamhost.com/Application_programming_interface), and the logfile location.

##`DreamHost API Test Account`

* Uses The DreamHost test API key
* Only allows read-only operations
* It's a useful example to show the file format as well as a harmless test

##`your.domain.name`

* Insert `your.domain.name` for the name of your domain name.
* Also put in your DreamHost API key.

        [Global]
        # The DreamHost API URL; doubtful it'll change
        api_url = https://api.dreamhost.com/
        # External IPv4 and IPv6 interface to use
        # Separated as the subnet provided by my ISP is on a different interface
        # than the routing IP on my external interface.
        ipv6_if = eth0
        ipv4_if = eth1
        # Log file
        log_file = dhdynupdate.log

        [DreamHost API Test Account]
        api_key = 6SHU5P2HLDAYECUM

        [your.domain.name]
        api_key=6SHU5P2HLDAYECUM

# Generating a DreamHost API Key

If you don't already have an appropriate API key:

* [Generate a new API key:](https://panel.dreamhost.com/?tree=home.api)
    * Make sure that `dns-*` is checked
    * Make sure *everything else* is unchecked

# FreeBSD License
Copyright (c) 2016, Troy Telford
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be interpreted as representing official policies, either expressed or implied.
