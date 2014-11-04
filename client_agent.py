# The client agent code
# Client agent is responsible for: downloading the video chunk, play it, monitor QoE and
# switch bitrate, switch server if QoE is not good enough
# @author : chenw@andrew.cmu.edu
import time
import datetime
from operator import itemgetter
from mpd_parser import *
from download_chunk import *

def findRep(sortedVidBWS, est_bw_val):
	for i in range(len(sortedVidBWS)):
		if sortedVidBWS[i][1] > est_bw_val:
			j = i -1
			break
		else:
			j = i
	repID = sortedVidBWS[j][0]
	return repID

server_addr = '130.211.49.19'
videoName = 'st'

rsts = mpd_parser(server_addr, videoName)
vidLength = int(rsts['mediaDuration'])
minBuffer = rsts['minBufferTime']
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
chunkLen = int(reps[minID]['length'])
chunkNext = int(reps[minID]['start'])

# Start downloading video and audio chunks
curBuffer = 0
chunk_download = 0
loadTS = time.time()
print "[AGENP] Start downloading video at " + datetime.datetime.fromtimestamp(int(loadTS)).strftime("%Y-%m-%d %H:%M:%S")
achunk_sz = download_chunk(server_addr, videoName, audioInit)
vchunk_sz = download_chunk(server_addr, videoName, vidInit)
startTS = time.time()
print "[AGENP] Start playing video at " + datetime.datetime.fromtimestamp(int(startTS)).strftime("%Y-%m-%d %H:%M:%S")
est_bw = (achunk_sz + vchunk_sz) * 8 / (startTS - loadTS)
print "[AGENP] Estimated bandwidth is : " + str(est_bw)
preTS = startTS
chunk_download += 1
curBuffer += chunkLen

while ((chunkNext + 1) * chunkLen < vidLength * timescale) :
	nextRep = findRep(sortedVids, est_bw)
	vidChunk = reps[nextRep]['name'].replace('$Number$', str(chunkNext))
	auChunk = reps[audioID]['name'].replace('$Number$', str(chunkNext))
	print "[AGENP] Download chunk: #" + str(chunkNext) + " at representation " + nextRep
	achunk_sz = download_chunk(server_addr, videoName, auChunk)
	vchunk_sz = download_chunk(server_addr, videoName, vidChunk)
	curTS = time.time()
	est_bw = (achunk_sz + vchunk_sz) * 8 / (curTS - preTS)
	print "[AGENP] Received chunk # " + str(chunkNext) + " at " + datetime.datetime.fromtimestamp(int(curTS)).strftime("%H:%M:%S")
	print "[AGENP] Estimated bandwidth is : " + str(est_bw)
	time_elapsed = curTS - preTS
	if time_elapsed > curBuffer:
		freezingTime = time_elapsed - curBuffer
		curBuffer = 0
		print "[AGENP] Client freezes for " + str(freezingTime)
	else:
		freezingTime = 0
		curBuffer = curBuffer - time_elapsed

	# Compute QoE of a chunk here

	# Update iteration information
	curBuffer = curBuffer + chunkLen
	preTS = curTS
	chunk_download += 1
	chunkNext += 1
