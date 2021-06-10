""" Main tesseract file """
import os
from datetime import timedelta
from flask import Flask

from views.misc import misc
from views.uploads import uploads
from views.admin import admin

from db import db

app = Flask(__name__)
app.secret_key = os.urandom(24)
dbType = os.environ.get("TESSERACT_DB_TYPE")
if dbType is None or dbType == "sqlite":
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.instance_path + "///db.sqlite3"
elif dbType == "mysql":
    dbUser = os.environ.get("MYSQL_USER")
    dbHost = os.environ.get("MYSQL_HOST")
    dbPass = os.environ.get("MYSQL_PASS")
    dbName = os.environ.get("MYSQL_DB_NAME")
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://{0}:{1}@{2}/{3}".format(dbUser, dbPass, dbHost, dbName)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=2)

app.register_blueprint(misc)
app.register_blueprint(uploads)
app.register_blueprint(admin)

uploads_dir = os.path.join(os.getcwd(), "uploads")

os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(app.instance_path, exist_ok=True)

db.init_app(app)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
