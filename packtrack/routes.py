import email
import re
import smtplib
from email.message import EmailMessage
from struct import pack
from flask import render_template, url_for, flash, redirect, request, Response, session
from packtrack import app
from packtrack import db
from packtrack import methods
from packtrack.models import User, Package
import json
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

packtrack_email_address = os.environ.get('PYTHON_GMAIL_ADDRESS')
packtrack_email_password = os.environ.get('PYTHON_GMAIL_PASSWORD')


# Home Page
@app.route("/")
def home():
  return render_template("home.html")

# Tracking Page
@app.route('/track', methods=['GET'])
def track():

    try:
      session['carrierCode'] = methods.getCarrierCode(request.args.get('carrier'))
      session['trackingNumber'] = request.args.get('trackingNum')

      packageData = methods.getPackageData(session['carrierCode'], session['trackingNumber'])

      packageStatus =  packageData['status_description'].upper()
      packageStatusDescription = packageData["carrier_status_description"]

      events = packageData['events']

      for event in events:
        event['event_date'] = methods.datetimeConvert(event['occurred_at'], '%Y-%m-%dT%H:%M:%SZ', '%A, %d %B %Y')
        event['event_time'] = methods.datetimeConvert(event['occurred_at'], '%Y-%m-%dT%H:%M:%SZ', '%I:%M %p')

      latest_event = events[0]
      first_event = events[-1]

      eventNum = len(events)
      
      # If there's only one event
      if eventNum == 1:
        return render_template("track.html", case = "one",latest_event = latest_event, status = packageStatus, status_description = packageStatusDescription)
      
      # There are more than one event
      events = events[1:eventNum-1]
      return render_template("track.html", case = "many", first_event = first_event, latest_event = latest_event, events = events,  status = packageStatus, status_description = packageStatusDescription)
    except:
      return redirect("/error")

# Update Page
@app.route("/update", methods = ['POST'])
def update():
  packageName = request.form['packageName']
  email = request.form['email']

  # See if package and user already exist in db
  package = methods.getPackageByTrackingNumber(session['trackingNumber'])
  user = methods.getUserByEmail(email)

  # If user exist, check for package
  if user:
    # If package exist, see if the user is already in the mailing list, if not, add
    if package:
      if user not in package.users:
        package.users.append(user)
      else:
        return render_template("update.html", packageName = package.name, email = email, inlist = True)
    # If package doesn't exist, create new package then add
    else:
      package = Package(carrier_code = session['carrierCode'], tracking_number = session['trackingNumber'], name = packageName)
      package.users.append(user)
      db.session.add(package)
  # If user doesn't exit, create new user
  else:
    user = User(email=email)
    db.session.add(user)
    # If package doesn't exist, create new package
    if not package:
      package = Package(carrier_code = session['carrierCode'], tracking_number = session['trackingNumber'], name = packageName)
    package.users.append(user)
    db.session.add(package)

  db.session.commit()

  return render_template("update.html", packageName = packageName, email = email, inlist = False)

# Error Page
@app.route("/error")
def error():
  return render_template("error.html")

# Webhook Handler
@app.route('/webhook', methods=['POST'])
def respond():

    payload = request.json

    # Get tracking number and lastest tracking event from payload
    tracking_number = payload["data"]["tracking_number"]
    lastest_event = payload["data"]["events"][0]
    status = payload["data"]["status_code"]
    status_description = payload["data"]['status_description']

    body = lastest_event['occurred_at'][:10]  + ' - ' + lastest_event['occurred_at'][11:-4] + '\n' + \
    lastest_event['description'] +  '\n' + lastest_event['city_locality'] + ' - ' + lastest_event['state_province']

    # Get package in db
    package = methods.getPackageByTrackingNumber(tracking_number)

    for user in package.users:
      print("\nPackage Update" + package.name + status + "\n\n"+body + "\n\nFrom: " + packtrack_email_address + " - To: " + user.email)

    # msg = EmailMessage()
    # msg['Subject'] = 'Pakage Update'

    # for email in package.emails:
    #   msg['To'] = email
    #   msg.set_content(body)

    #   with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    #     smtp.login(packtrack_email_address, packtrack_email_password)
    #     smtp.send_message(msg)

    # If package is delivered then delete in database

    if status == "DE":
      db.session.delete(package)
      db.session.commit()

    return Response(status=200)