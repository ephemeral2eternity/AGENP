import json
import os
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from gcs_authenticate import *
from gce_authenticate import *
from provision import *

# Authenticate GCS (Google Cloud Storage)
gcs_authenticate("./info/auth.json")

# Download auth.json from google cloud storage
os.system('gsutil cp gs://agens-storage/auth.json ./info/')

# Authenticate GCE
# Get the driver from an authentication json file which defines the service account, pem file path, datacenter, and project.
driver = gce_authenticate("./info/auth.json")

# Instances to create
nodeType = "f1-micro"
nodeSize = 10
image = "agens-client"
zones = [
	 "us-central1-a",
	 "us-central1-b",
	 "us-central1-f"]

# Provision node in all available zones
i = 6
users = ['a', 'b', 'c']
for zone in zones:
	for u in users:
		nodeID = "cli-" + str(i) + u 
		print "========= Provision f1-micro in Zone " + zone + " named " + nodeID + " ================="
		node = provision(driver, nodeType, nodeSize, image, zone, nodeID)
	i = i + 1
