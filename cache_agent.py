#!/usr/bin/python
# Cache Agent in Agent based management and control system
# Chen Wang, chenw@cmu.edu
import subprocess 
import argparse
import string,cgi,time
import json
import ntpath
import sys
import urllib2
import sqlite3 as lite
import shutil
import operator
import requests
from gcs_upload import *
from get_cache_agents import *
from ping import *
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from apscheduler.schedulers.background import BackgroundScheduler
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os # os. path

## Import self-written libraries
from cache_content import *
from gce_authenticate import *
from provision import *
 
## Current Path
CWD = os.path.abspath('.')

## Global Varibles
PORT = 8615     
UPLOAD_PAGE = 'upload.html' # must contain a valid link with address and port of the server
# QoE = json.loads(open("./info/QoE.json").read())
QoE = {}
agentID = ""
peerAgents = []
delta = 0.5
previousBytes = -1
client_addrs = []
cached_videos = []
bwTrace = {}

## Global Variables for Database connection
con = None
cur = None

## Global variable to access GCE

def make_index( relpath ):     
    abspath = os.path.abspath(relpath) # ; print abspath
    flist = os.listdir( abspath ) # ; print flist
     
    rellist = []     
    for fname in flist :     
        # relname = os.path.join(relpath, fname)
        # rellist.append(relname)
        rellist.append(fname)
     
     # print rellist
    inslist = []     
    for r in rellist :     
        inslist.append( '<a href="%s">%s</a><br>' % (r,r) )
     
    # print inslist
     
    page_tpl = "<html><head></head><body>%s</body></html>"         
    ret = page_tpl % ( '\n'.join(inslist) , )
     
    return ret

def welcome_page():
    page = "<html>  \
                <title>  \
                    AGENP Cache Agent \
                </title> \
                <body>  \
                    <h1> Welcome!! </h1>\
                    <p>This is the cache agent in AGENS system </p>\
                    <p>You can use '/videos' to show all available videos in local cache! </p>\
                </body> \
            </html>"
    return page

def num(s):
        try:
                return int(s)
        except ValueError:
                return float(s)

def getQoE(params):
	qUpdates = {}
	for param in params:
		if '=' in param:
			items = param.split('=', 2)
			qUpdates[items[0]] = items[1]
	return qUpdates

def answerQoE(handler):
	global QoE
	handler.send_response(200)
	handler.send_header('Content-type', 'text/html')
	handler.send_header('Params', json.dumps(QoE))
	handler.end_headers()
	handler.wfile.write("Updated QoE is: " + json.dumps(QoE))

def updateQoE(handler, params):
	global QoE, con, cur
	if len(params) >= 2:
		qupdates = getQoE(params)
		for s in qupdates.keys():
        		QoE[s] = num(qupdates[s]) * delta + QoE[s] * (1 - delta)
			print "[AGENP] Updated QoE is : " + str(QoE[s]) + " for server " + s
    		try:
			connection = lite.connect('agens.db')
			cur = connection.cursor()
			for s in qupdates.keys():
				cur.execute("UPDATE QoE SET QoE=? WHERE Name=?", (QoE[s], s))
				connection.commit()
			connection.close()
    		except lite.Error, e:
			if connection:
				connection.rollback()
			print "SQLITE DB Error %s" % e.args[0]
	answerQoE(handler)

def addOverlayPeer(handler, cmdStr):
	global agentID, peerAgents
	params = cmdStr.split('&')
	for param in params:
		if '=' in param:
			items = param.split('=', 2)
			peerAgents.append(items[1])
	answerOverlayQuery(handler)

def answerOverlayQuery(handler):
	global agentID, peerAgents
	handler.send_response(200)
	handler.send_header('Content-type', 'text/html')
	handler.send_header('Params', {'Peers': peerAgents})
	handler.end_headers()
	outHtml = "<h2>The peers of agent " + agentID + "</h2><ul>"
	for peer in peerAgents:
		outHtml = outHtml + "<li>" + peer + "</li>"
	outHtml = outHtml + "</ul>"
	handler.wfile.write(outHtml)

def queryVideos(handler):
	global cached_videos
    	update_cached_videos()
	handler.send_response(200)
	handler.send_header('Content-type', 'text/html')
	handler.send_header('Params', str(cached_videos))
	handler.end_headers()
	cached_video_page = "<h2>Locally cached videos: </h2><ul>"

	for video in cached_videos:
		cached_video_page = cached_video_page + "<li>" + video + "</li>"

	cached_video_page = cached_video_page + "</ul>"

	handler.wfile.write(cached_video_page)

