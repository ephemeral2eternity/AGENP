from mpd_parser import *

# Server Name
server_address = 'ec2-54-76-42-64.eu-west-1.compute.amazonaws.com'
videoName = 'st'

reps = mpd_parser(server_address, videoName)

for item in reps:
	print item
