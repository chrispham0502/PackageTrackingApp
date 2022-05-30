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
        
#p1 = Package(tracking_number = '9400111202508526786562', status_code = 'DE', status_description = 'Delivered')

# class Event(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable = False)
#     occurred_at = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
#     description = db.Column(db.Text, nullable = False)
#     city = db.Column(db.String(100))
#     state = db.Column(db.String(10))

#     def __repr__(self):
#         return f"Event('{self.occurred_at}', '{self.description}')"

# class Email(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email_address = db.Column(db.String(100), nullable = False)
#     packages = db.relationship('Package', secondary = 'link', lazy = True, overlaps = "emails")

#     def __repr__(self):
#         return f"Email('{self.id}', '{self.email_address}')"


# Link packages and emails to have a many-to-many relationship
class Link(db.Model):
    user_id = db.Column(db.Integer,  db.ForeignKey('user.id'), primary_key = True )
    package_id = db.Column(db.Integer,  db.ForeignKey('package.id'), primary_key = True )
    package_name = db.Column(db.String(100))
    



#e1 = Event(package_id = 1, description = 'package delivered', city = 'Los An', state = 'CA')