# Testing the file of gs_upload.py
# chenw@cmu.edu
from gs_upload import *

authFile = "./info/gsAuth.json"
bucketName = "agens-data"
fPath = "./data/chenw.txt"

gs_upload(authFile, bucketName, fPath)
