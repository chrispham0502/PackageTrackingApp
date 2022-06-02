from cProfile import run
from re import A
import requests
import json
from datetime import datetime
from packtrack.models import Package, User, Link
import os
from packtrack import db


API_KEY = os.environ.get('SHIPENGINE_API_KEY')

def get_URL(carrier_id, tracking_number):
    return "https://api.shipengine.com/v1/tracking?carrier_code=" + carrier_id + "&tracking_number=" + tracking_number

def process_URL(URL):
    payload={}
    headers = {
    'Host': 'api.shipengine.com',
    'API-Key': API_KEY
    }
    
    response = requests.request("GET", URL, headers=headers, data=payload).text
    response_data = json.loads(response)

    return response_data


def get_package_data(carrier_id, tracking_number):
    URL = get_URL(carrier_id, tracking_number)
    package_data = process_URL(URL)
    
    return package_data

def get_package_by_tracking_number(tracking_number):
    package = Package.query.filter_by(tracking_number = tracking_number).first()
    return package

def subscribe_package(package):
    carrier_code = package.carrier_code
    tracking_number = package.tracking_number
    URL = "https://api.shipengine.com/v1/tracking/start?carrier_code=" + carrier_code + "&tracking_number=" + tracking_number
    payload={}
    headers = {
        'Host': 'api.shipengine.com',
        'API-Key': API_KEY
    }

    response = requests.request("POST", URL, headers=headers, data=payload)
    
    print(response.text)


def unsubscribe_package(package):
    carrier_code = package.carrier_code
    tracking_number = package.tracking_number
    URL = "https://api.shipengine.com/v1/tracking/stop?carrier_code=" + carrier_code + "&tracking_number=" + tracking_number
    payload={}
    headers = {
        'Host': 'api.shipengine.com',
        'API-Key': API_KEY
    }

    response = requests.request("POST", URL, headers=headers, data=payload)

    print(response.text)


def get_carrier_code(carrier_name):

    carriers = {'USPS':'usps','UPS':'ups','FedEx':'fedex'}

    return carriers[carrier_name]

def datetime_convert(dateStringInput, dateStringInputFormat, dateStringOutputFormat):
    datetime_obj = datetime.strptime(dateStringInput, dateStringInputFormat)
    return datetime_obj.strftime(dateStringOutputFormat)

def get_user_by_email(email):
    user = User.query.filter_by(email = email).first()
    return user

def get_link(user, package):
    user_id = user.id
    package_id = package.id

    link = Link.query.filter_by(user_id = user_id, package_id = package_id).first()

    return link
