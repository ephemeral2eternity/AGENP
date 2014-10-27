import json
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from authenticate import *
from list_zones import *

# Get the driver from an authentication json file which defines the service account, pem file path, datacenter, and project.
driver = authenticate("auth.json")
# list_zones(driver)

# Create a new node
nodeName = "agenp01";
nodeSize = "f1-micro"
imageName = "backports-debian-7-wheezy-v20141021"
zone = "europe-west1-b"
diskSize = 20

# Create a boot disk
bootDisk = driver.create_volume(diskSize, nodeName, location=zone);

# Provision a disk
node_agenp01 = driver.create_node(nodeName, nodeSize, imageName, location=zone, ex_network='default', ex_boot_disk=bootDisk)
