import json
import os
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from authenticate import *

def provision(driver, nodeType, nodeSize, image, zone):
	# List all instances
	existing_nodes = driver.list_nodes()

	# Get the id of the new node.
	if not existing_nodes:
		nodeID = 1
	else:
		nodeID = len(existing_nodes) + 1

	# Create a new node
	nodeName = "agenp" + str(nodeID)

	# Create a boot disk
	bootDisk = driver.create_volume(nodeSize, nodeName, location=zone)

	# Provision a disk
	node = driver.create_node(nodeName, nodeType, image, location=zone, ex_network='default', ex_boot_disk=bootDisk)

	# Write JSON file and upload to gs://agenp-storage/
	nodeData = [{ "Name" : nodeName,
		      "Disk" : nodeName,
		      "Type" : nodeSize,
		      "Image": imageName,
		      "Location": zone,
		      "DiskSize": diskSize}]

	jsonFile = open(nodeName + ".json", "w")
	jsonFile.write(json.dumps(nodeData))
	jsonFile.close

	os.system('gsutil cp ./' + nodeName + '.json gs://agenp-storage/')
	return node
