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

import argparse
import configparser
import daemon
import logging
import netifaces
import time
import sys
from dhdns import dhdns

def setup_logger(logfile):
    try:
        logger = logging.basicConfig(
                 format='%(levelname)s:%(message)s',
                 filename = logfile,
                 filemode='w',
                 level=logging.DEBUG)
    except PermissionError as error:
        logging.critical("%s" % (error))
    except FileNotFoundError as error:
        logging.critical("It's likely your logfile path is invalid: %s" % (logfile))
        logging.critical("%s" % (error))
    except NameError as error:
        logging.critical("%s" % (error))
    except:
        logging.critical("Exception in setting up logging: %s" % (sys.exc_info()[0]))
        logging.critical("Could not set up logging! Exiting!")
        sys.exit(1)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    # Command line parsing...
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument("-d", "--daemon", action='store_true',
                            default=False, required=False,
                            dest="daemonize",
                            help="Execute %(prog)s as a dæmon")
    cmd_parser.add_argument("-c", "--config", action='store',
                            type=str, default="DreamHost API Test Account",
                            required=False, metavar="config",
                            dest="config_name",
                            help="Configuration name")
    args = cmd_parser.parse_args()

    # read configuration from file
    config = configparser.ConfigParser()
    try:
        config.read("dhdynupdate.conf")
    except:
        print("Error reading config file!")
        sys.exit()

    # Get configuration settings
    try:
        supported_address_families = ("AF_INET", "AF_INET6")
        configured_interfaces = {}
        api_key = config[args.config_name]["api_key"]
        api_url = config["Global"]["api_url"]
        local_hostname = config[args.config_name]["local_hostname"]
        logfile = config["Global"]["log_file"]
        update_interval = int(config["Global"]["update_interval"])
        for addr_type in supported_address_families:
            interface = config["Global"][addr_type]
            if interface in netifaces.interfaces():
                configured_interfaces[addr_type] = interface
    except KeyError as error:
        # Technically, logger isn't "configured" -- it'll dump messages to the
        # console.
        logging.critical("Could not find configuration for %s" % (error))
        sys.exit(1)
    except:
        logging.critical("Exception in parsing configuration settings: %s"
                         % (sys.exc_info()[0]))
        sys.exit(1)

#   When in doubt, do not run as a daemon. Daemon keeps stack traces from being
#   printed, and you're left wondering.
    if args.daemonize:
        with daemon.DaemonContext():
            # set up logging; it's much easier to just set it up within the
            # DaemonContext. Outside the daemoncontext requires a lot more work...
            setup_logger(logfile)
            dh_dns = dhdns(api_key, api_url, local_hostname, configured_interfaces)
            while True:
                dh_dns.update_if_necessary()
                time.sleep(update_interval)
    else:
        setup_logger(logfile)
        dh_dns = dhdns(api_key, api_url, local_hostname, configured_interfaces)
        dh_dns.update_if_necessary()

    logging.shutdown()

if __name__ == "__main__":
    main()

# vim: ts=4 sw=4 et
