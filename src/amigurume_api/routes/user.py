# Using code from https://www.youtube.com/watch?v=aX-ayOb_Aho
from flask import Flask
from src.amigurume_api.controllers.user import UserController
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.amigurume_api.utils.auth import check_clearance


class UserRouter:
    def __init__(self, app: Flask):
        self.app = app
        self.controller = UserController()

    def create_all(self):
        @self.app.route("/users")
        @jwt_required()
        def get_all_users():
            if check_clearance(get_jwt_identity()):
                return self.controller.get_all_users()
            return {'message': 'Admin clearance required'}, 400

        @self.app.route("/user/<int:id>")
        @jwt_required()
        def get_user(id):
            if check_clearance(get_jwt_identity()):
                return self.controller.get_user(id)
            return {'message': 'Admin clearance required'}, 400
        
        @self.app.route("/user/clearance/<int:id>", methods=["PATCH"])
        @jwt_required()
        def change_user_clearance(id):
            if check_clearance(get_jwt_identity()):
                return self.controller.change_user_clearance(id)
            return {'message': 'Admin clearance required'}, 400
        
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
        def refresh_user():
            return self.controller.refresh_user()
        
        @self.app.route("/user/log-out")
        @jwt_required()
        def log_out_user():
            return self.controller.log_out_user()