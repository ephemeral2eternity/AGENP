import os
import requests
import xml.etree.ElementTree as ET

server_address = 'ec2-54-76-42-64.eu-west-1.compute.amazonaws.com'
videoName = 'BBB'
mpdFile = 'stream.mpd'

url = 'http://' + server_address + '/' + videoName + '/' + mpdFile
r = requests.get(url)
mpdString = str(r.content)
print mpdString

root = ET.fromstring(mpdString)
for rep in root.iter('Representation'):
	print rep
	repID = rep.get('id')
