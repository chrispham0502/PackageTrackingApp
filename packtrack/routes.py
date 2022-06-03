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
      session['carrier_code'] = methods.get_carrier_code(request.args.get('carrier'))
      session['tracking_number'] = request.args.get('tracking_number').replace(" ","").lower()

      package_data = methods.get_package_data(session['carrier_code'], session['tracking_number'])

      package_status =  package_data['status_description'].upper()
      package_status_description = package_data["carrier_status_description"]

      events = package_data['events']

      for event in events:
        event['event_date'] = methods.datetime_convert(event['carrier_occurred_at'], '%Y-%m-%dT%H:%M:%S', '%A, %B %d %Y').upper()
        event['event_time'] = methods.datetime_convert(event['carrier_occurred_at'], '%Y-%m-%dT%H:%M:%S', '%I:%M %p').upper()

      latest_event = events[0]
      first_event = events[-1]

      event_num = len(events)
      
      # If there's only one event
      if event_num == 1:
        return render_template("track.html", case = "one",latest_event = latest_event, status = package_status, status_description = package_status_description)
      
      # There are more than one event
      events = events[1:event_num-1]
      return render_template("track.html", case = "many", first_event = first_event, latest_event = latest_event, events = events,  status = package_status, status_description = package_status_description)
    except:
      return redirect("/error")

# Update Page
@app.route("/update", methods = ['POST'])
def update():
  package_name = request.form['package_name']
  email = request.form['email']

  # See if package and user already exist in db
  package = methods.get_package_by_tracking_number(session['tracking_number'])
  user = methods.get_user_by_email(email)

  # If user exist, check for package
  if user:
    # If package exist, see if the user is already in the mailing list, if not, add
    if package:
      if user not in package.users:
        package.users.append(user)
      else:
        link = methods.get_link(user, package)
        return render_template("update.html", package_name = link.package_name, email = email, inlist = True)
    # If package doesn't exist, create new package then add
    else:
      package = Package(carrier_code = session['carrier_code'], tracking_number = session['tracking_number'])
      package.users.append(user)
      db.session.add(package)
  # If user doesn't exit, create new user
  else:
    user = User(email=email)
    db.session.add(user)
    # If package doesn't exist, create new package
    if not package:
      package = Package(carrier_code = session['carrier_code'], tracking_number = session['tracking_number'])
    package.users.append(user)
    db.session.add(package)

  db.session.commit()

  link = methods.get_link(user, package)
  link.package_name = package_name

  db.session.commit()

  methods.subscribe_package(package)

  return render_template("update.html", package_name = package_name, email = email, inlist = False)

# Error Page
@app.route("/error")
def error():
  return render_template("error.html")

# Webhook Handler
@app.route('/webhook', methods=['POST'])
def respond():

    payload = request.json

    # Get tracking number and lastest tracking event from payload
    tracking_number = payload["data"]["tracking_number"].replace(" ","").lower()
    lastest_event = payload["data"]["events"][0]
    event_date = methods.datetime_convert(lastest_event['carrier_occurred_at'], '%Y-%m-%dT%H:%M:%S', '%A, %B %d %Y')
    event_time = methods.datetime_convert(lastest_event['carrier_occurred_at'], '%Y-%m-%dT%H:%M:%S', '%I:%M %p')
    status = payload["data"]["status_code"]
    status_description = payload["data"]['status_description']

    # Get package in db
    package = methods.get_package_by_tracking_number(tracking_number)
    
    for user in package.users:

      package_name = methods.get_link(user, package).package_name
      
      # Composing message subject
      subject = "Package Update"
      if package_name:
        subject += " - " + package_name
      subject += " - " + status_description
  
      # Composing message body
      body = "Update details of your package " + package_name + ":\n\n" + event_date  + '\n' + event_time + '\n' + lastest_event['description']
      if lastest_event['city_locality']:
        body += "\n" + lastest_event['city_locality']
        if lastest_event['state_province']:
          body += ' - ' + lastest_event['state_province']

      msg = EmailMessage()
      msg['Subject'] = subject
      msg['To'] = user.email
      msg.set_content(body)
 
      with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(packtrack_email_address, packtrack_email_password)
        smtp.send_message(msg)

    # If package is delivered then unsubscribe and delete in database
    if status == "DE":
      methods.unsubscribe_package(package)
      db.session.delete(package)
      db.session.commit()

    return Response(status=200)

