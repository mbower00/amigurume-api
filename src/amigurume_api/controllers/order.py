from src.amigurume_api.db import Order, User, OrderProduct, Product, ProductType, db
from sqlalchemy import select
from src.amigurume_api.utils import package_result

class OrderController:
    def __init__(self):
        pass

    def _place_products_in_order(self, session, order):
        # get the OrderProducts (with Product info)
        order_product_result = session.execute(
            select(OrderProduct, Product, ProductType.type)
            .join(Product, OrderProduct.product_id == Product.id)
            .join(ProductType, Product.product_type_id == ProductType.id)
            .where(OrderProduct.order_id == order["id"])
        ).all()
        order_products = package_result(order_product_result, ["product", "type"])
        # adjust type attribute location
        # TODO: consider changing this to happen above, for efficiency.
        for order_product in order_products:
            if order_product["type"]:
                order_product["product"]["type"] = order_product["type"]
            del order_product["type"]
        # add order_products to their Order
        order["ordered_products"] = order_products

        
    def get_all_orders(self):
        with db.session() as session:
            # Get the Orders (with their User)
            order_result = session.execute(
                select(Order, User)
                .join(User, Order.user_id == User.id)
            ).all()
            orders = package_result(order_result, ["user"])

            for order in orders:
                self._place_products_in_order(session, order)

            return orders
    
    def get_order(self, id):
        with db.session() as session:
            # Get the Order (with their User)
            orderResult = session.execute(
                select(Order, User)
                .join(User, Order.user_id == User.id)
                .where(Order.id == id)
            ).first()
            order = package_result(orderResult, ["user"])

            self._place_products_in_order(session, order)

            return order