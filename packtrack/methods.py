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

def processUser(email_address):

    # attempt to get user from the database
    user = User.query.filter_by(email = email_address).first()

    # return if exist
    if user:
        return user

    # if not create new user
    new_user = User(email = email_address)
    db.session.add(new_user)
    db.session.commit()

    return new_user

def processPackage(carrier_code, tracking_number, name, description):
    
    # attempt to get package from the database
    package = Package.query.filter_by(carrier_code = carrier_code, tracking_number = tracking_number).first()

    # return if exist
    if package:
        return package

    # if not create new package
    new_package = Package(carrier_code = carrier_code, tracking_number = tracking_number, name = name, description = description)
    db.session.add(new_package)
    db.session.commit()
    
    return new_package


# def processEvents(package_id, eventsList):
#     for event in eventsList:
#         e_package_id = package_id
#         e_occurred_at = datetime.strptime(event['occurred_at'], '%Y-%m-%dT%H:%M:%SZ')
#         e_description = event['description']
#         e_city = event['city_locality']
#         e_state = event['state_province']
        
#         new_event = Event(package_id = e_package_id, occurred_at=e_occurred_at, description = e_description, \
#             city = e_city, state = e_state)
        
        # db.session.add(new_event)

def getPackageData(carrier_id, tracking_number):
    URL = getURL(carrier_id, tracking_number)
    packageData = processURL(URL)
    
    return packageData

def getPackageByTrackingNumber(tracking_number):
    package = Package.query.filter_by(tracking_number = tracking_number).first()
    return package

def subscribePackage(carrierCode, trackingNumber):
    URL = "https://api.shipengine.com/v1/tracking/start?carrier_code=" + carrierCode + "&tracking_number=" + trackingNumber
    payload={}
    headers = {
        'Host': 'api.shipengine.com',
        'API-Key': API_KEY
    }

    response = requests.request("POST", URL, headers=headers, data=payload)
    
    print(response.text)


def unsubscribePackage(carrierCode, trackingNumber):
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
    return datetime_obj.strftime(dateStringOutputFormat).upper()




# def sendUpdateEmail(package):


'''

event['occurred_at'], '%Y-%m-%dT%H:%M:%SZ'

from packtrack import db
from packtrack import methods
from packtrack.models import Package, User, Link
db.drop_all()
db.create_all()

e1 = Email(email_address = 'test1@gmail.com')

tmp = Package.query.filter_by(tracking_number = tracking_number).first()
getPackageByTrackingNumber(tracking_number)


trackingNumber = "9400111202508526786562"
carrierCode = "usps"
methods.processPackage(carrierCode, trackingNumber, 'Test Name', 'alo alo')

u1 = User(email_address = 'test1@gmail.com')
e = Email(email_address = 'test2@gmail.com')
e3 = Email(email_address = 'test3@gmail.com')
p1 = Package(carrier_code = "usps", tracking_number = "123", name = "test1", description = "test package")

'''
