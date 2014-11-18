# Authenticate google storage service using the service account and pem file.
# @input: authFile -- The details of service account and the location of pem file 
#			is defined in authFile
#	  scope -- The scope of controlling the google storage
# @return: the storage service handler
# @author: Chen Wang, chenw@cmu.edu

import httplib2
import os
import json

from apiclient import discovery, http
from oauth2client import file, client, tools

def get_storage_authenticate_service(authFile, scope):
        api_version = 'v1'

        # Read account name and key file
        jsonFile = open(authFile)
        authData = json.load(jsonFile)
        jsonFile.close()

        # Read key file
        client_email = authData["Account"]
        secret_file = authData["Secret"]
        secret_file_path = os.path.expanduser(secret_file)
        with open(secret_file_path) as f:
                private_key = f.read()

        # Authenticate httplib2.http object
        credentials = client.SignedJwtAssertionCredentials(client_email, private_key, scope)
        hp = credentials.authorize(httplib2.Http())
        service = discovery.build('storage', api_version, http=hp)
        return service
