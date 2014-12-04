import json
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from gce_authenticate import *

def get_available_srvs():
	driver = gce_authenticate("./info/auth.json")

	# List all instances
	server_ips = {}
	nodes = driver.list_nodes()
	for node in nodes:
		server_ips[node.name] = node.public_ips[0]

	return server_ips

