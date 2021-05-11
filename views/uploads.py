from flask import Blueprint, current_app, redirect, url_for, render_template, request, session, flash, send_file, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.utils import secure_filename
from argon2 import PasswordHasher
import os
import datetime
import json

from modules import auth
from modules import util
from db import db

from models.users import users
from models.files import files
from models.publiclinks import publiclinks

uploads = Blueprint("uploads", __name__)

uploads_dir = os.path.join(os.path.join(os.getcwd(), "instance"), 'uploads')

@uploads.route("/upload", methods=["POST", "GET"])
def upload():
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

			"""
			flagEncrypted = util.verifyRequestData(request, "flagEncrypted")
			encryptedPass = request.form["encryptedPass"]
			if flagEncrypted:
				if encryptedPass == "":
					flash("No password entered", "warning")
					uploadSuccessful = False
			"""

			flagRestricted = util.verifyRequestData(request, "flagRestricted")
			allowedIPs = request.form["allowedIPs"]
			if flagRestricted:
				if allowedIPs == "":
					flash("No IP addresses entered", "warning")
					uploadSuccessful = False

			if uploadSuccessful == False:
				return redirect(url_for("uploads.upload"))

			userUploadDir = os.path.join(uploads_dir, session["user"])

			if not os.path.exists(userUploadDir):
				os.makedirs(userUploadDir)

			filepath = os.path.join(userUploadDir, secure_filename(file.filename))			

			file.save(filepath)

			filename = os.path.splitext(file.filename)[0]
			fileext = os.path.splitext(file.filename)[1]
			flagstr = util.getFlagString(0, flagGlobal, flagShared, flagRestricted)

			fileObj = files(filename, fileext, filepath, session["user"], flagstr, keywords, 0, flagGlobal, globalAddresses, flagShared, sharedUsers, flagRestricted, allowedIPs)

			db.session.add(fileObj)
			db.session.commit()

			flash("File uploaded successfully", "info")
			return redirect(url_for("uploads.upload"))
		else:
			return render_template("upload.html")
	else:
		return redirect(url_for("misc.login"))

@uploads.route("/files", methods=["GET", "POST"])
def allfiles():
	if "user" in session:
		found_files = files.query.filter_by(uploader=session["user"]).all()
		sharedFiles = files.query.filter_by(shared=1).all()
		for f in sharedFiles:
			if session["user"] in f.sharedUsers:
				found_files.append(f)
		return render_template("files.html", found_files=found_files)
	else:
		return redirect(url_for("misc.login"))

@uploads.route("/download/<fileid>/", methods=["GET"])
def download(fileid):
	if "user" in session:
		fileToDown = files.query.filter_by(_id=fileid).first()
		if fileToDown == None:
			flash("File does not exist", "danger")
			return redirect(url_for("uploads.allfiles"))
		if fileToDown.restricted:
			ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)  
			allowedIPs = fileToDown.allowedIPs.split()
			if ip in allowedIPs:
				try:
					return send_file(fileToDown.path, as_attachment=True)		
				except FileNotFoundError:
					flash("File no longer exists", "warning")
					return render_template("notfound.html")
			else:
				flash("You are not authorised", "warning")
				return redirect(url_for("uploads.allfiles"))
		else:
			try:
				return send_file(fileToDown.path, as_attachment=True)		
			except FileNotFoundError:
				flash("File no longer exists", "warning")
				return render_template("notfound.html")
	else:
		return redirect(url_for("misc.login"))

@uploads.route("/delete/<fileid>/", methods=["GET"])
def delete(fileid):
	if "user" in session:
		fileToDel = files.query.filter_by(_id=fileid).first()
		if fileToDel == None:
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

@uploads.route("/unshare/<fileid>/", methods=["GET"])
def unshare(fileid):
	if "user" in session:		
		fileToDel = files.query.filter_by(_id=fileid).first()
		if fileToDel == None:
			flash("File does not exist", "danger")
		else:
			newSharedString = (fileToDel.sharedUsers.replace(session["user"], "")).strip()
			fileToDel.sharedUsers = newSharedString
			db.session.commit()
		return redirect(url_for("uploads.allfiles"))
	else:
		return redirect(url_for("misc.login"))

@uploads.route("/getlink/<fileid>/", methods=["GET"])
def getlink(fileid):
	if "user" in session:		
		existingLink = publiclinks.query.filter_by(fileid=fileid).first()
		if existingLink:
			flash("Link already exists at public/" + existingLink.identifier, "warning")
			return redirect(url_for("uploads.allfiles"))

		linkIden = util.getNewIdentifier(db)
		fileToLink = files.query.filter_by(_id=fileid).first()
		linkObj = publiclinks(fileid, fileToLink.filename, session["user"], linkIden)
		db.session.add(linkObj)
		db.session.commit()

		flash("Link created at public/" + linkIden, "info")
		return redirect(url_for("uploads.allfiles"))
	else:
		return redirect(url_for("misc.login"))