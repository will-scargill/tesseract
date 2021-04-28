from werkzeug.exceptions import BadRequestKeyError
from main import publiclinks
import random, string

def verifyRequestData(request, data):
	try:
		existCheck = request.form[data]
		returnData = True
	except BadRequestKeyError:
		returnData = False
	return returnData

def getFlagString(enc, glo, sha, res):
	flagString = ""
	if enc != False:
		flagString += "e"
	if glo != False:
		flagString += "g"
	if sha != False:
		flagString += "s"
	if res != False:
		flagString += "r"
	return flagString

def getNewIdentifier(db):
	doesNotExist = False
	while doesNotExist == False:
		allLinks = publiclinks.query.all()
		newIden = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(4))
		doesNotExist = publiclinks.query.filter_by(identifier=newIden).first() is None
		if doesNotExist:
			return newIden