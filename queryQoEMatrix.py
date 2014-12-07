"""
The code to query all agents and their QoE evaluations on other servers.
"""
import requests
import json
from get_available_srvs import *

# ================================================================================
# Query cache agent about how it observes user experiences with all servers
# @input : cache_agent --- The cache agent the user is closest to
# @return: qoe_vector --- QoEs of all servers observed from cache_agent
# ================================================================================
def query_QoE(cache_agent):
	print "Query address: ", cache_agent
	r = requests.get("http://" + cache_agent + "/QoE?query")
	qoe_vector = json.loads(r.headers['Params'])
	return qoe_vector

# ================================================================================
# Query several agents about how they evaluate others 
# @input : agentList --- The list of agents to query
#		   srvAddrs --- The addresses of all agents
# @return: QoEMat --- All server QoE evaluations for these agents (Stored in a dict)
# ================================================================================
def getQoEMatrix(agentList, srvAddrs):
	QoEMat = {}
	for agent in agentList:
		print "Query Agent: " + agent
		qoe_vector = query_QoE(srvAddrs[agent])
		QoEMat[agent] = qoe_vector
	return QoEMat

# ================================================================================
agents = ['cache-agent-01', 'cache-agent-02', 'cache-agent-03', 'cache-agent-04', 'cache-agent-05', 'cache-agent-06', 'cache-agent-07', 'cache-agent-08']
server_ips = get_available_srvs()
server_addrs = {}
for srv in server_ips.keys():
	if "cache-agent" in srv:
		server_addrs[srv] = server_ips[srv] + ":8615"

print "All servers on google cloud now are: "
print server_addrs
qoeDict = getQoEMatrix(agents, server_addrs)

# Upload the ping RTTs to google cloud storage
qoeMatFile = "./data/QoEMatrix.json"
with open(qoeMatFile, 'w') as outfile:
	json.dump(qoeDict, outfile, sort_keys = True, indent = 4, ensure_ascii=False)


