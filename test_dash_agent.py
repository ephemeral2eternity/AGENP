# Test client agent file, client_agent.py
from client_agent import *
from ping import *
from get_available_srvs import *
from gcs_upload import *
import operator
import json

# Define a function to run DASH, QAS_DASH and CQAS_DASH in one client
def test_dash_agent(clientID, cache_agent, candidates, port, videoName):
	server_ips = get_available_srvs()
	client = clientID.split("_")[0]

	# Get server addresses for candidate servers
	server_addrs = {}
	for srv in server_ips.keys():
		server_addrs[srv] = server_ips[srv] + ":" + str(port)

	# ping all servers and get the mean RTT
	# print "=========== Pinging Candidate Servers ============="
	# RTTs = json.load(open("./info/pings.json"))
	candidate_rtts = {}
	for srv in candidates:
		if 'cache' in srv:
			print "=========== Pinging " + srv + "  ============="
			rtt = getRTT(server_ips[srv], 5)
			mnRtt = sum(rtt) / float(len(rtt))
			candidate_rtts[srv] = mnRtt
			# candidate_rtts[srv] = RTTs[client][srv]

	# Upload the ping RTTs to google cloud storage
	pingFile = "./data/" + clientID + "-PING.json"
	with open(pingFile, 'w') as outfile:
		json.dump(candidate_rtts, outfile, sort_keys = True, indent = 4, ensure_ascii=False)
	bucketName = "agens-data"
	gcs_upload(bucketName, pingFile)

	# Attach the closest server as cache agent
	sorted_rtts = sorted(candidate_rtts.items(), key=operator.itemgetter(1))
	selected_srv = sorted_rtts[0][0]

	# Perform simple DASH streaming
	dashID = clientID + '-DASH'
	print "=========== DASH Streaming for " + dashID + "  ============="
	print "########## The cache agent is : " + cache_agent + "##############"
	print "########## The default selected server is : " + selected_srv + " ##############"
	dash(cache_agent, server_addrs, selected_srv, videoName, dashID)
