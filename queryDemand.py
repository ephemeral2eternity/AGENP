import sqlite3 as lite

agentID = "agens-02"

try:
	con = lite.connect('agens.db')
	cur = con.cursor()

	## Query the user demand from agens.db table
	cur.execute("SELECT * FROM DEMAND")
	demandData = cur.fetchall()

	## Write data to an outfile
	with open("./data/"+ agentID + "-demand.dat", 'w') as outfile:
		outfile.writelines(["%s, %s\n" % (item[0], item[1]) for item in demandData])

	con.close()
except lite.Error, e:
	if con:
		con.rollback()
	print "SQLITE DB Error %s" % e.args[0]
