import json
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from gce_authenticate import *
from destroy import *

# Get the driver from an authentication json file which defines the service account, pem file path, datacenter, and project.
driver = gce_authenticate("./info/auth.json")
# list_zones(driver)

# Create a new node
# nodeName = "agenp1";
# zone = "europe-west1-b"
nodeName = "agens-01"
zone = "us-central1-a"

destroy(driver, nodeName, zone)
