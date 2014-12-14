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

## Determine the cache agent from all available agents
server_ips = get_available_srvs()
all_cache_agents = []
# ping all servers and get the mean RTT
print "=========== Pinging All Agents ============="
srv_rtts = {}
for srv in server_ips.keys():
        if "agens" in srv and "web" not in srv:
                print "=========== Pinging " + srv + "  ============="
                rtt = getRTT(server_ips[srv], 5)
                mnRtt = sum(rtt) / float(len(rtt))
                srv_rtts[srv] = mnRtt
		all_cache_agents.append(srv)
		print "=========== RTT to " + srv + " is ", str(mnRtt), " ============"

print "All available cache agents are: "
print all_cache_agents

