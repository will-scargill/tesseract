

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
			if foundUser == None:
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
			return render_template("index.html", username=session["user"]),403	
	else:
		return redirect(url_for("login"))

@app.route("/admin/accounts/delete/<userid>", methods=["GET"])
def deleteUser(userid):
	if "user" in session:
		found_users = users.query.filter_by(name=session["user"]).first()
		if found_users.admin == True:
			foundUser = users.query.filter_by(_id=userid).first()
			if foundUser == None:
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
			return render_template("index.html", username=session["user"]),403	
	else:
		return redirect(url_for("login"))