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
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.instance_path + "///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=2)

app.register_blueprint(misc)
app.register_blueprint(uploads)
app.register_blueprint(admin)

uploads_dir = os.path.join(os.getcwd(), "uploads")

os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(app.instance_path, exist_ok=True)

if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.run(debug=True)
