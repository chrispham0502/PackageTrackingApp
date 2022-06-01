from cProfile import run
from re import A
import requests
import json
from datetime import datetime
from packtrack.models import Package, User, Link
import os
from packtrack import db


API_KEY = os.environ.get('SHIPENGINE_API_KEY')

def getURL(carrier_id, tracking_number):
    return "https://api.shipengine.com/v1/tracking?carrier_code=" + carrier_id + "&tracking_number=" + tracking_number

def processURL(URL):
    payload={}
    headers = {
    'Host': 'api.shipengine.com',
    'API-Key': API_KEY
    }
    
    response = requests.request("GET", URL, headers=headers, data=payload).text
    response_data = json.loads(response)

    return response_data


def getPackageData(carrier_id, tracking_number):
    URL = getURL(carrier_id, tracking_number)
    packageData = processURL(URL)
    
    return packageData

def getPackageByTrackingNumber(tracking_number):
    package = Package.query.filter_by(tracking_number = tracking_number).first()
    return package

def subscribePackage(package):
    carrierCode = package.carrier_code
    trackingNumber = package.tracking_number
    URL = "https://api.shipengine.com/v1/tracking/start?carrier_code=" + carrierCode + "&tracking_number=" + trackingNumber
    payload={}
    headers = {
        'Host': 'api.shipengine.com',
        'API-Key': API_KEY
    }

    response = requests.request("POST", URL, headers=headers, data=payload)
    
    print(response.text)


def unsubscribePackage(package):
    carrierCode = package.carrier_code
    trackingNumber = package.tracking_number
    URL = "https://api.shipengine.com/v1/tracking/stop?carrier_code=" + carrierCode + "&tracking_number=" + trackingNumber
    payload={}
    headers = {
        'Host': 'api.shipengine.com',
        'API-Key': API_KEY
    }

    response = requests.request("POST", URL, headers=headers, data=payload)

    print(response.text)


def getCarrierCode(carrierName):

    carriers = {'USPS':'usps','UPS':'ups','FedEx':'fedex'}

    return carriers[carrierName]

def datetimeConvert(dateStringInput, dateStringInputFormat, dateStringOutputFormat):
    datetime_obj = datetime.strptime(dateStringInput, dateStringInputFormat)
    return datetime_obj.strftime(dateStringOutputFormat)

def getUserByEmail(email):
    user = User.query.filter_by(email = email).first()
    return user

def getLink(user, package):
    user_id = user.id
    package_id = package.id

    link = Link.query.filter_by(user_id = user_id, package_id = package_id).first()

    return link
