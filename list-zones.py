from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

account = 'wangchen615@gmail.com'
pemFile = '~/gcloud/secret/agenp.pem'
dcName = 'europe-west1-a'
projID = 'long-micron-712'

ComputeEngine = get_driver(Provider.GCE)
# Datacenter is set to 'us-central1-a' as an example, but can be set to any
# zone, like 'us-central1-b' or 'europe-west1-a'
driver = ComputeEngine('1050790087234-i7b9ehtntguua9ti4espkovcftgroall@developer.gserviceaccount.com', '~/gcloud/secret/PRIV.pem', project='long-micron-712')

zones = driver.ex_list_zones()
print '|        id       ', '|   name   ', '|status '
for zone in zones:
	print zone.id, zone.name, zone.status
