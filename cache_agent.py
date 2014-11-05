#!/usr/bin/python
 
# Copyright Jon Berg , turtlemeat.com
 

# Modified by nikomu @ code.google.com     
 

import string,cgi,time
import json
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os # os. path
 
CWD = os.path.abspath('.')
## print CWD
PORT = 8615     
UPLOAD_PAGE = 'upload.html' # must contain a valid link with address and port of the server
QoE = json.loads(open("./info/QoE.json").read())
agentID = "agenp-01"
delta = 0.5

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

def getQoE(qoePath):
    q = qoePath.split("?", 2)[1]
    return num(q)

# -----------------------------------------------------------------------
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:   
            if self.path == '/' :
                page = welcome_page()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(page)
                return

            elif self.path.startswith('/videos'):   
                page = make_index( self.path.replace('/videos', '../videos') )
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(page)
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

            elif self.path.startswith("/QoE?"):   #our dynamic content
                client_qoe = getQoE(self.path)
                update_qoe = client_qoe * delta + num(QoE[agentID]) * (1 - delta)
                QoE[agentID] = update_qoe
                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.send_header('Params', json.dumps(QoE))
                self.end_headers()
                self.wfile.write("Updated QoE is : " + str(update_qoe))
                return

            else : # default: just send the file     
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
        # global rootnode ## something remained in the orig. code     
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))     
            if ctype == 'multipart/form-data':
                # original version :     
                '''
                query=cgi.parse_multipart(self.rfile, pdict)
                upfilecontent = query.get('upfile')
                print "filecontent", upfilecontent[0] 

                '''
                # using cgi.FieldStorage instead, see 
                 # http://stackoverflow.com/questions/1417918/time-out-error-while-creating-cgi-fieldstorage-object     
                fs = cgi.FieldStorage( fp = self.rfile, 
                                        headers = self.headers, # headers_, 
                                        environ={ 'REQUEST_METHOD':'POST' } # all the rest will come from the 'headers' object,     
                                        # but as the FieldStorage object was designed for CGI, absense of 'POST' value in environ     
                                        # will prevent the object from using the 'fp' argument !     
                                      )
                ## print 'have fs'

            else: raise Exception("Unexpected POST request")
    
            fs_up = fs['upfile']
            filename = os.path.split(fs_up.filename)[1] # strip the path, if it presents     
            fullname = os.path.join(CWD, filename)
 

            # check for copies :     
            if os.path.exists( fullname ):     
                fullname_test = fullname + '.copy'
                i = 0
                while os.path.exists( fullname_test ):
                    fullname_test = "%s.copy(%d)" % (fullname, i)
                    i += 1
                fullname = fullname_test
                 
            if not os.path.exists(fullname):
                with open(fullname, 'wb') as o:
                    # self.copyfile(fs['upfile'].file, o)
                    o.write( fs_up.file.read() )     
 

            self.send_response(200)
 

            self.end_headers()
            
            self.wfile.write("<HTML><HEAD></HEAD><BODY>POST OK.<BR><BR>");
            self.wfile.write( "File uploaded under name: " + os.path.split(fullname)[1] );
            self.wfile.write(  '<BR><A HREF=%s>back</A>' % ( UPLOAD_PAGE, )  )
            self.wfile.write("</BODY></HTML>");

        except Exception as e:
            # pass
            print e
            self.send_error(404,'POST to "%s" failed: %s' % (self.path, str(e)) )

def main():
    try:
        server = HTTPServer(('', PORT), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
 
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
 

    main()
 