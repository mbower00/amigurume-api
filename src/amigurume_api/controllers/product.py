# using code from https://www.youtube.com/watch?v=aX-ayOb_Aho
# using code from https://www.youtube.com/watch?v=d4CZf0QrY7kc
# using code from Gemini Cloud Assist chat

from flask import request
from sqlalchemy import delete, select, update
from src.amigurume_api.utils import package_result, get_order_by, get_direction
from src.amigurume_api.db import ImageName, Product, ProductType, db, OrderProduct
from google.cloud import storage

class ProductController:
    def __init__(self):
        pass
        
    def get_all_products(self):
        order_by = get_order_by(request, Product)
        direction = get_direction(request)
        with db.session() as session:
            result = session.execute(
                select(Product, ProductType.type)
                .join(ProductType, Product.product_type_id == ProductType.id)
                .order_by(getattr(getattr(Product, order_by), direction)())
            ).all()
            return package_result(result, ['type'])
        
    def get_all_products_from(self):
        ids = request.get_json()['ids']
        print(ids)
        order_by = get_order_by(request, Product)
        direction = get_direction(request)
        with db.session() as session:
            product = Product()
            result = session.execute(
                select(Product, ProductType.type)
                .join(ProductType, Product.product_type_id == ProductType.id)
                .where(Product.id.in_(ids))
                .order_by(getattr(getattr(Product, order_by), direction)())
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
        formatted_type = data["type"].lower().strip()
        with db.session() as session:
            type_id = self._add_or_find_type(session, data['type'])

            # add new product with correct type
            product = Product(
                name = data.get("name"),
                stock = data.get("stock"),
                description = data.get("description"),
                image_url = data.get("image_url"),
                price = data.get("price"),
                product_type_id = type_id
            )
            session.add(product)
            session.commit()
            return {"id": product.id, "type": formatted_type}
        
    # using code from:
    # - https://www.youtube.com/watch?v=d4CZf0QrY7kc
    # - Gemini Cloud Assist chat
    def add_product_image(self):
        image = request.files.get('image')

        # ensure correct type
        if not (image.filename.rsplit('.', 1)[1] in ['png', 'jpg', 'jpeg']):
            return {'message': 'File must be .png, .jpg, or .jpeg'}

        # create name
        with db.session() as session:
            image_name = ImageName()
            session.add(image_name)
            session.commit()
            file_name = f'{image_name.id}{image.filename}'
        
        try:
            storage_client = storage.Client()
            gcs_bucket = storage_client.bucket('amigurume')
            blob = gcs_bucket.blob(file_name)
            blob.upload_from_file(image.stream, content_type=image.content_type)
            url = blob.public_url
        except Exception as e:
            print(e)
            return {'message': f'Failed to add {image.filename}'}, 500

        return {'image_url': url} 
    
    def update_product(self, id):
        data = request.get_json()
        data['id'] = id
        try:
            formatted_type = data["type"].lower().strip()
        except KeyError:
            formatted_type = None
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
            return {'id': id, 'type': formatted_type}
    
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
