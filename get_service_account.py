import json

def get_service_account(authFile):
	jsonFile = open(authFile)
	authData = json.load(jsonFile)
	jsonFile.close()

	return authData["Account"]
