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

        @self.app.route("/order/<int:id>")
        def get_order(id):
            return self.controller.get_order(id)