""" Routes for file handling """
import os
from flask import Blueprint, redirect, url_for, render_template, request, session, flash, send_file
from werkzeug.utils import secure_filename

from app.modules import util

from app.db import db

from app.models import files
from app.models import publiclinks

bp = Blueprint("uploads", __name__)

uploads_dir = os.path.join(os.getcwd(), "uploads")


@bp.route("/upload", methods=["POST", "GET"])
def upload():
    """ Route for uploading a file """
    if "user" in session:
        if request.method == "POST":
            uploadSuccessful = True
            file = request.files["inputFile"]
            keywords = request.form["keywords"]

            if request.files['inputFile'].filename == '':
                flash("No file submitted", "warning")
                uploadSuccessful = False

            flagGlobal = util.verifyRequestData(request, "flagGlobal")
            globalAddresses = request.form["globalAddresses"]
            if flagGlobal:
                if globalAddresses == "":
                    flash("No global addresses entered", "warning")
                    uploadSuccessful = False

            flagShared = util.verifyRequestData(request, "flagShared")
            sharedUsers = request.form["sharedUsers"]
            if flagShared:
                if sharedUsers == "":
                    flash("No users entered", "warning")
                    uploadSuccessful = False

            # flagEncrypted = util.verifyRequestData(request, "flagEncrypted")
            # encryptedPass = request.form["encryptedPass"]
            # if flagEncrypted:
            #    if encryptedPass == "":
            #        flash("No password entered", "warning")
            #        uploadSuccessful = False

            flagRestricted = util.verifyRequestData(request, "flagRestricted")
            allowedIPs = request.form["allowedIPs"]
            if flagRestricted:
                if allowedIPs == "":
                    flash("No IP addresses entered", "warning")
                    uploadSuccessful = False

            if uploadSuccessful is False:
                return redirect(url_for("uploads.upload"))

            userUploadDir = os.path.join(uploads_dir, session["user"])

            if not os.path.exists(userUploadDir):
                os.makedirs(userUploadDir)

            filepath = os.path.join(userUploadDir, secure_filename(file.filename))

            file.save(filepath)

            filename = os.path.splitext(file.filename)[0]
            fileext = os.path.splitext(file.filename)[1]
            flagstr = util.getFlagString(flagGlobal, flagShared, flagRestricted)

            fileObj = files(filename, fileext, filepath, session["user"], flagstr, keywords, 0, flagGlobal, globalAddresses, flagShared, sharedUsers, flagRestricted, allowedIPs)

            db.session.add(fileObj)
            db.session.commit()

            flash("File uploaded successfully", "info")
            return redirect(url_for("uploads.upload"))
        else:
            return render_template("upload.html")
    else:
        return redirect(url_for("misc.login"))


@bp.route("/files", methods=["GET", "POST"])
def allfiles():
    """ Get all files the user can access """
    if "user" in session:
        found_files = files.query.filter_by(uploader=session["user"]).all()
        sharedFiles = files.query.filter_by(shared=1).all()
        for f in sharedFiles:
            if session["user"] in f.sharedUsers:
                found_files.append(f)
        return render_template("files.html", found_files=found_files)
    else:
        return redirect(url_for("misc.login"))


@bp.route("/download/<fileid>/", methods=["GET"])
def download(fileid):
    """ Download a file """
    if "user" in session:
        fileToDown = files.query.filter_by(_id=fileid).first()
        if fileToDown is None:
            flash("File does not exist", "danger")
            return redirect(url_for("uploads.allfiles"))
        if fileToDown.restricted:
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            allowedIPs = fileToDown.allowedIPs.split()
            if ip in allowedIPs:
                try:
                    print("kahsbd")
                    return send_file(fileToDown.path, as_attachment=True)
                except FileNotFoundError:
                    flash("File no longer exists", "warning")
                    return render_template("notfound.html")
            else:
                flash("You are not authorised", "warning")
                return redirect(url_for("uploads.allfiles"))
        else:
            try:
                if fileToDown.uploader == session["user"] or session["user"] in fileToDown.sharedUsers:
                    return send_file(fileToDown.path, as_attachment=True)
                else:
                    flash("You are not authorised", "warning")
                    return redirect(url_for("uploads.allfiles"))
            except FileNotFoundError:
                flash("File no longer exists", "warning")
                return render_template("notfound.html")
    else:
        return redirect(url_for("misc.login"))


@bp.route("/delete/<fileid>/", methods=["GET"])
def delete(fileid):
    """ Delete a file """
    if "user" in session:
        fileToDel = files.query.filter_by(_id=fileid).first()
        if fileToDel is None:
            flash("File does not exist", "danger")
        else:
            try:
                os.remove(fileToDel.path)
            except FileNotFoundError:
                pass
            fileToDel = files.query.filter_by(_id=fileid).delete()
            db.session.commit()
        return redirect(url_for("uploads.allfiles"))
    else:
        return redirect(url_for("misc.login"))


@bp.route("/unshare/<fileid>/", methods=["GET"])
def unshare(fileid):
    """ Remove a file that was shared with a user """
    if "user" in session:
        fileToDel = files.query.filter_by(_id=fileid).first()
        if fileToDel is None:
            flash("File does not exist", "danger")
        else:
            newSharedString = (fileToDel.sharedUsers.replace(session["user"], "")).strip()
            fileToDel.sharedUsers = newSharedString
            db.session.commit()
        return redirect(url_for("uploads.allfiles"))
    else:
        return redirect(url_for("misc.login"))


@bp.route("/getlink/<fileid>/", methods=["GET"])
def getlink(fileid):
    """ Create a public link for a file """
    if "user" in session:
        existingLink = publiclinks.query.filter_by(fileid=fileid).first()
        if existingLink:
            flash("Link already exists at public/" + existingLink.identifier, "warning")
            return redirect(url_for("uploads.allfiles"))

        linkIden = util.getNewIdentifier()
        fileToLink = files.query.filter_by(_id=fileid).first()
        linkObj = publiclinks(fileid, fileToLink.filename, session["user"], linkIden)
        db.session.add(linkObj)
        db.session.commit()

        flash("Link created at public/" + linkIden, "info")
        return redirect(url_for("uploads.allfiles"))
    else:
        return redirect(url_for("misc.login"))
