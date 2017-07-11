# This is a service script to setup a test ambient on a neo4j database.
# The test database will just contain 100 :Target nodes each of them with
# name and geneid properties.

from neo4j.v1 import GraphDatabase, basic_auth
from builtins import input
import json
import getpass

if __name__ == "__main__":

	# get neo4j server credentials
	server = input("insert n4j server address (default: bolt://localhost:7687): ")
	if server == '':
		server = "bolt://localhost:7687"
		print("Server set to default")
	user = input("insert user name: ")
	pwd = getpass.getpass("insert password: ")

	# set neo4j session
	driverLocal = GraphDatabase.driver(server, auth=basic_auth(user, pwd))
	sessionLocal = driverLocal.session()
	print("local connection done.")

	# leggo il file json in cui ho salvato una parte dei nodi target di DIANA
	jsonFile = open("TargetDump2.json")
	targetNodes = json.load(jsonFile)
	jsonFile.close()
	
	# insert nodes from json file to local db
	# create all the single queries
	queries = ["CREATE (:Target {name: \""+ str(t["row"][0]["name"]) +"\", geneid: \""+ str(t["row"][0]["geneid"]) +"\"}) " for t in targetNodes["data"]]
	
	# execute in blocks of 200 queries
	start = 0
	stop = 0
	count = 0
	while stop < len(queries):
		thisQuery = ""
		start = stop
		stop += 200
		count += len(queries[start:stop])
		for q in queries[start:stop]:
			thisQuery += q
		sessionLocal.run(thisQuery)
		print(str(count) + " of " + str(len(queries)) + " Targets added ...")
	print("All done.")
	
	sessionLocal.close()