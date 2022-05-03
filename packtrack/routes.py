from flask import render_template, url_for, flash, redirect, request
from packtrack import app
from packtrack import db
from packtrack.models import User, Package


@app.route("/", methods = ['POST', 'GET'])
def index():
    title = "Test App"
    if request.method == "POST":
      test_name = request.form['name']
      test_email = request.form['email']
      test_password = request.form['password']
      new_test = User(username = test_name, email = test_email, password = test_password)

      try:
        db.session.add(new_test)
        db.session.commit()
        return render_template("index.html", title = title)

      except:
        return "Error"

    else:
      return render_template("index.html", title = title)
