from flask import Flask, redirect, url_for, render_template, request, session, flash, send_file, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.utils import secure_filename
from argon2 import PasswordHasher
import os
import datetime
import json

from modules import auth
from modules import util

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.instance_path + "///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=2)

db = SQLAlchemy(app)
ph = PasswordHasher()

uploads_dir = os.path.join(app.instance_path, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

class users(db.Model):
	_id = db.Column("id", db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	password = db.Column(db.String(100))
	admin = db.Column(db.Boolean())

	def __init__(self, name, password, admin):
		self.name = name
		self.password = password
		self.admin = admin

class files(db.Model):
	_id = db.Column("id", db.Integer, primary_key=True)
	filename = db.Column(db.String(64))
	extension = db.Column(db.String(8)) 
	path = db.Column(db.String(128))
	uploader = db.Column(db.String(64))
	flags = db.Column(db.String(128))
	datetime = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
	keywords = db.Column(db.String(128))
	encrypted = db.Column(db.Boolean())
	glo = db.Column(db.Boolean())
	globalAddresses = db.Column(db.String(128))
	shared = db.Column(db.Boolean())
	sharedUsers = db.Column(db.String(128))
	restricted = db.Column(db.Boolean())
	allowedIPs = db.Column(db.String(128))

	def __init__(self, filename, filetype, path, uploader, flagstring, keywords, encrypted, glo, globalAddresses, shared, sharedUsers, restricted, allowedIPs):
		self.filename = filename
		self.extension = filetype
		self.path = path
		self.uploader = uploader
		self.flags = flagstring
		self.keywords = keywords
		self.encrypted = encrypted
		self.glo = glo
		self.globalAddresses = globalAddresses
		self.shared = shared
		self.sharedUsers = sharedUsers
		self.restricted = restricted
		self.allowedIPs = allowedIPs

class publiclinks(db.Model):
	_id = db.Column("id", db.Integer, primary_key=True)
	fileid = db.Column(db.Integer())
	identifier = db.Column(db.String(64))

	def __init__(self, fileid, identifier):
		self.fileid = fileid
		self.identifier = identifier

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		session.permanent = True
		user = request.form["username"]
		password = request.form["password"]
		found_users = users.query.filter_by(name=user).first()
		if found_users:
			authed = auth.VerifyHash(found_users.password, password)
			if authed:
				session["user"] = user
				return redirect(url_for("home"))
			else:
				flash("Invalid login", "warning")
				return redirect(url_for("login"))
		else:
			flash("Invalid login", "warning")
			return redirect(url_for("login"))
	else:
		if "user" in session:
			return redirect(url_for("home"))
		return render_template("login.html")

@app.route("/home")
def home():
	if "user" in session:
		user = session["user"]
		ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)  
		return render_template("index.html", username=user, ip=ip)
	else:
		return redirect(url_for("login"))

@app.route("/upload", methods=["POST", "GET"])
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
				return redirect(url_for("upload"))

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
			return redirect(url_for("upload"))
		else:
			return render_template("upload.html")
	else:
		return redirect(url_for("login"))

@app.route("/admin/accounts", methods=["GET", "POST"])
def adminAccounts():
	if "user" in session:
		if request.method == "POST":
			username = request.form["username"]
			password = request.form["password"]
			passwordHash = ph.hash(password)

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
			found_users = users.query.filter_by(name=session["user"]).first()
			if found_users.admin == True:

				allUsers = users.query.all()

				return render_template("accounts.html", allUsers=allUsers)
			else:
				flash("You are not authorised", "warning")
				return render_template("index.html", username=session["user"]),403
	else:
		return redirect(url_for("login"))

@app.route("/admin/network", methods=["GET"])
def adminNetwork():
	if "user" in session:
		found_users = users.query.filter_by(name=session["user"]).first()
		if found_users.admin == True:

			return render_template("network.html")
		else:
			flash("You are not authorised", "warning")
			return render_template("index.html", username=session["user"]),403
	else:
		return redirect(url_for("login"))

@app.route("/admin/logs", methods=["GET"])
def adminLogs():
	if "user" in session:
		found_users = users.query.filter_by(name=session["user"]).first()
		if found_users.admin == True:

			return render_template("logs.html")
		else:
			flash("You are not authorised", "warning")
			return render_template("index.html", username=session["user"]),403
	else:
		return redirect(url_for("login"))

@app.route("/admin/accounts/toggle/<userid>", methods=["GET"])
def toggleAdmin(userid):
	if "user" in session:
		found_users = users.query.filter_by(name=session["user"]).first()
		if found_users.admin == True:
			foundUser = users.query.filter_by(_id=userid).first()

			if foundUser.name == session["user"] or foundUser.name == "admin":
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
			return render_template("index.html", username=session["user"]),403	
	else:
		return redirect(url_for("login"))

@app.route("/admin/accounts/delete/<userid>", methods=["GET"])
def deleteUser(userid):
	if "user" in session:
		found_users = users.query.filter_by(name=session["user"]).first()
		if found_users.admin == True:
			foundUser = users.query.filter_by(_id=userid).first()

			if foundUser.admin:
				flash("You cannot delete this user", "warning")
			else:
				users.query.filter_by(_id=userid).delete()
				db.session.commit()

			allUsers = users.query.all()

			return render_template("accounts.html", allUsers=allUsers)
		else:
			flash("You are not authorised", "warning")
			return render_template("index.html", username=session["user"]),403	
	else:
		return redirect(url_for("login"))

@app.route("/files", methods=["GET", "POST"])
def allfiles():
	if "user" in session:
		found_files = files.query.filter_by(uploader=session["user"]).all()
		sharedFiles = files.query.filter_by(shared=1).all()
		for f in sharedFiles:
			if session["user"] in f.sharedUsers:
				found_files.append(f)
		return render_template("files.html", found_files=found_files)
	else:
		return redirect(url_for("login"))

@app.route("/download/<fileid>/", methods=["GET"])
def download(fileid):
	if "user" in session:
		fileToDown = files.query.filter_by(_id=fileid).first()
		if fileToDown.restricted:
			ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)  
			allowedIPs = fileToDown.allowedIPs.split()
			if ip in allowedIPs:
				return send_file(fileToDown.path, as_attachment=True)
			else:
				flash("You are not authorised", "warning")
				return redirect(url_for("allfiles"))
		else:
			return send_file(fileToDown.path, as_attachment=True)		
	else:
		return redirect(url_for("login"))

