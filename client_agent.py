# The client agent code
# Client agent is responsible for: downloading the video chunk, play it, monitor QoE and
# switch bitrate, switch server if QoE is not good enough
# @author : chenw@andrew.cmu.edu
import time
import datetime
import shutil
import math
import json
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
		j = min(j + 1, len(sortedVidBWS))
	
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

# server_addr = '130.211.49.19'
# videoName = 'st'
# clientID = 'Chen'

def client_agent(server_addr, videoName, clientID):
	rsts = mpd_parser(server_addr, videoName)
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
	achunk_sz = download_chunk(server_addr, videoName, audioInit)
	vchunk_sz = download_chunk(server_addr, videoName, vidInit)
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
		achunk_sz = download_chunk(server_addr, videoName, auChunk)
		vchunk_sz = download_chunk(server_addr, videoName, vidChunk)
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
