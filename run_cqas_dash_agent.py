# Script to run experiments from INESC-Porto client
from test_cqas_dash_agent import *
from get_available_srvs import *
from time import sleep
import random
import sys
import json
import operator

port = 8615
video = 'BBB'

client = sys.argv[1]

## Read json cache_agents.json file to get cache_agent
cache_agents = json.load(open("./info/cache_agents.json"))
cache_agent = cache_agents[client]
print "=============== Cache Agent for Client: ", client, " is ", cache_agent, " ======================"

## Read json exp candidates file
expCandidates = json.load(open("./info/exp.json"))

expNum = 6

for i in range(1, expNum + 1):
	expID = 'exp' + str(i)
	candidates = expCandidates[client][expID]
	clientID = client + "-" + expID
	print "Selected candidate servers for ", clientID, " are :"
	for srv in candidates:
		print srv
	test_cqas_dash_agent(clientID, cache_agent, candidates, port, video)
