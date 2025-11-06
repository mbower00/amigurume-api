# using code from https://www.youtube.com/watch?v=aX-ayOb_Aho

from flask import Flask
from src.amigurume_api.controllers.order import OrderController
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.amigurume_api.utils.auth import check_clearance


class OrderRouter:
    def __init__(self, app: Flask):
        self.app = app
        self.controller = OrderController()

    def create_all(self):
        @self.app.route("/orders")
        @jwt_required()
        def get_all_orders():
            if check_clearance(get_jwt_identity()):
                return self.controller.get_all_orders()
            return {'message': 'Admin clearance required'}, 400

        @self.app.route("/orders/user/<int:user_id>")
        @jwt_required()
        def get_orders_for_user(user_id):
            if check_clearance(get_jwt_identity(), ['admin']):
                return self.controller.get_orders_for_user(user_id)
            return {'message': 'Admin clearance required'}, 400
        
        @self.app.route("/orders/my")
        @jwt_required()
        def get_orders_for_current_user():
            if check_clearance(get_jwt_identity(), ['admin', 'user']):
                return self.controller.get_orders_for_current_user()
            return {'message': 'Admin or user clearance required'}, 400
        
        @self.app.route("/order/<int:id>")
        @jwt_required()
        def get_order(id):
            if check_clearance(get_jwt_identity()):
                return self.controller.get_order(id)
            return {'message': 'Admin clearance required'}, 400
        
        @self.app.route("/order", methods=["POST"])
        @jwt_required()
        def add_order():
            if check_clearance(get_jwt_identity(), ['admin', 'user']):
                return self.controller.add_order()
            return {'message': 'Admin or user clearance required'}, 400
        
        @self.app.route("/order/fulfill/<int:id>", methods=["PATCH"])
        @jwt_required()
        def fulfill_order(id):
            if check_clearance(get_jwt_identity()):
                return self.controller.fulfill_order(id)
            return {'message': 'Admin clearance required'}, 400
        
        @self.app.route("/order/<int:id>", methods=["DELETE"])
        @jwt_required()
        def delete_order(id):
            if check_clearance(get_jwt_identity()):
                return self.controller.delete_order(id)
            return {'message': 'Admin clearance required'}, 400