from models import *
from schema import product_schema, products_schema
from sqlalchemy import select
from flask import Blueprint, jsonify, request, render_template
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

product_routes = Blueprint("product_routes", __name__)


# GET /products: Retrieve all products
@product_routes.route("/products", methods=["GET"])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()
    return products_schema.jsonify(products), 200

# GET /products/paginate/<page_num>: Retrieve paginated product data - 5 products per page
@product_routes.route("/products/paginate/<int:page_num>", methods=["GET"])
def get_products_paginate(page_num):
    products = db.paginate(db.select(Product), per_page=5, page=page_num, error_out=True)
    
    return render_template('products.html', elements=products), 200

# GET /products/<id>: Retrieve a product by ID
@product_routes.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    product = db.session.get(Product, id)
    
    if not product:
        return jsonify({"message": "product id not found"}), 400
    
    return product_schema.jsonify(product), 200

# POST /products: Create a new product (protected, admin only)
@product_routes.route("/products", methods=["POST"])
@jwt_required()
def create_product():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)
    
    if not current_user or not current_user.admin:
        return jsonify({"message": "Access denied."}), 400
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Check values are not empty
    for key in product_data:
        if not product_data[f"{key}"]:
            return jsonify({"message": "Empty value detected"}), 400
    
    product = Product(product_name=product_data["product_name"], price=product_data["price"])
    db.session.add(product)
    db.session.commit()
    return product_schema.jsonify(product), 201

# PUT /products/<id>: Update a product by ID (protected, admin only)
@product_routes.route("/products/<int:id>", methods=["PUT"])
@jwt_required()
def update_product(id):
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)
    
    if not current_user or not current_user.admin:
        return jsonify({"message": "Access denied."}), 400
    
    product = db.session.get(Product, id)
    
    if not product:
        return jsonify({"message": "Product not found"}), 400
    
    try:
        product_updates = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    if product_updates["product_name"]:
        product.product_name = product_updates["product_name"]
    product.price = product_updates["price"]
    
    db.session.commit()
    
    return product_schema.jsonify(product), 200
    

# DELETE /products/<id>: Delete a product by ID (protected, admin only)
@product_routes.route("/products/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_product(id):
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)
    
    if not current_user or not current_user.admin:
        return jsonify({"message": "Access denied."}), 400
    
    product = db.session.get(Product, id)
    
    if not product:
        return jsonify({"message": "product not found"}), 400
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({"message": "Product Deleted!"}), 200