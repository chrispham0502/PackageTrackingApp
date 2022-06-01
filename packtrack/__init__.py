import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///packtrack.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://shhegbwfloylkc:ec9cd3e626bf2ca4122093da55ead04cf26d94058883706eff51c230f074f29a@ec2-34-227-120-79.compute-1.amazonaws.com:5432/dc7qnifqan4ln0'
db = SQLAlchemy(app)

app.secret_key = os.getenv("SECRET_KEY")

from packtrack import routes