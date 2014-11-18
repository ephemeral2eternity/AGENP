# Define a function to download a video file folder from google cloud storage
import httplib2
import os
import time
import json

from apiclient import discovery, http
from oauth2client import client, file, tools
from gcs_authenticate import *

def cache_content(contentName):
	# Execute gsutil command to cache content
	authFile = "./info/auth.json"
	bucketName = "agens-videos"
	gcs_authenticate(authFile)
	os.system('gsutil cp -r gs://agenp-videos/' + contentName + ' ../videos/')
