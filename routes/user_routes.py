from flask import jsonify, request, Blueprint, render_template
from sqlalchemy import select, exc
from marshmallow import ValidationError
from models import *
from schema import user_schema, users_schema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import bcrypt

user_routes = Blueprint('user_routes', __name__)

# POST /login: Authenticate user and return a JWT token
@user_routes.route("/login", methods=["POST"])
def login():
    data = request.json # email and password
    
    # Check if user in database; email is unique
    query = select(User).where(User.email == data.get("email"))
    user = db.session.execute(query).scalar()
    
    if not user or not bcrypt.checkpw(data.get("password").encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({"message": "Invalid email or password"}), 401
    
    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))
    
    return jsonify({"access_token": access_token}), 200
    

# POST /users: Create a new user
@user_routes.route("/users", methods=["POST"])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    encoded_pw = user_data["password"].encode('utf-8')
    
    hashed_password = bcrypt.hashpw(encoded_pw, bcrypt.gensalt())
    
    # Check if values are empty
    for key in user_data:
        if not user_data[f"{key}"]:
            return jsonify({"message": "Empty value detected."}), 400
    
    try:
        new_user = User(
            name=user_data["name"], 
            address=user_data["address"], 
            email=user_data["email"],
            password=hashed_password.decode('utf-8'),
            admin=user_data["admin"]
        )
        
        db.session.add(new_user)
        db.session.commit()
    except exc.IntegrityError as e:
        return jsonify({"message": "Duplicate email"}), 400
    
    return user_schema.jsonify(new_user), 201

# GET /users: Retrieve all users (protected, admin only)
@user_routes.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)
    
    if not current_user:
        return jsonify({"message": "User not found"}), 400
    
    if not current_user.admin:
        return jsonify({"message": "Access denied. Admin only."}), 401
    
    query = select(User)
    users = db.session.execute(query).scalars().all()
    
    return users_schema.jsonify(users), 200

# GET /users/paginate/<page_num>: Retrieve all users paginated (protected, admin only) (only displays name, email, address)
@user_routes.route("/users/paginate/<int:page_num>", methods=["GET"])
@jwt_required()
def get_users_paginate(page_num):
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)
    
    if not current_user:
        return jsonify({"message": "User not found"}), 400
    
    if not current_user.admin:
        return jsonify({"message": "Access denied. Admin only."}), 401
    
    users = db.paginate(db.select(User), per_page=5, page=page_num, error_out=True)
    
    return render_template('users.html', users=users)

# GET /users/<id>: Retrieve a user by ID (protected, admin only)
@user_routes.route("/users/<int:id>", methods=["GET"])
@jwt_required()
def get_user(id):
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)
    if not current_user:
        return jsonify({"message": "User not found"}), 400
    
    if not current_user.admin and current_user_id != id:
        return jsonify({"message": "Access denied. Admin only."}), 401
    
    user = db.session.get(User, id)
    
    if not user:
        return jsonify({"message": "User id not found"}), 400
    
    return user_schema.jsonify(user), 200

# PUT /users/<id>: Update a user by ID (protected)
@user_routes.route("/users/<int:id>", methods=["PUT"])
@jwt_required()
def update_user(id):
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if not current_user:
        return jsonify({"message": "User not found"}), 400
    
    # Current user can only modify their own account or if user is admin, they can modify other users.
    if not current_user.admin and current_user_id != id:
        return jsonify({"message": "Access Denied. Please login."}), 401
    
    user = db.session.get(User, id)
    
    if not user:
        return jsonify({"message": "User not found"}), 400
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Only update if fields are not empty
    try:
        if user_data["name"]:
            user.name = user_data["name"]
        if user_data["address"]:
            user.address = user_data["address"]
        if user_data["email"]:
            user.email = user_data["email"]
        if bool(user_data["admin"]) or not bool(user_data["admin"]):
            user.admin = bool(user_data["admin"])
        if user_data["password"]:
            encoded_pw = user_data["password"].encode('utf-8')
            user.password = bcrypt.hashpw(encoded_pw, bcrypt.gensalt())
        db.session.commit()
    except exc.IntegrityError as e:
            return jsonify({"message": "Duplicate email"}), 400
        
    return user_schema.jsonify(user), 200


# DELETE /users/<id>: Delete a user by ID (protected)
@user_routes.route("/users/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_user(id):
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)
    
    if not current_user:
        return jsonify({"message": "User not found"}), 400
    
    # Current user can only delete their own account or if user is admin, deleting other users is acceptable.
    if not current_user.admin and current_user_id != id:
        return jsonify({"message": "Access denied. Please login."}), 401
    
    user = db.session.get(User, id)
    
    if not user:
        return jsonify({"message": "User not found"}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": f"user {id} successfully deleted"}), 200

