from ping import *

server1 = '104.155.15.0'
server2 = '130.211.108.80'

rtt1 = getRTT(server1, 5)
mnRTT1 = sum(rtt1) / float(len(rtt1))
rtt2 = getRTT(server2, 5)
mnRTT2 = sum(rtt2) / float(len(rtt2))

print "Mean RTT for ", server1, " is ", mnRTT1, " ms"
print "Mean RTT for ", server2, " is ", mnRTT2, " ms"

