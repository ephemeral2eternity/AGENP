import json
import os
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from gce_authenticate import *
from list_zones import *

def destroy(driver, nodeName, zoneName):
	# Get a vm node
	node = driver.ex_get_node(nodeName, zone=zoneName)

	# Destroy the vm
	# driver.reboot_node(node)
	driver.destroy_node(node, destroy_boot_disk=True)
	# os.system('gsutil rm gs://agenp-storage/' + nodeName + '.json')
