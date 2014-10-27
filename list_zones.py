from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

def list_zones(driver):
	zones = driver.ex_list_zones()
	print '|        id       ', '|   name   ', '|status '
	for zone in zones:
		print zone.id, zone.name, zone.status
