import json
import os
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

def find_maxID(existing_nodes):
	ids = []
	for node in existing_nodes:
		node_id = int(node.name[-2:])
		ids.append(node_id)
	max_id = max(ids)
	return max_id

def provision(driver, nodeType, nodeSize, image, zone, nodeName):
	# List all instances
	existing_nodes = driver.list_nodes()

	## Get the id of the new node.
	#if not existing_nodes:
	#	nodeID = 1
	#else:
	#	nodeID = find_maxID(existing_nodes) + 1

	# Create a new node
	# nodeName = "agens-" + str(nodeID).zfill(2)

	# Get the image
	imageFile = driver.ex_get_image(image)

	# Create a boot disk
	bootDisk = driver.create_volume(nodeSize, nodeName, location=zone, image=imageFile)

	# Provision a disk
	node = driver.create_node(nodeName, nodeType, image, location=zone, ex_network='default', ex_boot_disk=bootDisk, use_existing_disk=True)

	return node
