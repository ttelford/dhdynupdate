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
import lockfile
import logging
import netifaces
import os
import time
import sys
from dhdns import dhdns
import interfaces

def setup_logger(logfile, log_level):
    """Does logging setup, using python logging"""
    try:
        logger = logging.basicConfig(
                 format='%(levelname)s:%(message)s',
                 filename = logfile,
                 filemode='w',
                 level=log_level)
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
        sys.exit(2)

def main(argv=None):
    """Command line parser, begins DaemonContext for main loop"""
    if argv is None:
        argv = sys.argv
    # Command line parsing...
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument("-d", "--daemon", action='store_true',
                            default=False, required=False,
                            dest="daemonize",
                            help="Execute %(prog)s as a dæmon")
    cmd_parser.add_argument("--debug", action='store', type=str,
                            default="WARNING", required=False,
                            dest="log_level", metavar="lvl",
                            help="Log Level, one of CRITICAL, ERROR, WARNING, INFO, DEBUG")
    cmd_parser.add_argument("-f", "--config-file", action='store',
                            type=str, default="/etc/dhdynupdate.conf",
                            required=False, metavar="path",
                            dest="configfile_path",
                            help="Configuration file path")
    config_name_default = "DreamHost API Test Account" 
    cmd_parser.add_argument("-c", "--config", action='store',
                            type=str, default=config_name_default,
                            required=False, metavar="config",
                            dest="config_name",
                            help="Configuration name; Conflicts with -m")
    cmd_parser.add_argument("-m", "--monitor-only", action='store_true',
                            default=False, required=False,
                            dest="monitor_only",
                            help="Only monitor the configured interfaces - don't access DreamHost API; Conflicts with -c")
    args = cmd_parser.parse_args()

    # read configuration from file
    config = configparser.ConfigParser()
    if len(config.read(args.configfile_path)) != 1:
        # Behavior of configparser.read() is to fail silently,
        #  returning an empty list of config filenames.
        print("Error reading config file!")
        sys.exit(3)

    if args.log_level == "CRITICAL":
        log_level = 50
    elif args.log_level == "ERROR":
        log_level = 40
    elif args.log_level == "WARNING":
        log_level = 30
    elif args.log_level == "INFO":
        log_level = 20
    elif args.log_level == "DEBUG":
        log_level = 10
    else:
        log_level = 0

    if args.monitor_only and not args.config_name in [config_name_default, ""]:
        print("Cannot specify -c and -m")
        sys.exit(4)

    # Get configuration settings
    try:
        supported_address_families = ("AF_INET", "AF_INET6")
        configured_interfaces = {}
        api_url = config["Global"]["api_url"]
        if not args.monitor_only:
            api_key = config[args.config_name]["api_key"]
            local_hostname = config[args.config_name]["local_hostname"]
        logfile = config["Global"]["log_file"]
        update_interval = int(config["Global"]["update_interval"])
        pid_file = config["Global"]["pidfile"]
        for addr_type in supported_address_families:
            interface = config["Global"][addr_type]
            # Accept valid interfaces and special external lookup "interface"
            if interface in netifaces.interfaces() or interface == "-ipify.org":
                configured_interfaces[addr_type] = interface
    except KeyError as error:
        # Technically, logger isn't "configured" -- it'll dump messages to the
        # console.
        print("Could not find configuration for %s" % (error))
        print("Create a configuration for this account, or specify a different "+
              "account with '-c'")
#        logging.critical("Could not find configuration for %s" % (error))
        sys.exit(4)
    except:
        print("Exception in parsing configuration settings: %s"
                         % (sys.exc_info()[0]))
#        logging.critical("Exception in parsing configuration settings: %s"
#                         % (sys.exc_info()[0]))
        sys.exit(5)

#   When in doubt, do not run as a daemon. Daemon keeps stack traces from being
#   printed, and you're left wondering why the dæmon is quitting.
    if args.daemonize:
        with daemon.DaemonContext(pidfile=lockfile.FileLock(pid_file)):
            # set up logging; it's much easier to just set it up within the
            # DaemonContext. Outside the daemoncontext requires a lot more work...
            setup_logger(logfile, log_level)
            logging.warning("Starting dhdynupdater...")
            try:
                pf = open(pid_file, 'w')
                pf.write("%s\n" % (os.getpid()))
                pf.close()
            except:
                logging.critical("Exception in setting up pidfile: %s" % (sys.exc_info()[0]))
                sys.exit(6)
            if not args.monitor_only:
                try:
                    dh_dns = dhdns(api_key, api_url, local_hostname, configured_interfaces)
                except:
                    logging.critical("Exception in creating dh_dns: %s" % (sys.exc_info()[0]))
            else:
                interface = interfaces.interfaces(configured_interfaces)
            while True:
                logging.warning("Starting dhdynupdater main loop...")
                try:
                    if args.monitor_only:
                        interface.addresses = interface.get_if_addresses(configured_interfaces)
                        print(interface.addresses)
                    else:
                        dh_dns.update_if_necessary()
                    time.sleep(update_interval)
                except:
                    logging.critical("Exception in main loop: %s" % (sys.exc_info()[0]))
                    logging.warning("Closing dhdynupdater...")
                    logging.shutdown()
                    sys.exit(0)
                logging.warning("looping dhdynupdater main loop...")
    else:
        if args.monitor_only:
            interface = interfaces.interfaces(configured_interfaces)
            print(interface.addresses)
        else:
            setup_logger(logfile, log_level)
            logging.warn("Starting dhdynupdater...")
            dh_dns = dhdns(api_key, api_url, local_hostname, configured_interfaces)
            dh_dns.update_if_necessary()

    logging.warning("Closing dhdynupdater...")
    logging.shutdown()

if __name__ == "__main__":
    main()

# vim: ts=4 sw=4 et
