from models import *
from schema import order_schema, orders_schema, products_schema
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import exc

order_routes = Blueprint("order_routes", __name__)


# POST /orders: Create a new order (requires user ID and order date in format "YYYY-MM-DD")
@order_routes.route("/orders", methods=["POST"])
def create_order():
    try:
        order = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    user = db.session.get(User, order["user_id"])
    
    if not user:
        return jsonify({"message": "User not found"}), 400
    
    new_order = Order(order_date=order["order_date"], user_id=order["user_id"])
    db.session.add(new_order)
    db.session.commit()
    
    return order_schema.jsonify(new_order), 201
    
# PUT /orders/<order_id>/add_product/<product_id>: Add a product to an order (prevent duplicates)
@order_routes.route("/orders/<int:order_id>/add_product/<int:product_id>", methods=["PUT"])
def add_product_to_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)
    
    if not order or not product:
        return jsonify({"message": "Order and/or product not found."}), 400
    
    try:
        order.products.append(product)
        db.session.commit()
    except exc.IntegrityError:
        return jsonify({"message": f"Product #{product_id} already in order #{order_id}"}), 400
    
    return jsonify({"message": f"Product #{product_id} added to order #{order_id}"}), 200

# DELETE /orders/<order_id>/remove_product/<product_id>: Remove a product from an order
@order_routes.route("/orders/<int:order_id>/remove_product/<int:product_id>", methods=["DELETE"])
def remove_product(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)
    
    if not order or not product:
        return jsonify({"message": "Order/product not found"}), 400
    
    if product not in order.products:
        return jsonify({"message": f"Product #{product_id} not in order #{order_id}."}), 400
    
    order.products.remove(product)
    db.session.commit()
    
    return jsonify({"message": f"Product removed from order #{order_id}"}), 200

# GET /orders/user/<user_id>: Get all orders for a user
@order_routes.route("/orders/user/<int:user_id>",methods=["GET"])
def get_user_orders(user_id):
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 400
    
    return orders_schema.jsonify(user.orders), 200

# GET /orders/<order_id>/products: Get all products for an order
@order_routes.route("/orders/<int:order_id>/products",methods=["GET"])
def get_order_products(order_id):
    order = db.session.get(Order, order_id)
    
    if not order:
        return jsonify({"message": "Order not found"}), 400
    
    if order.products == []:
        return jsonify({"message": "Order is currently empty."}), 200
    
    return products_schema.jsonify(order.products), 200