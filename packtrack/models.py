from datetime import datetime
import email
from email.policy import default
from enum import unique
from pydoc import describe
from packtrack import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    packages = db.relationship('Package', secondary = 'link', lazy = True, overlaps = "users")

    def __repr__(self):
        return f"User('{self.id}', '{self.email}')"
        
class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carrier_code = db.Column(db.String(50), nullable = False)
    tracking_number = db.Column(db.String(50), unique=True, nullable = False)
    users = db.relationship('User', secondary = 'link', lazy = True)

    def __repr__(self):
        return f"Package('{self.id}', '{self.tracking_number}')"

# Link packages and emails to have a many-to-many relationship
class Link(db.Model):
    user_id = db.Column(db.Integer,  db.ForeignKey('user.id'), primary_key = True )
    package_id = db.Column(db.Integer,  db.ForeignKey('package.id'), primary_key = True )
    package_name = db.Column(db.String(100))