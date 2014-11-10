# Test client agent file, client_agent.py

from client_agent import *

cache_agent = 'agenp-01'
server_addrs = {}
server_addrs['agenp-01'] = '130.211.49.19:8615'
server_addrs['agenp-02'] = '130.211.118.248:8615'
videoName = 'BBB'
clientID = 'Chen'

client_agent(cache_agent, server_addrs, videoName, clientID)
