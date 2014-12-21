import json
import os
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from gce_authenticate import *
from list_zones import *

# Download auth.json from google cloud storage
# os.system('gsutil cp gs://agens-storage/auth.json ./info/')

# Get the driver from an authentication json file which defines the service account, pem file path, datacenter, and project.
driver = gce_authenticate("./info/auth.json")

# List all zones
list_zones(driver)
