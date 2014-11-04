import os
import requests
import re
import xml.etree.ElementTree as ET

def num(s):
	try:
		return int(s)
	except ValueError:
		return float(s)

def mpd_parser(server_address, videoName):

	# server_address = 'ec2-54-76-42-64.eu-west-1.compute.amazonaws.com'
	# videoName = 'st'
	mpdFile = 'stream.mpd'

	url = 'http://' + server_address + '/' + videoName + '/' + mpdFile
	r = requests.get(url)
	mpdString = str(r.content)
	# print mpdString

	representations = {}

	root = ET.fromstring(mpdString)
	mediaLength = num(root.get('mediaPresentationDuration')[2:-1])
	minBufferTime = num(root.get('minBufferTime')[2:-1])
	for period in root:
		for adaptSet in period: 
			for rep in adaptSet:
				repType = rep.get('mimeType')
				repID = rep.get('id')
				repBW = rep.get('bandwidth')
				for seg in rep:
					initSeg = seg.get('initialization')
					segName = seg.get('media')
					segStart = seg.get('startNumber')
					segLength = seg.get('duration')
					timescale = seg.get('timescale')
				representations[repID] = dict(mtype=repType, name=segName, bw=repBW, initialization=initSeg, start=segStart, length=segLength, timescale=timescale)

	# for item in representations:
	#	print item

	return {'representations' : representations, 'mediaDuration':mediaLength, 'minBufferTime': minBufferTime}
