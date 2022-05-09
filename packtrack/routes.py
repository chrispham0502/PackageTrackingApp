from flask import render_template, url_for, flash, redirect, request, Response
from packtrack import app
from packtrack import db
from packtrack import methods
from packtrack.models import User, Package
import json


@app.route("/", methods = ['POST', 'GET'])
def index():
  title = "Test App"
  if request.method == "POST":
    carrier = request.form['carrier']
    tracking_number = request.form['trackingNum']

    package = methods.getPackageByTrackingNumber(tracking_number)

    # If package doesn't exist in database yet, process new package
    if package is None:
      title = "New Package"
      package = methods.processPackage(carrier, tracking_number)

    # If already existed then proceed
    else:
      title = "Old Package"

    events = package.events
    return render_template("index.html", title = title, events = events)

  else:
    return render_template("index.html", title = title)


@app.route('/webhook', methods=['POST'])
def respond():

    payload = request.json

    lastest_event = payload["event"]["body"]["data"]["events"][0]

    print("\n\n" + lastest_event['occurred_at'][:10]  + ' - ' + lastest_event['occurred_at'][11:-4] + '\n' + \
    lastest_event['description'] +  '\n' + lastest_event['city_locality'] + ' - ' + lastest_event['state_province'] + "\n\n")

    return Response(status=200)