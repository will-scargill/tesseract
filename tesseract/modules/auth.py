""" Functions for authentication """
import json
from argon2 import PasswordHasher
import argon2

ph = PasswordHasher()


def VerifyHash(h, password):
    """ Verify a password against the stored hash """
    try:
        ph.verify(json.loads(h), password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False
