from flask_sqlalchemy import SQLAlchemy
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str]
    clearance = mapped_column(ENUM('user', 'admin', name='clearance'))

class ProductType(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(unique=True)

class Product(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    quantity: Mapped[int]
    description: Mapped[Optional[str]]
    image_path: Mapped[Optional[str]]
    product_type_id = mapped_column(ForeignKey("product_type.id"))

class Order(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    created = mapped_column(DateTime)
    fulfilled = mapped_column(DateTime, nullable=True)
    user_id = mapped_column(ForeignKey("user.id"))
    cart = relationship('OrderProduct', back_populates="order")
    

class OrderProduct(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id = mapped_column(ForeignKey("product.id"))
    quantity: Mapped[int]
    order_id = mapped_column(ForeignKey("order.id"))
    order = relationship('Order', back_populates="cart")

# TODO: consider changing the two quantity attrs stock_quantity and order_quantity