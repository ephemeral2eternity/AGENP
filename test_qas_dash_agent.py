# Test client agent file, client_agent.py
from client_agent import *
from ping import *
from get_available_srvs import *
from gcs_upload import *
import operator

# Define a function to run DASH, QAS_DASH and CQAS_DASH in one client
def test_client_agent(clientID, cache_agent, candidates, port, videoName):
	server_ips = get_available_srvs()

	# Get server addresses for candidate servers
	server_addrs = {}
	for srv in server_ips.keys():
		server_addrs[srv] = server_ips[srv] + ":" + str(port)

	# Perform QAS DASH streaming
	qasdashID = clientID + '-QAS_DASH'
	print "=========== QAS-DASH Streaming for " + qasdashID + "  ============="
	print "########## The cache agent is : " + cache_agent + ". ##############"
	alpha = 0.5
	qas_dash(cache_agent, server_addrs, candidates, videoName, qasdashID, alpha)
