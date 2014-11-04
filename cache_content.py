import os

def cache_content(contentName):
	# Execute gsutil command to cache content
	os.system('gsutil cp -r gs://agenp-videos/' + contentName + ' ../videos/')
