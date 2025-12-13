# using code from https://www.youtube.com/watch?v=aX-ayOb_Aho

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
        def get_all_products():
            return self.controller.get_all_products()
        
        # with help from ChatGPT. It said that using get was a problem. https://chatgpt.com/c/691342fc-371c-832d-8eb1-71fcadf5972f
        @self.app.route("/products/from", methods=["PATCH"])
        def get_all_products_from():
            return self.controller.get_all_products_from()
        
        @self.app.route("/product/types")
        def get_product_types():
            return self.controller.get_product_types()
        
        @self.app.route("/product/<int:id>")
        def get_product(id):
            return self.controller.get_product(id)
        
        @self.app.route("/product", methods=["POST"])
        @jwt_required()
        def add_product():
            if check_clearance(get_jwt_identity()):
                return self.controller.add_product()
            return {'message': 'Admin clearance required'}, 400
        
        @self.app.route("/product/image", methods=["POST"])
        @jwt_required()
        def add_product_image():
            if check_clearance(get_jwt_identity()):
                return self.controller.add_product_image()
            return {'message': 'Admin clearance required'}, 400
        
        @self.app.route("/product/<int:id>", methods=["PATCH"])
        @jwt_required()
        def update_product(id):
            if check_clearance(get_jwt_identity()):
                return self.controller.update_product(id)
            return {'message': 'Admin clearance required'}, 400
        
        @self.app.route("/product/<int:id>", methods=["DELETE"])
        @jwt_required()
        def delete_product(id):
            if check_clearance(get_jwt_identity()):
                return self.controller.delete_product(id)
            return {'message': 'Admin clearance required'}, 400
