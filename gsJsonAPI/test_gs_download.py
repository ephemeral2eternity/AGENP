# Testing the gs_download.py
# @author: Chen Wang, chenw@cmu.edu
from gs_download import *

authFile = "./info/auth.json"
bucketName = 'agens-data'
objectName = 'BBB/stream.mpd'
filePath = "./info/"

gs_download(authFile, bucketName, objectName, filePath)
