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

packtrack_email_address = os.environ.get('PYTHON_GMAIL_ADDRESS')
packtrack_email_password = os.environ.get('PYTHON_GMAIL_PASSWORD')

@app.route("/", methods = ['POST', 'GET'])
def index():
  title = "Test App"
  if request.method == "POST":
    
    # get button request
    state = request.form['btn_identifier']

    # request to track package
    if state == 'track_package':
      session['carrier'] = request.form['carrier']
      session['tracking_number'] = request.form['trackingNum']

      events = methods.getTrackingEvents(session['carrier'], session['tracking_number'])
    
      return render_template("index.html", title = title, events = events, state = state)

    # request to subscribe to package update
    else:

      # get form details
      package_name = request.form['name']
      package_description = request.form['description']
      email = request.form['email']

      # process new user
      new_user = methods.processUser(email)

      # process new package
      new_package = methods.processPackage(session['carrier'], session['tracking_number'], package_name, package_description)

      # add user to package subscribe list
      new_package.users.append(new_user)

      db.session.commit()

      methods.subscribePackage(session['carrier'], session['tracking_number'])
      
      return "Sending info of package " + package_name + " to: " + email
  else:
    return render_template("index.html", title = title, state = 'load')


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