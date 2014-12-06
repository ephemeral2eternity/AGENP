import json
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from gce_authenticate import *
from destroy import *

# Get the driver from an authentication json file which defines the service account, pem file path, datacenter, and project.
driver = gce_authenticate("./info/auth.json")

# The agents to be deleted
nodeZones = {}
nodeZones['agens-01'] = 'asia-east1-a'
nodeZones['agens-02'] = 'asia-east1-b'
nodeZones['agens-03'] = 'asia-east1-c'
nodeZones['agens-04'] = 'europe-west1-b'
nodeZones['agens-05'] = 'europe-west1-b'
nodeZones['agens-06'] = 'europe-west1-c'
nodeZones['agens-07'] = 'us-central1-a'
nodeZones['agens-08'] = 'us-central1-b'
nodeZones['agens-09'] = 'us-central1-f'

for node in nodeZones.keys():
	print "Destroying node: ", node
	destroy(driver, node, nodeZones[node])
