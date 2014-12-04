import json
import os
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from gce_authenticate import *
from provision import *

# Download auth.json from google cloud storage
# os.system('gsutil cp gs://agens-storage/auth.json ./info/')

# Get the driver from an authentication json file which defines the service account, pem file path, datacenter, and project.
driver = gce_authenticate("./info/auth.json")

# List all instances
existing_nodes = driver.list_nodes()
for node in existing_nodes:
	print node.__dict__.keys()
	print node.id, node.name, node.public_ips[0], node.size, node.state, node.image
