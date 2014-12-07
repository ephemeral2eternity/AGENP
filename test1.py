# Script to run experiments from INESC-Porto client
from test_client_agent import *
from get_available_srvs import *
from ping import *
import operator

port = 8615
video = 'BBB'
cache_agent = 'agens-04'

## Determine the cache agent from all available agents
server_ips = get_available_srvs()
# ping all servers and get the mean RTT
print "=========== Pinging All Agents ============="
srv_rtts = {}
for srv in server_ips.keys():
        if "cache-agent" in srv:
                print "=========== Pinging " + srv + "  ============="
                rtt = getRTT(server_ips[srv], 5)
                mnRtt = sum(rtt) / float(len(rtt))
                srv_rtts[srv] = mnRtt

sorted_rtts = sorted(srv_rtts.items(), key=operator.itemgetter(1))
cache_agent = sorted_rtts[0][0]

# Experiment 1: two candidate servers within the same zone in the same region
candidates = ['cache-agent-04', 'cache-agent-05']
clientID = 'test1'
# test_client_agent(clientID, cache_agent, candidates, port, video)

# Get server addresses for candidate servers
server_addrs = {}
for srv in server_ips.keys():
	server_addrs[srv] = server_ips[srv] + ":" + str(port)

# ping all servers and get the mean RTT
candidate_rtts = {}
for srv in candidates:
	rtt = srv_rtts[srv]

# Perform Collaborative QAS DASH streaming
for i in range(1, 10):
	expID = "exp" + str(i)
	cqasdashID = clientID + "-" + expID + '-CQAS_DASH'
	print "=========== Collaborative QAS-DASH Streaming for " + cqasdashID + "  ============="
	alpha = 0.5
	cqas_dash(cache_agent, server_addrs, candidates, video, cqasdashID, alpha)
