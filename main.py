from flask import Flask, Blueprint, redirect, url_for, render_template, request, session, flash, send_file, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.utils import secure_filename
from argon2 import PasswordHasher
import os
import datetime
import json
import random
import string

from modules import auth
from modules import util

from views.misc import misc
from views.uploads import uploads
from views.admin import admin

from db import db

from models.users import users
from models.files import files
from models.publiclinks import publiclinks

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.instance_path + "///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=2)

app.register_blueprint(misc)
app.register_blueprint(uploads)
app.register_blueprint(admin)

uploads_dir = os.path.join(os.path.join(os.getcwd(), "instance"), 'uploads')

os.makedirs(uploads_dir, exist_ok=True)

if __name__ == "__main__":
	db.init_app(app)
	with app.app_context():
		db.create_all()
	
	app.run(debug=True)