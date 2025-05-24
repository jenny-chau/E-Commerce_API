# E-Commerce API

## Project Overview
- Create an E-Commerce RESTful API with a database that stores user, product, and order data
- CRUD operations: Routes and endpoints to GET, POST, PUT, DELETE the users, products, and orders

## Programming Languages, Frameworks, Tools
- Python
- Flask (routing, request handling, and response formatting)
- Flask-SQLAlchemy (database)
- Flask-Marshmallow (serialization and validation)
- MySQL
- Jinja2 (used for rendering HTML templates)
- JWT (generating tokens for logging in and accessing protected routes)
- Postman (API testing)

## Database Models
- User table stores name, address, email, admin, and password details
    - Admin is a boolean (users who are admin have more access to routes and endpoints)
    - Passwords are encoded
    - One-to-many relationship with orders
- Product table stores product name and price information
    - One-to-many relationship with orders
- Order table stores:
    - user ID who purchased the order
    - order date (in format "YYYY-MM-DD")
    - order creation timestamp (automatically filled out)
    - Many-to-many relationship with users and products using a Order_Product association table

## RESTful endpoints
- User routes
    - POST /login: Authenticate user and return a JWT token
    - POST /users: Create a new user
    - GET /users: Retrieve all users (protected, admin only)
    - GET /users/paginate/<page_num>: Retrieve all users paginated (protected, admin only) (only displays name, email, address)
    - GET /users/<id>: Retrieve a user by ID (protected, admin only)
    - PUT /users/<id>: Update a user by ID (protected)
    - DELETE /users/<id>: Delete a user by ID (protected)
- Product routes
    - GET /products: Retrieve all products
    - GET /products/paginate/<page_num>: Retrieve paginated product data - 5 products per page
    - GET /products/<id>: Retrieve a product by ID
    - POST /products: Create a new product (protected, admin only)
    - PUT /products/<id>: Update a product by ID (protected, admin only)
    - DELETE /products/<id>: Delete a product by ID (protected, admin only)
- Order routes
    - POST /orders: Create a new order (requires user ID and order date in format "YYYY-MM-DD")
    - PUT /orders/<order_id>/add_product/<product_id>: Add a product to an order (prevent duplicates)
    - DELETE /orders/<order_id>/remove_product/<product_id>: Remove a product from an order
    - GET /orders/user/<user_id>: Get all orders for a user
    - GET /orders/<order_id>/products: Get all products for an order

## Getting Started
1. Clone this Github repository
2. Create a virtual environment
3. `pip install -r requirements.txt`
4. Open Postman and upload "E-Commerce API.postman_collection.json" to view all routes
5. Run "app.py"
6. Start by creating a user and continue!