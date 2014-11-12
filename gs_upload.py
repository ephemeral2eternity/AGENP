# Define a function to upload a file to google cloud storage
# @author: chenw@cmu.edu
import argparse
import httplib2
import os
import sys
import json
import requests
import json

from apiclient import discovery, http
from oauth2client import file
from oauth2client import client
from oauth2client import tools

def gs_upload(authFile, bucketName, fPath):
	api_version = 'v1'

	# Read account name and key file
	jsonFile = open(authFile)
	authData = json.load(jsonFile)
	jsonFile.close()

	# Read key file
	client_email = authData["Account"]
	secret_file = authData["Secret"]
	secret_file_path = os.path.expanduser(secret_file)
	print secret_file_path
	with open(secret_file_path) as f:
		private_key = f.read()

	# Authenticate httplib2.http object
	credentials = client.SignedJwtAssertionCredentials(client_email, private_key, 'https://www.googleapis.com/auth/devstorage.full_control')
	hp = httplib2.Http()
	hp = credentials.authorize(hp)

	# Construct the service object for the interacting with the Cloud Storage API
	service = discovery.build('storage', api_version, http=hp)

	# Upload the file fName to bucket
	try:
		media = http.MediaFileUpload(fPath, mimetype='text/plain')
		fHead, fName = os.path.split(fPath)
		req = service.objects().insert(bucket=bucketName, media_body=media, name=fName)
		resp = req.execute()
		# print json.dumps(resp, indent=2)
	except client.AccessTokenRefreshError:
		print ("The credentials have been revoked or expired, please re-run"
			"the application to re-authorize")
