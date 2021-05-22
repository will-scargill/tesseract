""" Public link class """
from db import db


class publiclinks(db.Model):
    """ Public link class """
    _id = db.Column("id", db.Integer, primary_key=True)
    fileid = db.Column(db.Integer())
    filename = db.Column(db.String(64))
    creator = db.Column(db.String(64))
    identifier = db.Column(db.String(64))

    def __init__(self, fileid, filename, creator, identifier):
        self.fileid = fileid
        self.filename = filename
        self.creator = creator
        self.identifier = identifier
