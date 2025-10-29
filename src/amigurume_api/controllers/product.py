from flask import request
from sqlalchemy import select
from src.amigurume_api.utils import package_result
from src.amigurume_api.db import Product, ProductType, db

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
            result = session.execute(select(Product).where(Product.id == id)).first()
            return package_result(result)
        
    def add_product(self):
        data = request.get_json()
        given_type = data['type'].lower().strip()
        
        with db.session() as session:
            # check if given_type exists in db
            find_type = package_result(session.execute(
                    select(ProductType)
                    .where(ProductType.type == given_type)
                ).first())
            type_id = 0
            if find_type:
                # type found
                type_id = find_type["id"]
            else:
                # add new type
                product_type = ProductType(type=given_type)
                session.add(product_type)
                session.commit()
                type_id = product_type.id

            # add new product with correct type
            product = Product(
                name = data.get("name"),
                quantity = data.get("quantity"),
                description = data.get("description"),
                product_type_id = type_id
            )
            session.add(product)
            session.commit()
            return {"id": product.id}
            
            
            
