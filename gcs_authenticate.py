from service_account import service_account as SA
import os

def gcs_authenticate(authFile):
	# Create a service account object
	# serviceAccount = SA(authFile)

	# Activate a service account
	#cmdStr = "gcloud auth activate-service-account " + serviceAccount.account + " --key-file " + serviceAccount.secret
	os.system(cmdStr)

