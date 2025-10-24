from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.amigurume_api.routes.product import ProductRouter
from src.amigurume_api.routes.user import UserRouter
from src.amigurume_api.routes.order import OrderRouter

class Router:
    def __init__(self, app: Flask):
        self.app : Flask = app
        self.product_router = ProductRouter(app)
        self.user_router = UserRouter(app)
        self.order_router = OrderRouter(app)
    
    def create_all(self):
        @self.app.route("/")
        def hello():
            return { "msg" : "hello" }
        
        self.product_router.create_all()
        self.user_router.create_all()
        self.order_router.create_all()
        
        