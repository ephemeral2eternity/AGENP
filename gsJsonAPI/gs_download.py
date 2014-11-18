# Define a function to recursively download a folder of files from google cloud storage
# @author: Chen Wang, chenw@cmu.edu
import httplib2
import os
import sys
import random
import json
import urllib

from apiclient import discovery, http
from apiclient.errors import HttpError
from oauth2client import client, tools
from get_storage_authenticate_service import *

RW_SCOPE = 'https://www.googleapis.com/auth/devstorage.read_write'
RO_SCOPE = 'https://www.googleapis.com/auth/devstorage.read_only'
FULL_SCOPE = 'https://www.googleapis.com/auth/devstorage.full_control'

# Retry transport and file IO errors.
RETRYABLE_ERRORS = (httplib2.HttpLib2Error, IOError)

# Number of times to retry failed downloads.
NUM_RETRIES = 5

# Number of bytes to send/receive in each request.
CHUNKSIZE = 2 * 1024 * 1024

def handle_progressless_iter(error, progressless_iters):
	if progressless_iters > NUM_RETRIES:
		print 'Failed to make progress for too many consecutive iterations.'
	raise error

	sleeptime = random.random() * (2**progressless_iters)
	print ('Caught exception (%s). Sleeping for %s seconds before retry #%d.' % (str(error), sleeptime, progressless_iters))
	time.sleep(sleeptime)

def gs_download(authFile, bucketName, objectName, fPath):
	# Construct the service object
	service = get_storage_authenticate_service(authFile, RO_SCOPE)

	fName = os.path.basename(objectName)
	f = open(fPath + fName, 'w')
	request = service.objects().get_media(bucket=bucketName, object=objectName)
	request.uri = urllib.unquote(request.uri)
	print request.uri
	media = http.MediaIoBaseDownload(f, request, chunksize=CHUNKSIZE)
	
	progressless_iters = 0
	done = False
	while not done:
		error = None
		try:
			progress, done = media.next_chunk()
		except HttpError, err:
			error = err
			if err.resp.status < 500:
				raise
		except RETRYABLE_ERRORS, err:
			error = err

		if error:
			progressless_iters += 1
			handle_progressless_iter(error, progressless_iters)
		else:
			progressless_iters = 0
