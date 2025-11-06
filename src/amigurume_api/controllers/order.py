from src.amigurume_api.db import Order, User, OrderProduct, Product, ProductType, db
from flask import request
from sqlalchemy import delete, select, update
from src.amigurume_api.utils import package_result
from datetime import datetime, timezone

class OrderController:
    def __init__(self):
        pass

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
        
    def get_orders_by_user(self, user_id):
        with db.session() as session:
            # Get the user to return
            user_result = session.execute(
                select(User)
                .where(User.id == user_id)
            ).first()
            user = package_result(user_result)
            # Get the orders
            order_result = session.execute(
                select(Order)
                .where(Order.user_id == user_id)
            ).all()
            orders = package_result(order_result)
            # add the products
            for order in orders:
                self._place_products_in_order(session, order)

            return {'user': user, 'orders': orders}
        
    def add_order(self):
        data = request.get_json()
        with db.session() as session:
            # check that the user exsists
            if not session.execute(
                select(User)
                .where(User.id == data['user_id'])
            ).first():
                return {"message": "User not found"}, 400
            
            # check that each ordered product:
            # # exsists
            # # has enough stock
            for ordered_product in data["ordered_products"]:
                product_result = session.execute(
                    select(Product)
                    .where(Product.id == ordered_product["id"])
                ).first()
                if not product_result:
                    return {"message": f"Product (id: {ordered_product['id']}) not found"}, 400
                product = package_result(product_result)
                if ordered_product['quantity'] > product['stock']:
                    return {"message": f"Not enough product (id: {ordered_product['id']}) in stock (in stock: {product['stock']}, ordered: {ordered_product['quantity']})" }, 400
                else:
                    # store new stock for below update
                    ordered_product['new_stock'] = product['stock'] - ordered_product['quantity']
            
            order_products = []

            # this is a seperate loop so that errors can be caught before updates
            # update the stock of each ordered product
            # and populate order_products 
            for ordered_product in data["ordered_products"]:
                session.execute(
                    update(Product)
                    .where(Product.id == ordered_product['id'])
                    .values(stock = ordered_product['new_stock'])
                )
                order_products.append(OrderProduct(
                    product_id = ordered_product['id'],
                    quantity = ordered_product['quantity'],
                ))

            # create the Order with OrderProducts
            order = Order(
                user_id = data["user_id"],
                cart = order_products
            )
            session.add(order)
            session.commit()
            return {"id": order.id}
        
    def fulfill_order(self, id):
        fulfilled = datetime.now(timezone.utc)
        try:
            to_null = request.args['to-null']
            if to_null != '0':
                fulfilled = None
        except KeyError:
            pass
        
        with db.session() as session:
            result = session.execute(
                update(Order)
                .where(Order.id == id)
                .values(fulfilled = fulfilled)
                .returning(Order)
            )
            session.commit()
            if not result.all():
                return {'message': 'No order updated.'}, 400
        
        msg_suffix = f'fulfilled on {fulfilled.strftime("%m/%d/%Y %I:%M %p")} UTC' if fulfilled else 'set to unfulfilled'
        return {'message': f'Order (id: {id}) {msg_suffix}'}
    
    def delete_order(self, id):
        with db.session() as session:
            # Delete all associated orderProducts
            session.execute(
                delete(OrderProduct)
                .where(OrderProduct.order_id == id)
            )
            session.commit()
            # Delete the Order
            result = session.execute(
                delete(Order)
                .where(Order.id == id)
                .returning(Order)
            )
            session.commit()
            if result.all():
                return {'message': f'Deleted order (id: {id})'}
            else:
                return {'message': 'No order deleted.'}, 400
    
    def _place_products_in_order(self, session, order):
        if not order: return
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