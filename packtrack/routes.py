import email
from flask import render_template, url_for, flash, redirect, request, Response, session
from packtrack import app
from packtrack import db
from packtrack import methods
from packtrack.models import User, Package
import json


@app.route("/", methods = ['POST', 'GET'])
def index():

  title = "Test App"
  if request.method == "POST":

    state = request.form['btn_identifier']

    if state == 'track_package':
      session['carrier'] = request.form['carrier']
      session['tracking_number'] = request.form['trackingNum']

      events = methods.getTrackingEvents(session['carrier'], session['tracking_number'])
    
      return render_template("index.html", title = title, events = events, state = state)

    else:
      session['package_name'] = request.form['name']
      session['package_description'] = request.form['description']
      session['email'] = request.form['email']

      new_user = methods.processUser(session['email'])

      new_package = methods.processPackage(session['carrier'], session['tracking_number'], session['package_name'], session['package_description'] )

      new_package.users.append(new_user)
      db.session.commit()

      methods.subscribePackage(session['carrier'], session['tracking_number'])
      
      return "Sending info of package " + session['package_name'] + session['package_description'] + session['tracking_number'] + " to: " +  session['email']

  else:
    db.drop_all()
    db.create_all()
    return render_template("index.html", title = title, state = 'load')


# Webhook Handler
@app.route('/webhook', methods=['POST'])
def respond():

    payload = request.json

    events = payload["event"]["body"]["data"]["events"]

    for lastest_event in events:
      print("\n\n" + lastest_event['occurred_at'][:10]  + ' - ' + lastest_event['occurred_at'][11:-4] + '\n' + \
      lastest_event['description'] +  '\n' + lastest_event['city_locality'] + ' - ' + lastest_event['state_province'] + "\n\n")

    return Response(status=200)