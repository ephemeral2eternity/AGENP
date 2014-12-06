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
def getQoEMatrix(agentList, srvIPs):
	QoEMat = {}
	for agent in agentList:
		print "Query Agent: " + agent
		qoe_vector = query_QoE(srvIPs[agent] + ":8615")
		QoEMat[agent] = qoe_vector
	return QoEMat

# ================================================================================
agents = ['agens-02', 'agens-04', 'agens-05', 'agens-08', 'agens-09']
server_ips = get_available_srvs()
print "All servers on google cloud now are: "
print server_ips
qoeDict = getQoEMatrix(agents, server_ips)

# Upload the ping RTTs to google cloud storage
qoeMatFile = "./data/QoEMatrix.json"
with open(qoeMatFile, 'w') as outfile:
	json.dump(qoeDict, outfile, sort_keys = True, indent = 4, ensure_ascii=False)


