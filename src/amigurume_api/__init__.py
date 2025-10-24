# using code from: 
# - https://flask.palletsprojects.com/en/stable/quickstart/
# - https://flask.palletsprojects.com/en/stable/tutorial/factory/

from flask import Flask
from src.amigurume_api.db import db
from flask_sqlalchemy import SQLAlchemy
from src.amigurume_api.routes import Router
from src.amigurume_api.utils import package_result

def create_app():
    app = Flask(__name__)

    # below two lines from https://medium.com/@brodiea19/flask-sqlalchemy-how-to-upload-photos-and-render-them-to-your-webpage-84aa549ab39e
    # app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png"]
    # app.config["UPLOAD_PATH"] = "image_uploads"

    # connection string code comes from Google Gemini
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2:///amigurume_dev"

    db.init_app(app)

    with app.app_context():
        db.create_all()

    Router(app).create_all()
    
    return app