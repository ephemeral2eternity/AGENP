# The client agent code
# Client agent is responsible for: downloading the video chunk, play it, monitor QoE and
# switch bitrate, switch server if QoE is not good enough
# @author : chenw@andrew.cmu.edu
import time
import datetime
import shutil
import math
import json
import requests
from operator import itemgetter
from mpd_parser import *
from download_chunk import *

def findRep(sortedVidBWS, est_bw_val, bufferSz, minBufferSz):
	for i in range(len(sortedVidBWS)):
		if sortedVidBWS[i][1] > est_bw_val:
			j = max(i - 1, 0)
			break
		else:
			j = i

	if bufferSz < minBufferSz:
		j = max(j-1, 0)
	elif bufferSz > 20:
		j = min(j + 1, len(sortedVidBWS) - 1)
	
	repID = sortedVidBWS[j][0]
	return repID

def computeQoE(freezing_time, cur_bw, max_bw):
	delta = 0.5
	a = [1.3554, 40]
	b = [5.0, 6.3484, 4.4, 0.72134]
	q = [5.0, 5.0]

	if freezing_time > 0:
		q[0] = b[0] - b[1] / (1 + math.pow((b[2]/freezing_time), b[3]))

	q[1] = a[0] * math.log(a[1]*cur_bw/max_bw)

	qoe = delta * q[0] + (1 - delta) * q[1]
	return qoe

def num(s):
        try:
                return int(s)
        except ValueError:
                return float(s)

def averageQoE(client_trace):
	mn_QoE = 0
	if len(client_trace) < 5:
		for chunk_tr in client_trace:
			mn_QoE += client_trace[chunk_tr]["QoE"]
		mn_QoE = mn_QoE / len(client_trace)
	else:
		for chunk_tr in client_trace.keys()[-5:]:
			mn_QoE += client_trace[chunk_tr]["QoE"] / 5
	return mn_QoE

# ================================================================================
# Query cache agent about how it observes user experiences with all servers
# @input : cache_agent --- The cache agent the user is closest to
# @return: qoe_vector --- QoEs of all servers observed from cache_agent
# ================================================================================
def query_QoE(cache_agent):
	r = requests.get("http://" + cache_agent + "/QoE?query")
	qoe_vector = json.loads(r.headers['Params'])
	return qoe_vector

# ================================================================================
# Upload user experiences with a candidate server to cache agent
# @input : cache_agent --- The cache agent the user is closest to
#	   qoe --- User quality experiences with server denoted by server_name over
#		   5 chunks
#	   server_name --- the name of the server the user is downloading chunks from
# @return: qoe_vector --- QoEs of all servers observed from cache_agent
# ================================================================================
def update_QoE(cache_agent, qoe, server_name):
	r = requests.get("http://" + cache_agent + "/QoE?update&" + "q=" + str(qoe) + "&s=" + server_name)
	qoe_vector = json.loads(r.headers['Params'])
	return qoe_vector

# ================================================================================
# Read candidate server QoE from QoE vectors
# @input : qoe_vector --- QoE Vector obtained from cache agent
#	   server_addrs --- Candidate servers {name:ip} to download a videos
# @return: srv_qoe --- QoEs of candidate servers {srv:qoe}
# ================================================================================
def get_server_QoE(qoe_vector, server_addrs):
	srv_qoe = {}
	for srv_name in server_addrs.keys():
		if srv_name not in qoe_vector.keys():
			print "[AGENP-ERROR] Input server name " + srv_name + " does not exist!!!"
			sys.exit(1)
		srv_qoe[srv_name] = qoe_vector[srv_name]
	return srv_qoe
	
