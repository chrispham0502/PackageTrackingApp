import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///packtrack.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://akutllistguvct:2c13ac7ac59a91da802005aca1089a37ce9eb79f7e72e1d73149d97690fb8a23@ec2-54-175-79-57.compute-1.amazonaws.com:5432/dcj0uri5cjocka'
db = SQLAlchemy(app)

app.secret_key = os.getenv("SECRET_KEY")

from packtrack import routes