def cacheVideos(handler, cmdStr):
	global cached_videos
	params = cmdStr.split('&')
	to_cache = []
	for video in params:
		if 'cache' not in video:
			if video not in cached_videos:
				to_cache.append(video)
				cache_content(video)
				cached_videos.append(video)
			else:
				print video + " is cached locally!"

	if to_cache:	
		video_cache_page = "<h2>Starts caching videos: </h2><ul>"
		for v in to_cache:
			video_cache_page = video_cache_page + "<li>" + video + "</li>"
		video_cache_page = video_cache_page + "</ul>"
	else:
		video_cache_page = "<h2>Videos already cached!</h2>"
	handler.send_response(200)
	handler.send_header('Content-type', 'text/html')
	handler.end_headers()
	handler.wfile.write(video_cache_page)

def deleteVideos(handler, cmdStr):
	global cached_videos
	params = cmdStr.split('&')
	for video in params:
		if "delete" not in video:
			print "delete locally cached video ", video
			if video in cached_videos:
				try:
					subprocess.Popen(["rm", "-r", "-f", "../videos/"+ video])
				except:
					failPage = "<h2>Fail to delete video " + video + "<h2>"
					handler.send_response(200)
					handler.send_header('Content-type', 'text/html')
					handler.end_headers()
					handler.wfile.write(failPage)
		
				successPage = "<h2>Successfully delete video: " + video + "<h2>"
				handler.send_response(200)
				handler.send_header('Content-type', 'text/html')
				handler.end_headers()
				handler.wfile.write(successPage)
				cached_videos.remove(video)
			else:
				errPage = "<h2>Wrong Video to delete: " + video + "<h2>"
				handler.send_response(200)
				handler.send_header('Content-type', 'text/html')
				handler.end_headers()
				handler.wfile.write(errPage)

