""" Routes for admin section """
import json
from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from argon2 import PasswordHasher

from models.users import users
from models.publiclinks import publiclinks

from db import db

ph = PasswordHasher()

admin = Blueprint("admin", __name__)


@admin.route("/admin/accounts", methods=["GET", "POST"])
def adminAccounts():
    """ Display details about user accounts and allow creation """
    if "user" in session:
        found_users = users.query.filter_by(name=session["user"]).first()
        if found_users.admin is True:
            if request.method == "POST":
                username = request.form["username"]
                password = request.form["password"]
                passwordHash = ph.hash(password.strip())

                allUsers = users.query.all()
                for user in allUsers:
                    if user.name == username:
                        flash("An account with this name already exists", "warning")
                        return render_template("accounts.html", allUsers=allUsers)

                newUser = users(username, json.dumps(passwordHash), 0)

                db.session.add(newUser)
                db.session.commit()

                allUsers = users.query.all()
                return render_template("accounts.html", allUsers=allUsers)
            else:
                allUsers = users.query.all()
                return render_template("accounts.html", allUsers=allUsers)
        else:
            flash("You are not authorised", "warning")
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            return render_template("index.html", username=session["user"], ip=ip), 403
    else:
        return redirect(url_for("misc.login"))


@admin.route("/admin/links", methods=["GET"])
def adminLinks():
    """ Display and remove public links """
    if "user" in session:
        found_users = users.query.filter_by(name=session["user"]).first()
        if found_users.admin is True:

            allLinks = publiclinks.query.all()

            return render_template("links.html", allLinks=allLinks)
        else:
            flash("You are not authorised", "warning")
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            return render_template("index.html", username=session["user"], ip=ip), 403
    else:
        return redirect(url_for("misc.login"))


@admin.route("/admin/network", methods=["GET"])
def adminNetwork():
    """ Placeholder """
    if "user" in session:
        found_users = users.query.filter_by(name=session["user"]).first()
        if found_users.admin is True and False:  # pylint: disable=R1727 # Temporarily disabled

            return render_template("network.html")
        else:
            flash("You are not authorised", "warning")
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            return render_template("index.html", username=session["user"], ip=ip), 403
    else:
        return redirect(url_for("misc.login"))


@admin.route("/admin/logs", methods=["GET"])
def adminLogs():
    """ Show logs """
    if "user" in session:
        found_users = users.query.filter_by(name=session["user"]).first()
        if found_users.admin is True:

            return render_template("logs.html")
        else:
            flash("You are not authorised", "warning")
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            return render_template("index.html", username=session["user"], ip=ip), 403
    else:
        return redirect(url_for("misc.login"))


@admin.route("/admin/accounts/toggle/<userid>", methods=["GET"])
def toggleAdmin(userid):
    """ Toggles the admin status of a user """
    if "user" in session:
        found_users = users.query.filter_by(name=session["user"]).first()
        if found_users.admin is True:
            foundUser = users.query.filter_by(_id=userid).first()
            if foundUser is None:
                flash("User not found", "danger")
            elif foundUser.name == session["user"] or foundUser.name == "admin":
                flash("You cannot revoke this user's admin", "warning")
            else:
                if foundUser.admin:
                    foundUser.admin = 0
                elif not foundUser.admin:
                    foundUser.admin = 1
                db.session.commit()

            allUsers = users.query.all()

            return render_template("accounts.html", allUsers=allUsers)
        else:
            flash("You are not authorised", "warning")
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            return render_template("index.html", username=session["user"], ip=ip), 403
    else:
        return redirect(url_for("misc.login"))


@admin.route("/admin/accounts/delete/<userid>", methods=["GET"])
def deleteUser(userid):
    """ Deletes a user """
    if "user" in session:
        found_users = users.query.filter_by(name=session["user"]).first()
        if found_users.admin is True:
            foundUser = users.query.filter_by(_id=userid).first()
            if foundUser is None:
                flash("User not found", "danger")
            elif foundUser.admin:
                flash("You cannot delete this user", "warning")
            else:
                users.query.filter_by(_id=userid).delete()
                db.session.commit()

            allUsers = users.query.all()

            return render_template("accounts.html", allUsers=allUsers)
        else:
            flash("You are not authorised", "warning")
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            return render_template("index.html", username=session["user"], ip=ip), 403
    else:
        return redirect(url_for("misc.login"))


@admin.route("/admin/links/delete/<linkid>", methods=["GET"])
def deleteLink(linkid):
    """ Deletes a public link """
    if "user" in session:
        found_users = users.query.filter_by(name=session["user"]).first()
        if found_users.admin is True:
            foundLink = publiclinks.query.filter_by(_id=linkid).first()
            if foundLink is None:
                flash("Link not found", "danger")
            else:
                publiclinks.query.filter_by(_id=linkid).delete()
                db.session.commit()

            allLinks = publiclinks.query.all()

            return render_template("links.html", allLinks=allLinks)
        else:
            flash("You are not authorised", "warning")
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            return render_template("index.html", username=session["user"], ip=ip), 403
    else:
        return redirect(url_for("misc.login"))


@admin.route("/admin/accounts/change/<userid>", methods=["GET", "POST"])
def changePassword(userid):
    """ Change the password of a user """
    if "user" in session:
        found_users = users.query.filter_by(name=session["user"]).first()
        if found_users.admin is True:
            if request.method == "POST":
                foundUser = users.query.filter_by(_id=userid).first()
                newPassword = request.form["password"]
                if newPassword != "":
                    newPassHash = ph.hash(newPassword)
                    foundUser.password = json.dumps(newPassHash)

                    db.session.commit()
                    flash("Password change successful", "info")
                    return redirect(url_for("admin.adminAccounts"))
                else:
                    flash("Password is empty", "warning")
                    return render_template("change.html", userid=userid)
            else:
                return render_template("change.html", userid=userid)
        else:
            flash("You are not authorised", "warning")
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            return render_template("index.html", username=session["user"], ip=ip), 403
    else:
        return redirect(url_for("misc.login"))
