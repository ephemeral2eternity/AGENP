import json
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from authenticate import *
from destroy import *

# Get the driver from an authentication json file which defines the service account, pem file path, datacenter, and project.
driver = authenticate("auth.json")
# list_zones(driver)

# Create a new node
nodeName = "agenp01";
zone = "europe-west1-b"

destroy(driver, nodeName, zone)
