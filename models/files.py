""" File class """
import datetime
from db import db


class files(db.Model):
    """ File class """
    _id = db.Column("id", db.Integer, primary_key=True)
    filename = db.Column(db.String(64))
    extension = db.Column(db.String(8))
    path = db.Column(db.String(128))
    uploader = db.Column(db.String(64))
    flags = db.Column(db.String(128))
    datetime = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    keywords = db.Column(db.String(128))
    encrypted = db.Column(db.Boolean())
    glo = db.Column(db.Boolean())
    globalAddresses = db.Column(db.String(128))
    shared = db.Column(db.Boolean())
    sharedUsers = db.Column(db.String(128))
    restricted = db.Column(db.Boolean())
    allowedIPs = db.Column(db.String(128))

    def __init__(self, filename, filetype, path, uploader, flagstring, keywords, encrypted, glo, globalAddresses, shared, sharedUsers, restricted, allowedIPs):
        self.filename = filename
        self.extension = filetype
        self.path = path
        self.uploader = uploader
        self.flags = flagstring
        self.keywords = keywords
        self.encrypted = encrypted
        self.glo = glo
        self.globalAddresses = globalAddresses
        self.shared = shared
        self.sharedUsers = sharedUsers
        self.restricted = restricted
        self.allowedIPs = allowedIPs
