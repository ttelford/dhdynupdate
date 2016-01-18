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
import logging
import requests
import sys
import uuid

class http_access():
    # Initialize...
    def __init__(self, api_url):
        """Initialize HTTP(S) Goo"""
        self.api_url = api_url

    def request_get(self, request_params):
        """HTTP(S) GET Request"""
        # Use a UUID to ensure our request is unique, only processed once.
        request_params["unique_id"]=str(uuid.uuid4())
        try:
            dreamhost_response = requests.get(self.api_url, params=request_params)
        except:
            logging.critical("Unexpected error:", sys.exc_info()[0])
            print("Unexpected error:", sys.exc_info()[0])
            message="Could not contact host %(api_url)s.  Exiting"
            print(message)
            logging.critical(message)
            raise
            sys.exit()
        dreamhost_response.close()
        logging.debug("API URL:" + self.api_url)
        logging.debug(dreamhost_response.request.headers)
        logging.debug(dreamhost_response.request.url)
        response_json = dreamhost_response.json()
        if response_json["result"] != "success":
            logging.error("DreamHost did not complete the request: %s"
                          % (request_params))
        else:
            logging.info("Successful Request:  %s, %s"
                          % (response_json["result"],
                            (json.dumps(dreamhost_response.json(),
                            sort_keys=True, indent=4))))
        return response_json

# vim: ts=4 sw=4 et
