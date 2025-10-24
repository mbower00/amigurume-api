from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.amigurume_api.controllers.user import UserController

class UserRouter:
    def __init__(self, app: Flask):
        self.app = app
        self.controller = UserController()

    def create_all(self):
        @self.app.route("/users")
        def get_all_users():
            return self.controller.get_all_users()

        @self.app.route("/user/<int:id>")
        def get_user(id):
            return self.controller.get_user(id)