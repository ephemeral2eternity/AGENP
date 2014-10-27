import json
import os
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from authenticate import *
from provision import *

# Download auth.json from google cloud storage
os.system('gsutil cp gs://agenp-storage/auth.json ./')

# Get the driver from an authentication json file which defines the service account, pem file path, datacenter, and project.
driver = authenticate("auth.json")

# Instances to create
nodeType = "f1-micro"
nodeSize = 20
image = "agenp"
zone = "us-central1-a"

# Provision node
node = provision(driver, nodeType, nodeSize, image, zone)

