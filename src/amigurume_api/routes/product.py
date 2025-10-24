from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from src.amigurume_api.controllers.product import ProductController

class ProductRouter:
    def __init__(self, app: Flask):
        self.app = app
        self.controller = ProductController()

    def create_all(self):
        @self.app.route("/products")
        def get_all_products():
            return self.controller.get_all_products()

        @self.app.route("/product/types")
        def get_product_types():
            return self.controller.get_product_types()
        
        @self.app.route("/product/<int:id>")
        def get_product(id):
            return self.controller.get_product(id)
        
        @self.app.route("/product", methods=["POST"])
        def add_product():
            return self.controller.add_product()