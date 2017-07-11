# This is the main module to integrate pathways and diseases into the DIANA database

from neo4j.v1 import GraphDatabase, basic_auth, AuthError
from builtins import input
from BioParsingKegg import getEntry, getPathwayList, getDiseaseList
from dataEntry import insertPathway, insertDisease
import json
import getpass
import time
current_milli_time = lambda: int(round(time.time() * 1000))

print("This script will get pathways and diseases from kegg to DIANA's n4j database.")
# richiedi informazioni del server n4j
server = input("insert n4j server address (default: bolt://localhost:7687): ")
if server == '':
	server = "bolt://localhost:7687"
	print("Server set to default")
user = input("insert user name: ")
pwd = getpass.getpass("insert password: ")

# set neo4j session
try:
	driverLocal = GraphDatabase.driver(server, auth=basic_auth(user, pwd))
except AuthError:
	print("Wrong credentials. Bye.")
	exit()

sessionLocal = driverLocal.session()
print("n4j connection ok")

# need to insert pathways?
needPathways = 0
while needPathways != 'y' and needPathways != 'Y' and needPathways != 'n' and needPathways != 'N':
	needPathways = input("Do you want to insert pathways in your db? [y/n]: ")

if needPathways == 'y' or needPathways == 'Y':
	needPathways = True
else:
	needPathways = False

# need to insert diseases?
needDiseases = 0
while needDiseases != 'y' and needDiseases != 'Y' and needDiseases != 'n' and needDiseases != 'N':
	needDiseases = input("Do you want to insert diseases in your db? [y/n]: ")

if needDiseases == 'y' or needDiseases == 'Y':
	needDiseases = True
else:
	needDiseases = False
	
# need to insert DB_INFO?
needDbInfo = 0
while needDbInfo != 'y' and needDbInfo != 'Y' and needDbInfo != 'n' and needDbInfo != 'N':
	needDbInfo = input("Do you want to insert kegg.jp and genome.jp metadata in your db? [y/n]: ")

if needDbInfo == 'y' or needDbInfo == 'Y':
	needDbInfo = True
else:
	needDbInfo = False

# sulla proprietà geneid di :Target avvengono molte ricerche.
# creare un indice su tale proprietà aumenta l'efficienza.
sessionLocal.run("CREATE INDEX ON :Target(geneid)")

# INSERT PATHWAYS
# get parthways list
if needPathways:
	print("Retrieving pathway list for mmu...")
	pl = getPathwayList("mmu")

	# insert each pathway
	i=0
	# TEST
	print("Importing pathway data to neo4j db...")
	#ts1 = current_milli_time()
	#TEST
	for pw in pl:
		thisPathway = getEntry(pw)
		insertPathway(sessionLocal, thisPathway)
		i += 1
		if i==1:
			# sulla proprietà entry avvengono molte ricerche.
			# creare un indice su tale proprietà aumenta l'efficienza.
			sessionLocal.run("CREATE INDEX ON :Pathway(entry)")
		if i%10 == 0:
			print( str(i) + " of " + str(len(pl)) + " pathways...")
	print("Pathways: done")
	#TEST
	#print(current_milli_time() - ts1)


# INSERT DISEASES
if needDiseases:
	
	print()
	print("Retrieving disease list...")
	diseaseList = getDiseaseList()
	
	# insert each disease
	print("Importing diseases data to neo4j db...")
	i = 0
	for d in diseaseList:
		insertDisease(sessionLocal, d)
		i += 1
		if i==1:
			# sulla proprietà entry avvengono molte ricerche.
			# creare un indice su tale proprietà aumenta l'efficienza.
			sessionLocal.run("CREATE INDEX ON :Disease(entry)")
		if i%10 == 0:
			print( str(i) + " of " + str(len(diseaseList)) + " diseases...")
	print("Diseases: done")


# METADATA NODES
# insert metadata for kegg.jp and genome.jp
if needDbInfo:
	print()
	print("Writing DB_info for kegg.jp and genome.jp...")
	sessionLocal.run("MERGE (:DB_info {name: {name}, link: {link}})",
				{"name": "KEGG", "link": "http://rest.kegg.jp/"})
	sessionLocal.run("MERGE (:DB_info {name: {name}, link: {link}})",
				{"name": "GenomeNet", "link": "http://www.genome.jp/kegg-bin/show_pathway?map="})
	print("DB_info: done.")


# Chiusura sessione db
sessionLocal.close()