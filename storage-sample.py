# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# [START all]
"""Command-line skeleton application for Cloud Storage API.
Usage:
  $ python storage-sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python storage-sample.py --help

"""

import argparse
import httplib2
import os
import sys
import json
import requests

from apiclient import discovery, http
from oauth2client import file
from oauth2client import client
from oauth2client import tools

def dump(obj):
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))

def main(argv):
  # Define sample variables.
  _BUCKET_NAME = 'agens-data'
  _API_VERSION = 'v1'

  # Parser for command-line arguments.
  parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])
  
  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  print "parse input done"

  client_email = '840406026086-56d4ehaiu6ujfb8gkb9om7t71p1ekpeo@developer.gserviceaccount.com'
  with open("/Users/Chen/secrets/agens.p12") as f:
    private_key = f.read()

  credentials = client.SignedJwtAssertionCredentials(client_email, private_key,
    'https://www.googleapis.com/auth/devstorage.full_control')

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  hp = httplib2.Http()
  hp = credentials.authorize(hp)

  # Construct the service object for the interacting with the Cloud Storage API.
  service = discovery.build('storage', _API_VERSION, http=hp)

  try:
    req = service.buckets().get(bucket=_BUCKET_NAME)
    resp = req.execute()
    print json.dumps(resp, indent=2)

    # try insert an file
    media = http.MediaFileUpload("./data/chenw.txt", 'text/plain')
    req = service.objects().insert(bucket=_BUCKET_NAME, media_body=media, name="chenw.txt")
    resp = req.execute()
    print json.dumps(resp, indent=2)

    fields_to_return = 'nextPageToken,items(name,size,contentType,metadata(my-key))'
    req = service.objects().list(bucket=_BUCKET_NAME, fields=fields_to_return)
    # If you have too many items to list in one request, list_next() will
    # automatically handle paging with the pageToken.
    while req is not None:
      resp = req.execute()
      print json.dumps(resp, indent=2)
      req = service.objects().list_next(req, resp)

  except client.AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")



if __name__ == '__main__':
  main(sys.argv)
# [END all]
