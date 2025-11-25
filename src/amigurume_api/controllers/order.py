# using code from https://www.youtube.com/watch?v=aX-ayOb_Aho

from src.amigurume_api.db import Order, User, OrderProduct, Product, ProductType, db
from flask import request
from sqlalchemy import delete, select, update, and_
from src.amigurume_api.utils import package_result, get_order_by, get_direction
from datetime import datetime, timezone
from flask_jwt_extended import get_jwt_identity

class OrderController:
    def __init__(self):
        pass

    def get_all_orders(self):
        order_by = get_order_by(request, Order)
        direction = get_direction(request)
        filter_func = self._get_filter()
        with db.session() as session:
            # Get the Orders (with their User)
            order_result = session.execute(
                select(Order, User)
                .join(User, Order.user_id == User.id)
                .where(filter_func())
                .order_by(getattr(getattr(Order, order_by), direction)())
            ).all()
            orders = package_result(order_result, ["user"])

            for order in orders:
                del order['user']['password']
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

            if order:
                del order['user']['password']
            self._place_products_in_order(session, order)

            return order
        
    def get_orders_for_user(self, user_id):
        order_by = get_order_by(request, Order)
        direction = get_direction(request)
        filter_func = self._get_filter()
        with db.session() as session:
            # Get the user to return
            user_result = session.execute(
                select(User)
                .where(User.id == user_id)
            ).first()
            if not user_result:
                return {"message": "User not found"}, 400
            user = package_result(user_result)
            # Get the orders
            order_result = session.execute(
                select(Order)
                .where(and_(
                    Order.user_id == user_id,
                    filter_func()
                ))
                .order_by(getattr(getattr(Order, order_by), direction)())
            ).all()
            orders = package_result(order_result)
            # add the products
            for order in orders:
                self._place_products_in_order(session, order)
        del user['password']
        return {'user': user, 'orders': orders}
        
    def get_orders_for_current_user(self):
        username = get_jwt_identity()
        with db.session() as session:
            # check that the user exsists
            user_result = session.execute(
                select(User)
                .where(User.username == username)
            ).first()
            if not user_result:
                return {"message": "User not found"}, 400
            user_id = package_result(user_result)['id']
        return self.get_orders_for_user(user_id)
        
    def add_order(self):
        data = request.get_json()

        # ensure there is only one of each product id
        ids = []
        for ordered_product in data["ordered_products"]:
            if ordered_product["id"] in ids:
                return {"message": "Cannot have duplicate products. Use quantity instead."}, 400
            ids.append(ordered_product["id"])

        username = get_jwt_identity()
        with db.session() as session:
            # check that the user exsists
            user_result = session.execute(
                select(User)
                .where(User.username == username)
            ).first()
            if not user_result:
                return {"message": "User not found"}, 400
            user_id = package_result(user_result)['id']
            
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
                user_id = user_id,
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
        
        return {'fulfilled': fulfilled}
    
    def delete_order(self, id):
        with db.session() as session:
            # Check if fulfilled
            order_select = session.execute(select(Order).where(Order.id == id)).first()
            order = package_result(order_select)
            if not order:
                return {'message': 'No order found to delete.'}, 400
            if not order['fulfilled']:
                # Get all associated orderProducts
                order_products_select = session.execute(select(OrderProduct).where(OrderProduct.order_id == id)).all()
                order_products = package_result(order_products_select)
                # Restock products
                for order_product in order_products:
                    product_select = session.execute(select(Product).where(Product.id == order_product["product_id"])).first()
                    product = package_result(product_select)
                    new_stock = product["stock"] + order_product["quantity"]
                    session.execute(
                        update(Product)
                        .where(Product.id == order_product["product_id"])
                        .values(stock = new_stock)
                    )
                    session.commit()
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
    
    def _get_filter(self):
        # filter_arg = request.args.get('filter')
        # if filter_arg:
        #     if filter_arg not in ['fulfilled', 'unfulfilled']:
        #         filter_arg = None
        # return filter_arg
        filter_arg = request.args.get('filter')
        filter_func = lambda : True
        if filter_arg == 'fulfilled':
            filter_func = lambda : Order.fulfilled != None
        if filter_arg == 'unfulfilled':
            filter_func = lambda : Order.fulfilled == None
        return filter_func