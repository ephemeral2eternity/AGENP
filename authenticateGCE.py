import json
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

def authenticateGCE():

	ComputeEngine = get_driver(Provider.GCE)
	# Datacenter is set to 'us-central1-a' as an example, but can be set to any
	# zone, like 'us-central1-b' or 'europe-west1-a'
	driver = ComputeEngine(datacenter='us-central1-a', project='agents-web')
	return driver
