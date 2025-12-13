# using code from: 
# - https://flask.palletsprojects.com/en/stable/quickstart/
# - https://flask.palletsprojects.com/en/stable/tutorial/factory/
# - https://github.com/theskumar/python-dotenv#readme
# - https://www.youtube.com/watch?v=aX-ayOb_Aho
# - https://flask-cors.readthedocs.io/en/latest/

import os
from flask import Flask, request
from sqlalchemy import select
from src.amigurume_api.db import db, BlockedToken
from src.amigurume_api.jwt import jwt
from src.amigurume_api.routes import Router
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # using code copied from chatGPT https://chatgpt.com/c/691342fc-371c-832d-8eb1-71fcadf5972f
    CORS(app, origins=["https://admin.amigurume.me", "https://user.amigurume.me"], supports_credentials=True)
    # DEVTODO: change this for admin frontend dev
    # using code copied from chatGPT https://chatgpt.com/c/691342fc-371c-832d-8eb1-71fcadf5972f
    # CORS(app, origins=["https://admin.amigurume.me", "http://localhost:5173"], supports_credentials=True)

    # connection string code comes from Google Gemini
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DB_STRING']
    # using code from https://flask-jwt-extended.readthedocs.io/en/stable/options.html#jwt-secret-key
    app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']

    db.init_app(app)
    jwt.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_blocked_token(headers, data):
        with db.session() as session:
            return bool(session.execute(
                select(BlockedToken)
                .where(BlockedToken.jti == data['jti'])
            ).first())


    with app.app_context():
        db.create_all()

    Router(app).create_all()
    
    return app
