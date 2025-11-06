# Using code from https://www.youtube.com/watch?v=aX-ayOb_Aho
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.amigurume_api.controllers.user import UserController
from flask_jwt_extended import jwt_required, get_jwt_identity

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
        
        @self.app.route("/user/clearance/<int:id>", methods=["PATCH"])
        def change_user_clearance(id):
            return self.controller.change_user_clearance(id)
        
        # Using code from https://www.youtube.com/watch?v=aX-ayOb_Aho
        @self.app.route("/user/sign-up", methods=["POST"])
        def sign_up_user():
            return self.controller.sign_up_user()
        
        # Using code from https://www.youtube.com/watch?v=aX-ayOb_Aho
        @self.app.route("/user/log-in", methods=["POST"])
        def log_in_user():
            return self.controller.log_in_user()
        
        # Using code from https://www.youtube.com/watch?v=aX-ayOb_Aho
        @self.app.route("/user/refresh")
        @jwt_required(refresh=True)
        def refresh_user():
            return self.controller.refresh_user()
        
        @self.app.route("/user/log-out")
        @jwt_required(verify_type=False)
        def log_out_user():
            return self.controller.log_out_user()