# ================================================================================
# Client agent to play the video
# @input : cache_agent --- Cache agent that is closest to the client
#	   server_addrs --- Candidate servers {name:ip} to download a videos
#	   videoName --- The name of the video the user is requesting
#	   clientID --- The ID of client.
# ================================================================================
def client_agent(cache_agent, server_addrs, videoName, clientID):
	# Initialize servers' qoe
	cache_agent_ip = server_addrs[cache_agent]
	qoe_vector = query_QoE(cache_agent_ip)
	server_qoes = get_server_QoE(qoe_vector, server_addrs)

	# Selecting a server with maximum QoE
	selected_srv = max(server_qoes.iteritems(), key=operator.itemgetter(1))[0]
	selected_srv_ip = server_addrs[selected_srv]

	rsts = mpd_parser(selected_srv, videoName)
	vidLength = int(rsts['mediaDuration'])
	minBuffer = num(rsts['minBufferTime'])
	reps = rsts['representations']

	vidBWs = {}

	for rep in reps:
		if not 'audio' in rep:
			vidBWs[rep] = int(reps[rep]['bw'])		
		else:
			audioID = rep
			audioInit = reps[rep]['initialization']
			start = reps[rep]['start']
			audioName = reps[rep]['name']

	sortedVids = sorted(vidBWs.items(), key=itemgetter(1))

	minID = sortedVids[0][0]
	vidInit = reps[minID]['initialization']
	maxBW = sortedVids[-1][1]

	# Read common parameters for all chunks
	timescale = int(reps[minID]['timescale'])
	chunkLen = int(reps[minID]['length']) / timescale
	chunkNext = int(reps[minID]['start'])

	# Start downloading video and audio chunks
	curBuffer = 0
	chunk_download = 0
	loadTS = time.time()
	print "[AGENP] Start downloading video " + videoName + " at " + datetime.datetime.fromtimestamp(int(loadTS)).strftime("%Y-%m-%d %H:%M:%S")
	achunk_sz = download_chunk(selected_srv_ip, videoName, audioInit)
	vchunk_sz = download_chunk(selected_srv_ip, videoName, vidInit)
	startTS = time.time()
	print "[AGENP] Start playing video at " + datetime.datetime.fromtimestamp(int(startTS)).strftime("%Y-%m-%d %H:%M:%S")
	est_bw = (achunk_sz + vchunk_sz) * 8 / (startTS - loadTS)
	# print "[AGENP] Estimated bandwidth is : " + str(est_bw) + " at chunk #init"
	print "|-- Chunk # --|- Representation -|-- QoE --|-- Buffer --|-- Freezing --|"
	preTS = startTS
	chunk_download += 1
	curBuffer += chunkLen

	client_tr = {}

	while ((chunkNext + 1) * chunkLen < vidLength) :
		nextRep = findRep(sortedVids, est_bw, curBuffer, minBuffer)
		vidChunk = reps[nextRep]['name'].replace('$Number$', str(chunkNext))
		auChunk = reps[audioID]['name'].replace('$Number$', str(chunkNext))
		loadTS = time.time();
		# print "[AGENP] Download chunk: #" + str(chunkNext) + " at representation " + nextRep
		achunk_sz = download_chunk(selected_srv_ip, videoName, auChunk)
		vchunk_sz = download_chunk(selected_srv_ip, videoName, vidChunk)
		curTS = time.time()
		est_bw = (achunk_sz + vchunk_sz) * 8 / (curTS - loadTS)
		# print "[AGENP] Received chunk # " + str(chunkNext) + " at " + datetime.datetime.fromtimestamp(int(curTS)).strftime("%H:%M:%S")
		# print "[AGENP] Estimated bandwidth is : " + str(est_bw) + " at chunk #" + str(chunkNext)
		# print "[AGENP] Current Buffer Size : " + str(curBuffer)
		time_elapsed = curTS - preTS
		# print "[AGENP] Time Elapsed when downloading :" + str(time_elapsed)
		if time_elapsed > curBuffer:
			freezingTime = time_elapsed - curBuffer
			curBuffer = 0
			# print "[AGENP] Client freezes for " + str(freezingTime)
		else:
			freezingTime = 0
			curBuffer = curBuffer - time_elapsed

		# Compute QoE of a chunk here
		curBW = num(reps[nextRep]['bw'])
		chunk_QoE = computeQoE(freezingTime, curBW, maxBW)
		# print "[AGENP] Current QoE for chunk #" + str(chunkNext) + " is " + str(chunk_QoE)
		print "|---", str(chunkNext), "---|---", nextRep, "---|---", str(chunk_QoE), "---|---", str(curBuffer), "---|---", str(freezingTime), "---|"
		
		client_tr[chunkNext] = dict(Representation=nextRep, QoE=chunk_QoE, Buffer=curBuffer, Freezing=freezingTime)

		# Count Previous QoE average
		if chunkNext%5 == 0:
			mnQoE = averageQoE(client_tr)
			qoe_vector = update_QoE(cache_agent_ip, selected_srv, mnQoE)
			server_qoes = get_server_QoE(qoe_vector, server_addrs)
			# Selecting a server with maximum QoE
			selected_srv = max(server_qoes.iteritems(), key=operator.itemgetter(1))[0]
			selected_srv_ip = server_addrs[selected_srv]
			print "[AGENP] Received Server QoE is :" + json.dumps(server_qoe)

		# Update iteration information
		curBuffer = curBuffer + chunkLen
		if curBuffer > 30:
			time.sleep(chunkLen)
		preTS = curTS
		chunk_download += 1
		chunkNext += 1

	trFileName = "./data/" + clientID + "-" + videoName + "-" + str(time.time()) + ".json"
	with open(trFileName, 'w') as outfile:
		json.dump(client_tr, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

	shutil.rmtree('./tmp')
	os.system('gsutil cp ' + trFileName + ' gs://agens-data/')
