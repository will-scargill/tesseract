""" Log class """
import datetime
from db import db


class logs(db.Model):
    """ Log class """
    _id = db.Column("id", db.Integer, primary_key=True)
    user = db.Column(db.String(64))
    datetime = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    ip = db.Column(db.String(64))
    action = db.Column(db.String(128))

    def __init__(self, user, ip, action):
        self.user = user
        self.ip = ip
        self.action = action
