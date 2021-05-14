""" User class """
from db import db


class users(db.Model):
    """ User class """
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    admin = db.Column(db.Boolean())

    def __init__(self, name, password, admin):
        self.name = name
        self.password = password
        self.admin = admin
