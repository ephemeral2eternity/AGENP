import json
import os
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from authenticate import *
from provision import *

# Download auth.json from google cloud storage
<<<<<<< HEAD
os.system('gsutil cp gs://agens-storage/auth.json ./')
=======
os.system('gsutil cp gs://agens-storage/auth.json ./info/')
>>>>>>> ddffa2013265fa5e2807a4ac4c01d7c047c3d251

# Get the driver from an authentication json file which defines the service account, pem file path, datacenter, and project.
driver = authenticate("./info/auth.json")

# Instances to create
nodeType = "f1-micro"
nodeSize = 20
image = "agenp"
zone = "us-central1-a"

# Provision node
node = provision(driver, nodeType, nodeSize, image, zone)

