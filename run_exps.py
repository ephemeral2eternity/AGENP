# Script to run experiments from INESC-Porto client
from test_client_agent import *
from get_available_srvs import *
from time import sleep
import random
import sys
import operator

port = 8615
video = 'BBB'

client = sys.argv[1]
# client = 'porto'
# cache_agent = 'agens-05'

## Determine the cache agent from all available agents
server_ips = get_available_srvs()
all_cache_agents = []
# ping all servers and get the mean RTT
print "=========== Pinging All Agents ============="
srv_rtts = {}
for srv in server_ips.keys():
        if "cache-agent" in srv:
                print "=========== Pinging " + srv + "  ============="
                rtt = getRTT(server_ips[srv], 5)
                mnRtt = sum(rtt) / float(len(rtt))
                srv_rtts[srv] = mnRtt
		all_cache_agents.append(srv)

print "All available cache agents are: "
print all_cache_agents

sorted_rtts = sorted(srv_rtts.items(), key=operator.itemgetter(1))
cache_agent = sorted_rtts[0][0]

print "=============== Cache Agent for Client: ", client, " is ", cache_agent, " ======================"

expNum = 10
clientCandidates = {}
clientCandidates["cache-agent"] = cache_agent

for i in range(1, expNum + 1):
	candidates = random.sample(all_cache_agents, 2)
	expID = 'exp' + str(i)
	clientID = client + "-" + expID
	print "Selected candidate servers for ", clientID, " are :"
	print candidates
	test_client_agent(clientID, cache_agent, candidates, port, video)
	clientCandidates[expID] = candidates
	sleep(random.randint(10, 600))

	candidateFile = "./data/" + client + "-candidates.json"
	with open(candidateFile, 'w') as outfile:
		json.dump(clientCandidates, outfile, sort_keys = True, ident = 4, ensure_ascii=False)

	# upload the file to google cloud
	bucketName = "agens-data"
	gcs_upload(bucketName, candidateFile)
