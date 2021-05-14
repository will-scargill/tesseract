""" Utilities """
import random
import string
import os
from werkzeug.exceptions import BadRequestKeyError

from models.publiclinks import publiclinks


def verifyRequestData(request, data):
    """ Check if request data exists """
    try:
        existCheck = request.form[data]  # pylint: disable=W0612 # Only created to see if possible
        returnData = True
    except BadRequestKeyError:
        returnData = False
    return returnData


def getFlagString(glo, sha, res):
    """ Form a flag string for storing in the db """
    flagString = ""
    if glo is not False:
        flagString += "g"
    if sha is not False:
        flagString += "s"
    if res is not False:
        flagString += "r"
    return flagString


def getNewIdentifier():
    """ Get a unique identifier for a public link """
    doesNotExist = False
    while doesNotExist is False:
        newIden = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(4))
        doesNotExist = publiclinks.query.filter_by(identifier=newIden).first() is None
        if doesNotExist:
            return newIden


def newInstallCheck():
    """ Check if lock.txt exists """
    if not os.path.isfile("instance/lock.txt"):
        with open("instance/lock.txt", "w") as f:
            f.write(";)")
            f.close()
