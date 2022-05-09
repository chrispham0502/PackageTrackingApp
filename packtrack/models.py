from datetime import datetime
import email
from email.policy import default
from enum import unique
from pydoc import describe
from packtrack import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(50), unique=True, nullable = False)
    status_code = db.Column(db.String(10), nullable = False)
    status_description = db.Column(db.String(100), nullable = False)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    events = db.relationship('Event', backref = 'package', lazy = True)
    emails = db.relationship('Email', secondary = 'link', lazy = True)

    def __repr__(self):
        return f"Package('{self.id}', '{self.tracking_number}')"

#p1 = Package(tracking_number = '9400111202508526786562', status_code = 'DE', status_description = 'Delivered')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable = False)
    occurred_at = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable = False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(10))

    def __repr__(self):
        return f"Event('{self.occurred_at}', '{self.description}')"

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(100), nullable = False)
    packages = db.relationship('Package', secondary = 'link', lazy = True, overlaps = "emails")

    def __repr__(self):
        return f"Email('{self.id}', '{self.email_address}')"


# Link packages and emails to have a many-to-many relationship
class Link(db.Model):
    package_id = db.Column(db.Integer,  db.ForeignKey('package.id'), primary_key = True )
    email_id = db.Column(db.Integer,  db.ForeignKey('email.id'), primary_key = True )



#e1 = Event(package_id = 1, description = 'package delivered', city = 'Los An', state = 'CA')