@app.route("/delete/<fileid>/", methods=["GET"])
def delete(fileid):
	if "user" in session:
		fileToDel = files.query.filter_by(_id=fileid).first()
		os.remove(fileToDel.path)
		fileToDel = files.query.filter_by(_id=fileid).delete()
		db.session.commit()
		return redirect(url_for("allfiles"))
	else:
		return redirect(url_for("login"))

@app.route("/unshare/<fileid>/", methods=["GET"])
def unshare(fileid):
	if "user" in session:		
		fileToDel = files.query.filter_by(_id=fileid).first()
		newSharedString = (fileToDel.sharedUsers.replace(session["user"], "")).strip()
		fileToDel.sharedUsers = newSharedString
		db.session.commit()
		return redirect(url_for("allfiles"))
	else:
		return redirect(url_for("login"))

@app.route("/getlink/<fileid>/", methods=["GET"])
def getlink(fileid):
	if "user" in session:		
		existingLink = publiclinks.query.filter_by(fileid=fileid).first()
		if existingLink:
			flash("Link already exists at public/" + existingLink.identifier, "warning")
			return redirect(url_for("allfiles"))

		linkIden = util.getNewIdentifier(db)
		fileToLink = files.query.filter_by(_id=fileid).first()
		linkObj = publiclinks(fileid, linkIden)
		db.session.add(linkObj)
		db.session.commit()

		flash("Link created at public/" + linkIden, "info")
		return redirect(url_for("allfiles"))
	else:
		return redirect(url_for("login"))

@app.route("/public/<iden>", methods=["GET"])
def public(iden):
	idFromIden = publiclinks.query.filter_by(identifier=iden).first()
	fileToDown = files.query.filter_by(_id=idFromIden.fileid).first()
	return send_file(fileToDown.path, as_attachment=True)

@app.route("/logout")
def logout():
	session.pop("user", None)
	flash("Logged out", "info")
	return redirect(url_for("login")) 

if __name__ == "__main__":
	db.create_all()
	app.run(debug=True)