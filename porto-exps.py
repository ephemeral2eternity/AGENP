# Script to run experiments from INESC-Porto client
from test_client_agent import *

port = 8615
video = 'BBB'

# Experiment 1: two candidate servers within the same zone in the same region
candidates = ['agens-04', 'agens-05']
clientID = 'porto-exp1'
test_client_agent(clientID, candidates, port, video)

# Experiment 2: two candidate servers within the same regions in the different zones
candidates = ['agens-04', 'agens-06']
clientID = 'porto-exp2'
test_client_agent(clientID, candidates, port, video)

# Experiment 3: two candidate servers in different regions
candidates = ['agens-05', 'agens-07']
clientID = 'porto-exp3'
test_client_agent(clientID, candidates, port, video)

# Experiment 4: two candidate servers within the same regions remotely
candidates = ['agens-08', 'agens-09']
clientID = 'porto-exp4'
test_client_agent(clientID, candidates, port, video)

# Experiment 5: two candidate servers within different regions remotely
candidates = ['agens-01', 'agens-09']
clientID = 'porto-exp5'
test_client_agent(clientID, candidates, port, video)

# Experiment 6: two candidate servers in the different regions, one locally and the other remotely
candidates = ['agens-02', 'agens-06']
clientID = 'porto-exp6'
test_client_agent(clientID, candidates, port, video)

# Experiment 7: two candidate servers within the same remote region
candidates = ['agens-02', 'agens-03']
clientID = 'porto-exp7'
test_client_agent(clientID, candidates, port, video)

# Experiment 2: two candidate servers within different remote regions
candidates = ['agens-03', 'agens-08']
clientID = 'porto-exp8'
test_client_agent(clientID, candidates, port, video)
