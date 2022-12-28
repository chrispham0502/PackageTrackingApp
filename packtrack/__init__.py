import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///packtrack.db'



dbURL = os.getenv('DB_URL')

app.config['SQLALCHEMY_DATABASE_URI'] = dbURL
db = SQLAlchemy(app)

app.secret_key = os.getenv("SECRET_KEY")

from packtrack import routes