# -----------------------------------------------------------------------
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
	    if "ico" in self.command:
		return

            elif self.path == '/' :
                page = welcome_page()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(page)
                return

	    ## Processing requests related to locally cached videos 
            elif self.path.startswith('/videos'):
		if '?' in self.path:
			cmdStr = self.path.split('?', 2)[1]
			if 'query' in cmdStr:
				print "Query local cached videos"
				queryVideos(self)
			elif 'cache' in cmdStr:
				print "cache a new video"
				cacheVideos(self, cmdStr)
			elif 'delete' in cmdStr:
				deleteVideos(self, cmdStr)
			else:
				print "[AGENP]Wrong videos command"
				print "Please try videos?query, delete, cache!"
		else:
                	page = make_index( self.path.replace('/videos', '../videos') )
                	self.send_response(200)
                	self.send_header('Content-type', 'text/html')
                	self.end_headers()
                	self.wfile.write(page)
                return

	    ## Processing requests related to QoE
            elif self.path.startswith("/QoE?"):   #our dynamic content
		contents = self.path.split('?', 2)[1]
		params = contents.split('&')
		if 'query' in contents:
			print "[AGENP] Receive QoE query message!"
                	answerQoE(self)
		elif 'update' in contents:
			print "[AGENP] Receive QoE update message!"
			updateQoE(self, params)
		return

	    ## Processing requests related to Ring Overlay
	    elif self.path.startswith('/overlay?'):
		cmdStr = self.path.split('?', 2)[1]
		if 'query' in cmdStr:
			answerOverlayQuery(self)
		#if 'update' in cmdStr:
		#	answerOverlayUpdate(self, cmdStr)
		if 'add' in cmdStr:
			addOverlayPeer(self, cmdStr)
		return

            elif self.path.endswith(".html"):
                ## print curdir + sep + self.path
                f = open(curdir + sep + self.path)
                #note that this potentially makes every file on your computer readable by the internet
                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
                
            elif self.path.endswith(".esp"):   #our dynamic content
                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write("hey, today is the " + str(time.localtime()[7]))
                self.wfile.write(" day in the year " + str(time.localtime()[0]))
                return

            else :
		# Get client addresses
		client_addr = self.client_address[0]
		if client_addr not in client_addrs:
			client_addrs.append(client_addr)
 
		# default: just send the file     
                # filepath = self.path[1:] + '/videos/' # remove leading '/'
                filepath = '../videos' + self.path
                fileSz = os.path.getsize(filepath)
                f = open( os.path.join(CWD, filepath), 'rb' )
                #note that this potentially makes every file on your computer readable by the internet
                self.send_response(200)
                self.send_header('Content-type',    'application/octet-stream')
                self.send_header('Content-Length', str(fileSz))
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            return # be sure not to fall into "except:" clause ?       

        except IOError as e :  
             # debug     
             print e
             self.send_error(404,'File Not Found: %s' % self.path)

    def do_POST(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write("<HTML><HEAD></HEAD><BODY>POST OK.<BR><BR>");
            self.wfile.write( "File uploaded under name: " + os.path.split(fullname)[1] );
            self.wfile.write(  '<BR><A HREF=%s>back</A>' % ( UPLOAD_PAGE, )  )
            self.wfile.write("</BODY></HTML>");

# ================================================================================
# Read outbound bytes in 5 seconds. 
# ================================================================================
def get_tx_bytes():
	file_txbytes = open('/sys/class/net/eth0/statistics/tx_bytes')
	lines = file_txbytes.readlines()
	tx_bytes = int(lines[0])
	return tx_bytes

# ================================================================================
# Monitor outbound traffic every 5 seconds. 
# ================================================================================
def bw_monitor():
	global previousBytes, bwTrace, agentID, con
	if previousBytes < 0:
		previousBytes = get_tx_bytes()
	else:
		curBytes = get_tx_bytes()
		out_bw = (curBytes - previousBytes)/5
		previousBytes = curBytes
		print "[AGENP-Monitoring]Outbound bandwidth is " + str(out_bw) + " bytes/second!"

		## Record the bw in bwTraces and dump it per hour 60 * 60 / 5 = 720
		curTS = time.time()

		# Save TS to the database
    		try:
			connection = lite.connect('agens.db')
			cur = connection.cursor()
			cur.execute('''INSERT INTO BW(TS, BW) VALUES(?, ?)''', (int(curTS), out_bw))
			connection.commit()
			connection.close()
    		except lite.Error, e:
			if connection:
				connection.rollback()
			print "SQLITE DB Error %s" % e.args[0]		

		# Save TS to google cloud
		bwTrace[curTS] = out_bw
		if len(bwTrace) >= 720:
			bwTraceFile = "./data/" + agentID + "-bw-" + str(int(curTS)) + ".json"
			with open(bwTraceFile, 'w') as outfile:
				json.dump(bwTrace, outfile, sort_keys = True, indent = 4, ensure_ascii = False)

		# Upload the bwTrace file to google cloud
		bucketName = "agens-data"
		gcs_upload(bucketName, bwTraceFile)

		# Client bwTrace buffer
		bwTrace = {}

		# Delete local bwTrace file
		shutil.rmtree(bwTraceFile)

# ================================================================================
# Monitor user demand on a cache agent. 
# User demand is measured by the number of unique flows connecting to the same 
# cache agent in 1 minutes.
# ================================================================================
def demand_monitor():
	global client_addrs, con
	demand = len(client_addrs)
	print "[AGENP-Monitoring] There are " + str(len(client_addrs)) + \
		" clients connecting to this server in last 1 minutes."
	
	## Record the user demand per 1 minute
	curTS = time.time()

	# Save TS to the database
    	try:
		connection = lite.connect('agens.db')
		cur = connection.cursor()
		cur.execute('''INSERT INTO DEMAND(TS, USERNUM) VALUES(?, ?)''', (int(curTS), demand))
		connection.commit()
		connection.close()
    	except lite.Error, e:
		if connection:
			connection.rollback()
		print "SQLITE DB Error %s" % e.args[0]
		
	print "==================================================="
	for client in client_addrs:
		print client
	print "==================================================="
	# Clear client agents to empty
	client_addrs[:] = []
	

# ================================================================================
# Show locally cached videos for current cache agent. 
# ================================================================================
def update_cached_videos():
    global cached_videos
    cached_videos = []
    abspath = os.path.abspath("../videos/") # ; print abspath
    dirs = filter(os.path.isdir, [os.path.join(abspath, f) for f in os.listdir(abspath)]) # ; print flist
    print "Locally cached videos are: ", dirs
    for video in dirs:
	cached_videos.append(ntpath.basename(video))

# ================================================================================
# Get Current Agent ID from its external IP address
# ================================================================================
def getAgentID():
    cache_agents = get_cache_agents()
    cur_ip = getIPAddr()
    agent_id = ""

    for agent in cache_agents:
	if cur_ip in agent.public_ips:
		agent_id = agent.name
		break

    return agent_id

# ================================================================================
# Try to add current node as a peer to an existing available node
# Inputs:
# 	name: existing node's name (agentID)
# 	ip: existing node's ip address
# Return:
#	True: successfull. False: failed.
# ================================================================================
def add_peer(name, ip):
  global agentID, PORT, peerAgents
  try:
	r = requests.get("http://" + ip + ":" + str(PORT) + "/overlay?add&peer=" + agentID)
	peerAgents.append(name)
	return True
  except requests.ConnectionError, e:
	return False

# ================================================================================
# Add closest available agents as the peer agent
# ================================================================================
def addPeerAgents():
   global agentID, peerAgents
   agent_ips = get_cache_agent_ips()

   ## Ping all other agents
   peer_rtts = {}
   for agent in agent_ips.keys():
	if agent != agentID:
		rtt = getRTT(agent_ips[agent], 5)
		mnRtt = sum(rtt) / float(len(rtt))
		peer_rtts[agent] = mnRtt

   ## Sort all peers by rtts to them
   sorted_peers = sorted(peer_rtts.items(), key=operator.itemgetter(1))
   print sorted_peers

   ## Try to add a peer from the closest one
   for peer in sorted_peers:
	if add_peer(peer[0], agent_ips[peer[0]]):
		break
	
# ================================================================================
# Initialize the global variables with input arguments
# @argv: system inpute arguments
# ================================================================================
def initialize():
    global agentID, PORT, peerAgents, delta
    # Parse the input arguments
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--agentID", help="The agent ID of current agent!")
    # parser.add_argument("--port", type=int, help="The port number the agent is running on!")
    # parser.add_argument("--peers", nargs='+', help="The peer agent!")
    # parser.add_argument("--delta", type=float, help="The delta coefficient to forget previous QoE observations!")
    # args = parser.parse_args()
    # if args.agentID:
    #	agentID = args.agentID
    # if args.port:
    #	PORT = args.port
    # if args.peers:
    #	peerAgents = args.peers
    # if args.delta:
    #    delta = args.delta
    agentID = getAgentID()
    addPeerAgents()
    print "Agent ID: ", agentID
    print "Listening Port: ", str(PORT)
    print "Peer Agents: ", peerAgents
    print "Forgetting Coefficient: ", str(delta) 

    # Update what have been cached locally
    update_cached_videos()

    # Initialize Database
    initializeDB()

# ================================================================================
# Get external IP address of current agent
# ================================================================================
def getIPAddr():
	data = json.loads(urllib2.urlopen("http://ip.jsontest.com/").read())
	return data["ip"]

# ================================================================================
# Initialize the sqllite database
# ================================================================================
def initializeDB():
    global driver, con, cur, agentID, PORT, cached_videos, QoE
    agent_ips = get_cache_agent_ips()
    curIP = agent_ips[agentID]
    curAgents = []
    curQoE = []
    curAgents.append((agentID, curIP, PORT))
    curQoE.append((agentID, curIP, 5.0))
    for key, value in agent_ips.iteritems():
	if key is not agentID:
		curAgents.append((key, value, PORT))
		curQoE.append((key, value, 4.0))
		QoE[key] = 4.0
    QoE[agentID] = 5.0

    try:
	con = lite.connect('agens.db')
	cur = con.cursor()
	## The format of all tables in agens.db
	cur.execute("CREATE TABLE Agents(Name TEXT, Addr TEXT, port INT)")
	cur.execute("CREATE TABLE QoE(Name TEXT, Addr TEXT, QoE REAL)")
	cur.execute("CREATE TABLE BW(TS INT, BW INT)")
	cur.execute("CREATE TABLE DEMAND(TS INT, USERNUM INT)")
	cur.executemany("INSERT INTO Agents VALUES(?, ?, ?)", curAgents)
	cur.executemany("INSERT INTO QoE VALUES(?, ?, ?)", curQoE)
	con.commit()
	con.close()
    except lite.Error, e:
	if con:
		con.rollback()
	print "SQLITE DB Error %s" % e.args[0]

#==========================================================================================
# Main Function of Cache Agent
#==========================================================================================
def main(argv):
    initialize()
    try:
	sched = BackgroundScheduler()
	sched.add_job(bw_monitor, 'interval', seconds=5)
	sched.add_job(demand_monitor, 'interval', minutes=1)
	sched.start()

        server = HTTPServer(('', PORT), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
 
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()
	sched.shutdown()
	# con.close()

if __name__ == '__main__':
    main(sys.argv)
 
