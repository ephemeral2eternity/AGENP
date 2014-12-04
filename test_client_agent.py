# Test client agent file, client_agent.py

from client_agent import *

cache_agent = 'agens'
server_addrs = {}
server_addrs['agens'] = '104.155.15.0:8615'
server_addrs['agens-02'] = '130.211.108.80:8615'
videoName = 'BBB'


#clientID = 'INESC-DASH'
#dash(cache_agent, server_addrs, videoName, clientID)

clientID = 'INESC-QAS_DASH'
alpha = 0.5
qas_dash(cache_agent, server_addrs, videoName, clientID, alpha)

#clientID = 'Chen_CQAS_DASH'
#cqas_dash(cache_agent, server_addrs, videoName, clientID)
