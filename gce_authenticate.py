import json
from pprint import pprint
from service_account import service_account as SA
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

def gce_authenticate(authFile):
	sa = SA(authFile)

	ComputeEngine = get_driver(Provider.GCE)
	# Datacenter is set to 'us-central1-a' as an example, but can be set to any
	# zone, like 'us-central1-b' or 'europe-west1-a'
	print "The account to access Google Compute Engine is as follows:"
	print "Account: ", sa.account
	print "Secret file location: ", sa.secret
	print "Project: ", sa.project
	driver = ComputeEngine(sa.account, sa.secret, project=sa.project, auth_type="SA")
	return driver
