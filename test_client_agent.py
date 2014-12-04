# Test client agent file, client_agent.py

from client_agent import *

cache_agent = 'agenp-01'
server_addrs = {}
server_addrs['agens-01'] = '130.211.49.19:8615'
server_addrs['agens-02'] = '130.211.118.248:8615'
videoName = 'BBB'


clientID = 'Chen_DASH'
dash(cache_agent, server_addrs, videoName, clientID)

clientID = 'Chen_QAS_DASH'
alpha = 0.5
qas_dash(cache_agent, server_addrs, videoName, clientID, alpha)

clientID = 'Chen_CQAS_DASH'
cqas_dash(cache_agent, server_addrs, videoName, clientID)
