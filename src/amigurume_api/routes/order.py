from flask import Flask
from src.amigurume_api.controllers.order import OrderController

class OrderRouter:
    def __init__(self, app: Flask):
        self.app = app
        self.controller = OrderController()

    def create_all(self):
        @self.app.route("/orders")
        def get_all_orders():
            return self.controller.get_all_orders()

        @self.app.route("/orders/user/<int:user_id>")
        def get_orders_by_user(user_id):
            return self.controller.get_orders_by_user(user_id)
        
        @self.app.route("/order/<int:id>")
        def get_order(id):
            return self.controller.get_order(id)
        
        @self.app.route("/order", methods=["POST"])
        def add_order():
            return self.controller.add_order()
        
        @self.app.route("/order/fulfill/<int:id>", methods=["PATCH"])
        def fulfill_order(id):
            return self.controller.fulfill_order(id)
        
        @self.app.route("/order/<int:id>", methods=["DELETE"])
        def delete_order(id):
            return self.controller.delete_order(id)