from flask import Flask
from src.amigurume_api.controllers.product import ProductController
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.amigurume_api.utils.auth import check_clearance

class ProductRouter:
    def __init__(self, app: Flask):
        self.app = app
        self.controller = ProductController()

    def create_all(self):
        @self.app.route("/products")
        @jwt_required()
        def get_all_products():
            if check_clearance(get_jwt_identity()):
                return self.controller.get_all_products()
            return {'message': 'Admin clearance required'}, 400

        @self.app.route("/product/types")
        def get_product_types():
            return self.controller.get_product_types()
        
        @self.app.route("/product/<int:id>")
        def get_product(id):
            return self.controller.get_product(id)
        
        @self.app.route("/product", methods=["POST"])
        def add_product():
            return self.controller.add_product()
        
        @self.app.route("/product/<int:id>", methods=["PATCH"])
        def update_product(id):
            return self.controller.update_product(id)
        
        @self.app.route("/product/<int:id>", methods=["DELETE"])
        def delete_product(id):
            return self.controller.delete_product(id)
