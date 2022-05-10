from cProfile import run
from re import A
import requests
import json
from datetime import datetime
from packtrack.models import Package, User, Link, Event
from packtrack import db

def getURL(carrier_id, tracking_number):
    return "https://api.shipengine.com/v1/tracking?carrier_code=" + carrier_id + "&tracking_number=" + tracking_number

def processURL(URL):
    payload={}
    headers = {
    'Host': 'api.shipengine.com',
    'API-Key': 'TEST_2dTAIchnrNr3xKwycD9+KpHeFFn4BJzHX28XK+MssZs'
    }
    
    response = requests.request("GET", URL, headers=headers, data=payload).text
    response_data = json.loads(response)

    return response_data

def processUser(email_address):
    new_user = User(email = email_address)
    db.session.add(new_user)
    db.session.commit()

    return new_user

def processPackage(carrier_code, tracking_number, name, description):
    
    new_package = Package(carrier_code = carrier_code, tracking_number = tracking_number, name = name, description = description)
    db.session.add(new_package)
    db.session.commit()
    
    return new_package


def processEvents(package_id, eventsList):
    for event in eventsList:
        e_package_id = package_id
        e_occurred_at = datetime.strptime(event['occurred_at'], '%Y-%m-%dT%H:%M:%SZ')
        e_description = event['description']
        e_city = event['city_locality']
        e_state = event['state_province']
        
        new_event = Event(package_id = e_package_id, occurred_at=e_occurred_at, description = e_description, \
            city = e_city, state = e_state)
        
        db.session.add(new_event)
    
def getTrackingEvents(carrier_id, tracking_number):
    URL = getURL(carrier_id, tracking_number)
    package_data = processURL(URL)
    
    events = package_data['events']

    return events

def getPackageByTrackingNumber(tracking_number):
    tmp = Package.query.filter_by(tracking_number = tracking_number).first()
    return tmp


# def dateConvert(dateString, dateStringFormat):
#     datetime_obj = datetime.strptime(dateString, dateStringFormat)
#     return datetime_obj


# def sendUpdateEmail(package):


'''
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
