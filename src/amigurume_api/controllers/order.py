from src.amigurume_api.db import Order, db
from sqlalchemy import select
from src.amigurume_api.utils import package_result

class OrderController:
    def __init__(self):
        pass
        
    def get_all_orders(self):
        with db.session() as session:
            result = session.scalars(select(Order)).all()
            return package_result(result)
    
    def get_order(self, id):
        with db.session() as session:
            result = session.scalars(select(Order).where(Order.id == id)).first()
            return package_result(result)