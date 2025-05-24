# Schema used to serialize, deserialize, and validate python object types to and from JSON

from flask_marshmallow import Marshmallow
from models import *

ma = Marshmallow()

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True
        
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        
user_schema = UserSchema()
users_schema = UserSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)