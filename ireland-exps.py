# Script to run experiments from INESC-Porto client
from test_client_agent import *
from get_available_srvs import *
import operator
port = 8615
video = 'BBB'

## Determine the cache agent from all available agents
server_ips = get_available_srvs()
# ping all servers and get the mean RTT
print "=========== Pinging All Agents ============="
srv_rtts = {}
for srv in server_ips.keys():
	if srv != "agens-web":
		print "=========== Pinging " + srv + "  ============="
		rtt = getRTT(server_ips[srv], 5)
                mnRtt = sum(rtt) / float(len(rtt))
                srv_rtts[srv] = mnRtt

sorted_rtts = sorted(srv_rtts.items(), key=operator.itemgetter(1))
cache_agent = sorted_rtts[0][0]

# Experiment 1: two candidate servers within the same zone in the same region
candidates = ['agens-04', 'agens-05']
clientID = 'ireland-exp1'
test_client_agent(clientID, cache_agent, candidates, port, video)

# Experiment 2: two candidate servers within the same regions in the different zones
candidates = ['agens-05', 'agens-06']
clientID = 'ireland-exp2'
test_client_agent(clientID, cache_agent, candidates, port, video)

# Experiment 3: two candidate servers in different regions
candidates = ['agens-06', 'agens-08']
clientID = 'ireland-exp3'
test_client_agent(clientID, cache_agent, candidates, port, video)

# Experiment 4: two candidate servers within the same regions remotely
candidates = ['agens-08', 'agens-07']
clientID = 'ireland-exp4'
test_client_agent(clientID, cache_agent, candidates, port, video)

# Experiment 5: two candidate servers within different regions remotely
candidates = ['agens-02', 'agens-07']
clientID = 'ireland-exp5'
test_client_agent(clientID, cache_agent, candidates, port, video)

# Experiment 6: two candidate servers in the different regions, one locally and the other remotely
candidates = ['agens-01', 'agens-09']
clientID = 'ireland-exp6'
test_client_agent(clientID, cache_agent, candidates, port, video)

# Experiment 7: two candidate servers within the same remote region
candidates = ['agens-01', 'agens-03']
clientID = 'ireland-exp7'
test_client_agent(clientID, cache_agent, candidates, port, video)

# Experiment 2: two candidate servers within different remote regions
candidates = ['agens-02', 'agens-09']
clientID = 'ireland-exp8'
test_client_agent(clientID, cache_agent, candidates, port, video)
