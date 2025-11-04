# using code from: 
# - https://flask.palletsprojects.com/en/stable/quickstart/
# - https://flask.palletsprojects.com/en/stable/tutorial/factory/
# - https://github.com/theskumar/python-dotenv#readme
# - https://www.youtube.com/watch?v=aX-ayOb_Aho

import os
from dotenv import load_dotenv
from flask import Flask
from src.amigurume_api.db import db
from src.amigurume_api.jwt import jwt
from flask_sqlalchemy import SQLAlchemy
from src.amigurume_api.routes import Router
from src.amigurume_api.utils import package_result

def create_app():
    app = Flask(__name__)

    load_dotenv()

    # connection string code comes from Google Gemini
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DB_STRING']

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    Router(app).create_all()
    
    return app