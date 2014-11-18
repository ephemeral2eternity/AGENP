# Define a function to upload a file to google cloud storage
# @author: chenw@cmu.edu
import argparse
import httplib2
import os
import sys
import requests
import json

from apiclient import discovery, http
from oauth2client import client
from oauth2client import tools
from get_storage_authenticate_service import *

FULL_SCOPE = 'https://www.googleapis.com/auth/devstorage.full_control'

def gs_upload(authFile, bucketName, fPath):
	# Get the storage service object
	service = get_storage_authenticate_service(authFile, FULL_SCOPE)

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
