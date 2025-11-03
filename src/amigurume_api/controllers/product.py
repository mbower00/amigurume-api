from flask import request
from sqlalchemy import delete, select, update
from src.amigurume_api.utils import package_result
from src.amigurume_api.db import Product, ProductType, db, OrderProduct

class ProductController:
    def __init__(self):
        pass
        
    def get_all_products(self):
        with db.session() as session:
            result = session.execute(
                select(Product, ProductType.type)
                .join(ProductType, Product.product_type_id == ProductType.id)
            ).all()
            return package_result(result, ['type'])
        
    def get_product_types(self):
        with db.session() as session:
            result = session.execute(select(ProductType)).all()
            return package_result(result)
        
    def get_product(self, id):
        with db.session() as session:
            result = session.execute(
                select(Product, ProductType.type)
                .join(ProductType, Product.product_type_id == ProductType.id)
                .where(Product.id == id)
            ).first()
            return package_result(result, ['type'])

    def add_product(self):
        data = request.get_json()
        with db.session() as session:
            type_id = self._add_or_find_type(session, data['type'])

            # add new product with correct type
            product = Product(
                name = data.get("name"),
                stock = data.get("stock"),
                description = data.get("description"),
                product_type_id = type_id
            )
            session.add(product)
            session.commit()
            return {"id": product.id}
    
    def update_product(self, id):
        data = request.get_json()
        data['id'] = id
        with db.session() as session:
            # handle no such id
            if not session.execute(
                select(Product)
                .where(Product.id == id)
            ).all():
                return {'message': f'The product (id: {id}) was not found'}, 400
            # handle type
            if 'type' in data:
                data['product_type_id'] = self._add_or_find_type(session, data['type'])
                del data['type']
            # update
            session.execute(update(Product), [data])
            session.commit()
            return {'message': f'Updated product (id: {id})'}
    
    def delete_product(self, id):
        with db.session() as session:
            if session.execute(
                select(OrderProduct)
                .where(OrderProduct.product_id == id)
            ).all():
                return {'message': f'The product (id: {id}) cannot be deleted. It is in order(s).'}, 400
            result = session.execute(
                delete(Product)
                .where(Product.id == id)
                .returning(Product)
            )
            session.commit()
            if result.all():
                return {'message': f'Deleted product (id: {id})'}
            else:
                return {'message': 'No product deleted.'}, 400
            
    def _add_or_find_type(self, session, type):
        type = type.lower().strip()
        # check if given_type exists in db
        find_type = package_result(session.execute(
                select(ProductType)
                .where(ProductType.type == type)
            ).first())
        if find_type:
            # type found
            return find_type["id"]
        # add new type
        product_type = ProductType(type = type)
        session.add(product_type)
        session.commit()
        return product_type.id
