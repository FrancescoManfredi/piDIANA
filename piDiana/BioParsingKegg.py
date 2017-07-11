import requests
import re
import string


def getRestDbEntry(dbEntry, url = "http://rest.kegg.jp/get/" ):
	"""
	restituisce il risultato della chiamata Rest di tipo get del db kegg
	"""

	#completo la url
	thisUrl = url + dbEntry + "/"

	# eseguo chiamata rest e casto in stringa il risultato
	res = requests.get (thisUrl).text

	return res

#Torna il risultato della chiamata rest alla lista di un determinato elemento e organismo cercato
#La sintassi usata e' la stessa della documentazione kegg sulle chiamate rest,
# maggiori info alla pagina http://www.kegg.jp/kegg/rest/keggapi.html
def getRestList(data, org, url = "http://rest.kegg.jp/list/" ):

	#concateno la url della chiamata rest
	thisUrl = url + str(data) + '/' + str(org) + '/'

	#eseguo chiamata rest e casto in stringa il risultato
	res = requests.get(thisUrl).text

	return res


#estrae una lista dei pathway appartenenti all'organismo passato presenti nel database kegg
def getPathwayList( organism ):
	"""
	Restituisce una lista di pathways dato il codice identificativo di un organismo.
	"""

	#prendo la lista di pathway dell'organismo passato
	restResult = getRestList('pathway', organism)

	#compilo l'espressione regolare
	query = re.compile(organism + '\d\d\d\d\d')

	#applico l'espressione regolare sulla lista
	result = query.findall(restResult)

	return result

# prende la lista delle diseases da kegg
def getDiseaseList():
	"""
	Returns a list of diseases each in form {'entry': 'HXXXXX', 'name': 'name of disease'}
	"""
	lines = requests.get('http://rest.kegg.jp/list/disease').text.splitlines()
	return [{'entry': l.split('\t')[0][3:], 'name': l.split('\t')[1]} for l in lines]

#parsa la stringa string restituendo i caratteri compresi tra world1 e world2
def getStrBetweenWorldAndWorld( world1, world2, string):

	#compongo l'espressione regolare
	regularExpression = "(?s)(?<=" + str(world1) + ").+?(?=" + str(world2) + ")"

	# compilo l'espressione regolare
	query = re.compile(regularExpression)

	# applico l'espressione regolare sulla string passata
	result = query.findall(string)

	return result


#ritorna la una lista in cui ogni elemento di tale lista e' una riga della stringa passata
def getListOfAllStringLines(string):

	inputString = str(string)

	#elimino da inputString i caratteri [u' all'inizio e ] alla fine caratteristici delle liste
	inputString = list(inputString)
	inputString[0] = ""
	inputString[1] = ""
	inputString[2] = ""
	inputString[-1] = ""
	inputString = "".join(inputString)

	#transformo la stringa passata in input in una lista per estrarne gli indici di end-line
	s = list(inputString)

	#inizializzo i contatori
	x = 0
	y = 0

	#inizializzo la lista da riportare in output
	listaOut = []

	# ciclo la lista cercando i caratteri "\n" che rappresentano l'end-line
	# ( l'espressione regolare "(?s)(?<=  ).+?(?=\\n)" non ha effetto, non trova gli \n per un problema di formattazione in quanto la strigna passata non e' in formato raw )
	while x < len(s):

		#se il carattere s[x] = \
		if s[x] == '\\':
			#se il carattere s[x+1] e' uguale a n
			if s[x+1] == "n":
				#ho trovato un carattere di end-line
				#mi devo prendere la stringa compresa tra y e x(con x non compreso)

				#elimino il carattere \n, ANCHE SE NON COMMENTATO NON SI ELIMINA!!!!
				#s[x] = ''
				#s[x+1] = ''

				varString = inputString[y:x]

				#FATTO SOPRA, DA TESTARE
				#tolgo la n che mi si attacca senza motivo davanti a tutte le stringhe
				if varString[0] == 'n':
					if varString[1] == ' ':
						if varString[2] == ' ':

							varString = list(varString)
							varString[0] = ''
							varString[1] = ''
							varString[2] = ''

							varString = "".join(varString)

				#elimino gli spazi vuoti all'inizio di ogni stringa
				varString = varString.strip ()

				#agiungo varString alla lista
				listaOut.append(varString)

				#incremento y fino a x
				y = x + 1
		x = x+1

	return listaOut




	# 1- estraggo tutti le keyword
	# 2- uso il metodo getStrBetweenWorldAndWorld per estrarre il valore delle keyeord

	# STRUTTURA DATI: chiave-valore con chiave: keyword
	#                                   valore: lista delle righe delle keyword

	# Le REFERENCE hanno una loro sotto struttura, mi salvo il numero delle reference ma nn la loro sottostruttura

def getKeyValueByTextAndStructureOrganism( structure, text):

	#inizializzo il dizionario
	d = {}

	d['numReference'] = 0
	#inizializzo il contatore
	count = 0

	#ciclo sulla struttura
	while count < len(structure) - 1:

		# se non sto esaminando una referenza
		if(str(structure[count]) != 'REFERENCE'):

			#inizializzo una nuova chiave in d con valore una stringa = all'elemento della struttura secondo count,
			#che puntera' ad una lista di stringhe, ognuna rappresentante una riga della chiave della struttura in esame
			d[str(structure[count])] = getListOfAllStringLines(
				getStrBetweenWorldAndWorld( structure[count], structure[count+1],text))

		else:
			d['numReference'] = d['numReference'] + 1

		count = count + 1

	#prendo i dati dell'ultima keyWord
	d[str (structure[count])] = getListOfAllStringLines (
		getStrBetweenWorldAndWorld (structure[len(structure) - 1], "///", text))

	return d

# parsa il testo di un organismo e ne estrae le sue keyword (semplicemente tutte le parole che presentano piu' di 2 caratteri maiuscoli consegutivi )
def getKeywordByOrganismText( organismText ):

	# compongo l'espressione regolare,
	#   \n          prendo tutto cio' che inizia con un a capo,
	#   [A-Z]+      seguito da uno o piu' caratteri maiuscoli,
	#   [_]?    seguiti da 0 o 1 "_",
	#   [A-Z]+      e che finiscono con uno o piu' caratteri maiuscoli
	regularExpression = "(\n[A-Z]+[_]?[A-Z]+)"


	# compilo l'espressione regolare
	query = re.compile(regularExpression)

	# applico l'espressione regolare sulla lista
	parsingResult = query.findall(organismText)

	#inizializzo una nuova lista
	newList = []

	#ciclo sulla lista parsata precedentemente
	for i in parsingResult:
		#elimino il carattere endLine
		i = i[1:]

		#appendo i alla nuova lista
		newList.append(i)

	# aggiungo ENTRY alla lista delle keyword che altrimenti non verrebbe aggiunta
	listKeyWord = ['ENTRY']

	#aggiungo gli altri elementi in fondo alla lista
	listKeyWord.extend(newList)

	#restituisco la lista pulita
	return listKeyWord

#passato un id di un organismo ne ricava, tramite una chiamata get di tipo REST,
#una struttura chiave valore
def getEntry(idOrg):
	"""
	Prende id di un'entità in kegg, effettua la chiamata alla api REST per ottenere
	i dati relativi e li restituisce in un dizionario.
	"""
	#chiamata rest, text e' il testo che descrive l'organismo
	text = getRestDbEntry(idOrg)

	#estraggo le Keyword dall' organismo
	organismStructure = getKeywordByOrganismText(text)

	#creo il chiave valore ordinato
	result = getKeyValueByTextAndStructureOrganism( organismStructure, text)

	return result
