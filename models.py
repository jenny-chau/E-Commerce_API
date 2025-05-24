from sqlalchemy import String, ForeignKey, Table, Column, DateTime, Date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from typing import List
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey("order.id"), primary_key=True),
    Column("product_id", ForeignKey("product.id"), primary_key=True)
)

class User(Base):
    __tablename__= "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(250))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    password: Mapped[str] = mapped_column(String(72))
    admin: Mapped[bool] #True = user is admin, used to access specific user_routes
    
    # One-to-Many relationship with orders
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    
class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[datetime.date] = mapped_column(Date)
    create_timestamp_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    
    # Many-to-One relationship with user
    user: Mapped["User"] = relationship(back_populates="orders")
    
    # one-to-many relationship with product
    products: Mapped[List["Product"]] = relationship(secondary=order_product, back_populates="orders")
    
class Product(Base):
    __tablename__ = "product"
    id:  Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(500))
    price: Mapped[float]
    
    # one-to-many relationship with order
    orders: Mapped[List["Order"]] = relationship(secondary=order_product, back_populates="products")