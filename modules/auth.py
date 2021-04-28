from argon2 import PasswordHasher
import argon2
import json

def VerifyHash(h, password):
	try:
		ph.verify(json.loads(h), password)
		return True
	except argon2.exceptions.VerifyMismatchError:
		return False
		
ph = PasswordHasher()