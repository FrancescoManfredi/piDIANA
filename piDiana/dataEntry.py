# Modulo per i metodi di inserimento dati nel database n4j
from BioParsingKegg import getEntry

if __name__ == "__main__":
    print("Questo è un modulo. Esegui core.py.")

def insertPathway(dbsession, pathway):
	"""
	dbsession: sessione aperta con un database neo4j
	pathway: un dizionario con i dati di un pathway preso da kegg
	Questa funzione inserisce un pathway nel database neo4j e crea
	i collegamenti necessari con i target (che devono essere già presenti
	nel database)
	"""
	
	# Esiste la possibilità che un pathway nei dati di kegg non abbia
	# uno di questi campi. In questo caso voglio segnalare il problema
	# a chi sta eseguendo lo script.
	try:
		entry = pathway['ENTRY'][0].split()[0] # id univoco es: mmu00010
		name = pathway['NAME'][0] #nome testuale, es: Glycolysis / Gluconeogenesis - Mus musculus (mouse)
		fullData = "http://rest.kegg.jp/get/" + entry
		classe = pathway['CLASS'][0] # classe del pathway, es: Metabolism; Carbohydrate metabolism
		dbsession.run("MERGE (:Pathway {name: {name}, entry: {entry}, class: {classe}, fullData: {fullData} })",
				{"name": name, "entry": entry, "classe": classe, "fullData": fullData})
	except KeyError:
		print("Pathway " + entry + " on kegg does not have a CLASS field")
		dbsession.run("MERGE (:Pathway {name: {name}, entry: {entry}, class: {classe}, fullData: {fullData} })",
				{"name": name, "entry": entry, "classe": "no-data", "fullData": fullData})
		
	
	# gli url per prendere un gene dal geneid sono in forma /get/mmu:geneid
	
	# COLLEGO IL PATHWAY APPENA INSERITO AI TARGET COINVOLTI
	try:
		geneidList = [gid.split()[0] for gid in pathway['GENE']] #pulisco la lista dei geni per ridurla ai soli id
		
		# metodo più veloce: composizione di unica query
		# 37.801s per 30 pathways
		batchQuery = "MATCH (p:Pathway {entry:\"" + entry + "\"}), (t:Target) WHERE t.geneid IN ["
		
		for geneid in geneidList:
			# metodo più lento: 70.151s per 30 pathways
			#dbsession.run("MATCH (t:Target {geneid: {geneid}}), (p:Pathway {entry: {entry}}) CREATE (t)-[:InvolvedIn]->(p)",
			#	{"geneid": geneid, "entry": entry})

			batchQuery += "\"" + geneid + "\","
		batchQuery = batchQuery[:-1] + "]"
		batchQuery += " CREATE UNIQUE (t)-[:InvolvedIn]->(p)"
		# la query totale ha forma
		# MATCH (p:Pathway {entry:"entry"}), (t:Target) WHERE t.geneid IN ["value1", "value2",...]
		# CREATE UNIQUE (t)-[:InvolvedIn]->(p)
		dbsession.run(batchQuery)
		
	except KeyError:
		
		print("Pathway " + entry + " on kegg has no genes listed.")
		
			
def insertDisease(dbsession, disease):
	"""
	Insert a single disease and its relationship to pathways it's linke to given
	a dictionary in the form {'entry': 'HXXXXX', 'name': 'name of disease'}.
	"""
	
	# recupero i dati completi sulla disease per ottenere la lista dei pathways
	# ai quali va collegata
	
	# attenzione: i pathways possono essere presentati in due forme:
	# 1. hsaXXXXX Nome del pathway
	# 2. hsaXXXXX(altra roba tra parentesi che dovrebbe essere una specifica di geni)
	# il numero XXXXX è sempre a 5 cifre. In entrambi i casi posso usare uno slicing preciso
	# Alcune disease non hanno pathways a cui essere collegate
	try:
		pwList = getEntry(disease['entry'])['PATHWAY']
		pathwaysEntries = ["mmu" + e[3:8] for e in pwList]

		# inserimento singola disease
		dbsession.run("MERGE (:Disease {entry: {entry}, name: {name}})",
			{'entry': disease['entry'], 'name': disease['name']})
		
		batchQuery = "MATCH (d:Disease {entry:\"" + disease['entry'] + "\"}), (p:Pathway) WHERE p.entry IN ["
		
		# inserimento delle relationship con i pathways
		for pw in pathwaysEntries:
			batchQuery += "\"" + pw + "\","
			
		batchQuery = batchQuery[:-1] + "]"
		batchQuery += " CREATE UNIQUE (d)-[:RelatedTo]->(p)"
		dbsession.run(batchQuery)
	
	except KeyError:
		print("Disease " + disease['entry'] + " is not related to any pathway. Skipping.")