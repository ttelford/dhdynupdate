# DreamHost Dynamic DNS Record Update

`dhdynupdate` is a Python 3 utility for Linux. Other operating systems may
work, but have not been tested.

The purpose of `dhdynupdate` is similar to a number of dynamic DNS updaters on
the internet: to update DNS records with IP addresses for your local machine
for a domain hosted by [DreamHost](https://www.dreamhost.com), using the
[DreamHost API](http://wiki.dreamhost.com/Application_programming_interface).

When started using the systemd service file, `dhdynupdate` as an unprivileged
process. `dhdynudpate` can also execute as your user process.

## Features ##

* `dhdynupdate` supports updating both A and AAAA (IPv4 and IPv6) addresses.
* DNS records are updated on an as-needed basis to avoid sending unnecessary
DreamHost API calls
* `dhdynupdate` verifies & updates the DNS records for the configured
hostname upon dæmon instantiation
    * From there, `dhdynupdate` check your local IPv4 and/or IPv6 addresses.
    * If a IPv4/IPv6 address changes, `dhdynupdate` will update the
      corresponding entry in your DreamHost DNS Zone.

## Dependencies
`dhdynupdate` uses the following external modules:

* [`daemon`](https://pypi.python.org/pypi/python-daemon/)
    * Available in Debian/Ubuntu as `python3-daemon`
* [`netifaces`](https://pypi.python.org/pypi/netifaces)
    * Available in Debian/Ubuntu as `python3-netifaces`
* [`requests`](http://docs.python-requests.org/en/latest/)
    * Available in Debian/Ubuntu as `python3-requests`

# Installation
No binary packages exist yet, but, I've tested the following configuration on a
Debian Unstable/Sid system.

There is not an "easy" installation at this time; you will be required to copy
files into their proper destinations, and create a user for the dæmon to
execute as.

* Install dependencies:  
    * On Debian or Ubuntu, you should be able to:  `apt-get install python3-daemon python3-netifaces python3-requests`
* Create a `dhdynupdate` user/group for the dhdynupdate dæmon to execute as
* Copy (or clone) the git repository to `/usr/local/dhdyupdate`
* Copy `dhdynupdate.conf` to `/etc/`
* Create a directory for the logfile:
    `mkdir -p /var/log/dhdynupdate`
    `chown dhdynupdate:dhdynupdate /var/log/dhdynupdate`
* Install/activate the systemd service file:
    * Copy `dhdynupdate.service` to `/lib/systemd/system/`
    * `systemctl daemon-reload`
    * `systemctl enable dhdynupdate.service`

# Configuration
Configuration goes in `dhdynupdate.conf`, and is in the [Python 'config' file format.](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure)

## TL;DR config:
* Modify the following entires in `/etc/dhdynudpate.conf`:

	`AF_INET =  <interface with the IPv4 address you want to add to DreamHost DNS>`  
	`AF_INET6 = <interface with the IPv6 address you want to add to DreamHost DNS>`  

* Under `[your.domain.com]`, modify:

	`api_key = <your DreamHost API key>`
	`local_hostname = <the hostname you wish to add to DreamHost DNS>`


## Config File Sections
###`Global`
This section has global configuration options:

* Network interfaces to update the DNS records for
* [The DreamHost Web API URL](http://wiki.dreamhost.com/Application_programming_interface), and the logfile location.

###`DreamHost API Test Account`

* Uses The DreamHost test API key
* Only allows read-only operations
* It's a useful example to show the file format as well as a harmless test

###`your.domain.name`

* Insert `your.domain.name` for the name of your domain name.
* Also put in your DreamHost API key.

        [Global]
        # The DreamHost API URL; doubtful it'll change
        api_url = https://api.dreamhost.com/
        # External IPv4 and IPv6 interface to use
        # Separated as the subnet provided by my ISP is on a different interface
        # than the routing IP on my external interface.
        # IPv4 is the AF_INET address family
        AF_INET = eth1
        # IPv6 is the AF_INET6 family
        AF_INET6 = eth0
        # Log file
        log_file = /var/log/dhdynupdate.log
        # The update interval (in seconds)
        # for reference, 1h = 3600 s
        update_interval = 3600
        # PID file location
        pidfile = /run/dhdynupdate/dhdynupdate.pid
        
        [DreamHost API Test Account]
        api_key = 6SHU5P2HLDAYECUM
        local_hostname = ssh.thebesthostever.com
        
        [your.domain.name]
        api_key=6SHU5P2HLDAYECUM
        local_hostname = a6.groo.com

# Generating a DreamHost API Key

If you don't already have an appropriate API key:

* [Generate a new API key:](https://panel.dreamhost.com/?tree=home.api)
    * Make sure that `dns-*` is checked
    * Make sure *everything else* is unchecked

# Command-line usage

	usage: dhdynupdate.py [-h] [-d] [--debug lvl] [-c config]
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -d, --daemon          Execute dhdynupdate.py as a dæmon
	  --debug lvl           Log Level, one of CRITICAL, ERROR, WARNING, INFO,
	                        DEBUG
	  -c config, --config config
	                        Configuration name

If executed in daemon mode, `dhdynupdate` will dæmonize into a background
process, suitable for management using an init script or via systemd.

A config name is the name of the `dhdynupdate.conf` section you wish to use.
Multiple hostnames and API keys can be configured, enabling you to configure
multiple DNS domains or hostnames, and select which one to update at runtime.
 
For example, `./dhdynupdate.py -c your.domain.com` will load the
`[your.domain.name]` section in the `dhdynupdate.conf`.

# TODO:

* Proper [Python packaging](https://python-packaging.readthedocs.org/en/latest/)
* Maybe an RPM or Debian package
* OS X support

# FreeBSD License
Copyright (c) 2016, Troy Telford
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied.


![Created with VIM](http://www.vim.org/images/vim_created.gif "Created with VIM")
