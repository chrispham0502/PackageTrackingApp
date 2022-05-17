import email
import re
import smtplib
from email.message import EmailMessage
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



@app.route("/", methods = ['POST', 'GET'])
def home():
  if request.method == "POST":
    
      session['carrierCode'] = methods.getCarrierCode(request.form['carrier'])
      session['trackingNumber'] = request.form['trackingNum']

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
        return render_template("track.html", case = "one",lastest_event = latest_event, status = packageStatus)
      
      # There are more than one event
      events = events[1:eventNum-1]
      return render_template("track.html", case = "many", first_event = first_event, latest_event = latest_event, events = events,  status = packageStatus, status_description = packageStatusDescription)
        
  return render_template("home.html")

    # request to subscribe to package update
  #   else:

  #     # get form details
  #     package_name = request.form['name']
  #     package_description = request.form['description']
  #     email = request.form['email']

  #     # process new user
  #     new_user = methods.processUser(email)

  #     # process new package
  #     new_package = methods.processPackage(session['carrier'], session['tracking_number'], package_name, package_description)

  #     # add user to package subscribe list
  #     new_package.users.append(new_user)

  #     db.session.commit()

  #     methods.subscribePackage(session['carrier'], session['tracking_number'])
      
  #     return "Sending info of package " + package_name + " to: " + email
  # else:
    
  #   carriers = ['USPS', 'UPS', 'FedEx']

  return render_template("home.html")

@app.route('/track', methods=['POST', 'GET'])
def track():
  return render_template("track.html")

# Webhook Handler
@app.route('/webhook', methods=['POST'])
def respond():

    payload = request.json

    tracking_number = payload["data"]["tracking_number"]
    lastest_event = payload["data"]["events"][0]

    body = lastest_event['occurred_at'][:10]  + ' - ' + lastest_event['occurred_at'][11:-4] + '\n' + \
    lastest_event['description'] +  '\n' + lastest_event['city_locality'] + ' - ' + lastest_event['state_province']

    package = methods.getPackageByTrackingNumber(tracking_number)

    for user in package.users:
      print("\nSending message: \n\n" + body + "\n\nFrom: " + packtrack_email_address + " - To: " + user.email)

    # msg = EmailMessage()
    # msg['Subject'] = 'Pakage Update'

    # for email in package.emails:
    #   msg['To'] = email
    #   msg.set_content(body)

    #   with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    #     smtp.login(packtrack_email_address, packtrack_email_password)
    #     smtp.send_message(msg)

    return Response(status=200)