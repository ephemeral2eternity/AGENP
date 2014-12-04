'''
PING a server with count times and get the RTT list
'''
from subprocess import Popen, PIPE
import string
import re

# server_ip = '104.155.15.0'

def extract_number(s,notfound='NOT_FOUND'):
    regex=r'[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?'
    return re.findall(regex,s)

def getRTT(ip, count):
	'''
	Pings a host and return True if it is available, False if not.
	'''
	cmd = ['ping', '-c', str(count), ip]
	process = Popen(cmd, stdout=PIPE, stderr=PIPE)
	stdout, stderr = process.communicate()
	rttList = parsePingRst(stdout, count)
	# print rttList
	return rttList

def parsePingRst(pingString, count):
	rtts = []
	lines = pingString.splitlines()
	for i in range(1, count+1):
		curline = lines[i]
		# print curline
		curDataStr = curline.split(':', 2)[1]
		curData = extract_number(curDataStr)
		rtts.append(float(curData[-1]))
	return rtts

# if getRTT(server_ip, 5):
#	print '{} is available'.format(server_ip)
#else:
#	print '{} is not available'.format(server_ip)
