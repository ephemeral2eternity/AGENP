import json
import os
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from authenticate import *
from destroy import *

# Download auth.json from google cloud storage
os.system('gsutil cp gs://agens-storage/auth.json ./info/')

# Get the driver from an authentication json file which defines the service account, pem file path, datacenter, and project.
driver = authenticate("./info/auth.json")

# List all instances
existing_nodes = driver.list_nodes()
for node in existing_nodes:
	# print node.__dict__.keys()
	# print node.id, node.name, node.public_ips[0], node.size, node.state, node.image
	if "cache-" in node.name:
		print "Deleting node : ", node.name
		destroy(driver, node.name, node.datacenter)
