from cProfile import run
from re import A
import requests
import json
from datetime import datetime
from packtrack.models import Package, User, Link
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

def processPackage(carrier_id, tracking_number, name = None, description = None):
    URL = getURL(carrier_id, tracking_number)
    package_data = processURL(URL)
    p_tracking_number = package_data['tracking_number']
    p_status_code = package_data['status_code']
    p_status_description = package_data['status_description']
    p_name = name
    p_description = description
    new_package = Package(tracking_number = p_tracking_number, status_code = p_status_code, \
                     status_description = p_status_description, name = p_name, description = p_description)
    
    db.session.add(new_package)
    db.session.commit()

    tmp = Package.query.filter_by(tracking_number = p_tracking_number).first()
    
    events = package_data['events']

    processEvents (tmp.id, events)
    
    db.session.commit()

    return Package.query.filter_by(tracking_number = p_tracking_number).first()
    


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
