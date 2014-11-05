import json
import os
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

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

	# Get the image
	imageFile = driver.ex_get_image(image)

	# Create a boot disk
	bootDisk = driver.create_volume(nodeSize, nodeName, location=zone, image=imageFile)

	# Provision a disk
	node = driver.create_node(nodeName, nodeType, image, location=zone, ex_network='default', ex_boot_disk=bootDisk, use_existing_disk=True)

	# Write JSON file and upload to gs://agens-storage/
	os.system('gcloud compute instances describe ' + nodeName + ' --format json' + ' --zone ' + zone + ' > ' + nodeName + '.json')

	os.system('gsutil cp ./' + nodeName + '.json gs://agens-storage/')
	return node
