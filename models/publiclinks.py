from db import db

class publiclinks(db.Model):
	_id = db.Column("id", db.Integer, primary_key=True)
	fileid = db.Column(db.Integer())
	identifier = db.Column(db.String(64))

	def __init__(self, fileid, identifier):
		self.fileid = fileid
		self.identifier = identifier