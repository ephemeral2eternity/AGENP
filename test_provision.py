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
nodeSize = 30
image = "agens-web"
zone = "us-central1-a"
nodeName = "agens-0x"

# Provision node
node = provision(driver, nodeType, nodeSize, image, zone, nodeName)

