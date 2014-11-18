import json

class service_account:
	def __init__(self, authFile=None):
		self.authFile = authFile
		if authFile:
			self.authData = json.load(open(authFile))
			self.account = self.authData["Account"]
			self.secret = self.authData["Secret"]
			self.project = self.authData["Project"]
		else:
			self.authData = None
			self.account = None
			self.secret = None
			self.project = None
