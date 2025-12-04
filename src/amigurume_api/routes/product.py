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
        @jwt_required()
        def get_all_products():
            if check_clearance(get_jwt_identity(),  ['user', 'admin']):
                return self.controller.get_all_products()
            return {'message': 'Admin or user clearance required'}, 400

        @self.app.route("/product/types")
        @jwt_required()
        def get_product_types():
            if check_clearance(get_jwt_identity(), ['user', 'admin']):
                return self.controller.get_product_types()
            return {'message': 'Admin or user clearance required'}, 400
        
        @self.app.route("/product/<int:id>")
        @jwt_required()
        def get_product(id):
            if check_clearance(get_jwt_identity(), ['user', 'admin']):
                return self.controller.get_product(id)
            return {'message': 'Admin or user clearance required'}, 400
        
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
