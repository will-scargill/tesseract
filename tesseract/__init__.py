""" Application factory """
import os

from flask import Flask

from tesseract.models import files
from tesseract.models import publiclinks
from tesseract.models import users

from tesseract.routes import misc
from tesseract.routes import admin
from tesseract.routes import uploads

from .db import db


#def create_app(test_config=None):
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'tesseract.sqlite'),
    SQLALCHEMY_DATABASE_URI="sqlite:///" + app.instance_path + "///db.sqlite3",
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# if test_config is None:
    # load the instance config, if it exists, when not testing
    # app.config.from_pyfile('config.py', silent=True)
# else:
    # load the test config if passed in
    # app.config.from_mapping(test_config)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

app.register_blueprint(misc.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(uploads.bp)

db.init_app(app)
with app.app_context():
    db.create_all()

# return app
