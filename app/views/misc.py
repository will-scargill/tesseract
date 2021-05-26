""" Routes for all other pages """
import os
import json
import random
import string
import hashlib
from flask import Blueprint, redirect, url_for, render_template, request, session, flash, send_file
from argon2 import PasswordHasher

from modules import auth
from modules import util

from models.users import users
from models.files import files
from models.publiclinks import publiclinks
from db import db

ph = PasswordHasher()

misc = Blueprint("misc", __name__)


@misc.route("/", methods=["POST", "GET"])
def login():
    """ Login route """
    if request.method == "POST":
        session.permanent = True
        user = request.form["username"]
        password = request.form["password"]
        found_users = users.query.filter_by(name=user).first()
        if found_users:
            authed = auth.VerifyHash(found_users.password, password)
            if authed:
                session["user"] = user
                if user == "admin":
                    util.newInstallCheck()
                return redirect(url_for("misc.home"))
            else:
                flash("Invalid login", "warning")
                return redirect(url_for("misc.login"))
        else:
            flash("Invalid login", "warning")
            return redirect(url_for("misc.login"))
    else:
        if "user" in session:
            return redirect(url_for("misc.home"))
        return render_template("login.html")


@misc.route("/home")
def home():
    """ Home route """
    if "user" in session:
        user = session["user"]
        ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        return render_template("index.html", username=user, ip=ip)
    else:
        return redirect(url_for("misc.login"))


@misc.route("/public/<iden>", methods=["GET"])
def public(iden):
    """ Gets a file corresponding to a public link """
    idFromIden = publiclinks.query.filter_by(identifier=iden).first()
    if idFromIden is None:
        flash("Link does not correspond to a file", "warning")
        return render_template("notfound.html")
    else:
        fileToDown = files.query.filter_by(_id=idFromIden.fileid).first()
    try:
        md5_hash = hashlib.md5()
        with open(fileToDown.path, "rb") as fileObj:
            content = fileObj.read()
            md5_hash.update(content)
        checksum = md5_hash.hexdigest()

        return render_template("publicfile.html", filename=fileToDown.filename + fileToDown.extension, uploader=fileToDown.uploader, datetime=fileToDown.datetime, checksum=checksum, fileid=fileToDown._id)
    except FileNotFoundError:
        flash("File no longer exists", "warning")
        return render_template("notfound.html")


@misc.route("/pubdown/<fileid>", methods=["GET"])
def publicdownload(fileid):
    """ Path for actual file download """
    fileToDown = files.query.filter_by(_id=fileid).first()
    return send_file(fileToDown.path, as_attachment=True)


@misc.route("/logout")
def logout():
    """ Logout a user """
    if "user" in session:
        session.pop("user", None)
        flash("Logged out", "info")
    return redirect(url_for("misc.login"))


@misc.route("/newinstall")
def newinstall():
    """ Gets admin password for first time install """
    if os.path.isfile("instance/lock.txt"):
        flash("Install already complete", "warning")
        return render_template("notfound.html")
    else:
        exists = users.query.filter_by(name="admin").first()
        if not exists:
            newPass = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
            newPassHash = ph.hash(newPass)
            newAdmin = users("admin", json.dumps(newPassHash), 1)
            db.session.add(newAdmin)
            db.session.commit()
            with open("/app/templates/newinstall.html", "w") as f:
                f.write(newPass)
                f.close()
            return render_template("newinstall.html")
        else:
            return render_template("newinstall.html")
