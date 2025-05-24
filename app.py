from flask import Flask
from flask_jwt_extended import JWTManager
from routes.user_routes import user_routes
from routes.product_routes import product_routes
from routes.order_routes import order_routes
from models import *
from schema import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:mysqlrootuser@localhost/ecommerce_api'

app.config['JWT_SECRET_KEY'] = '09f368103c7a561d84a8fbda3da7d05ff81492d15730cf190a0c6acba6b8fbbb'
jwt = JWTManager(app)

db.init_app(app)
ma.init_app(app)

app.register_blueprint(user_routes)
app.register_blueprint(product_routes)
app.register_blueprint(order_routes)
    
if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()
        
    app.run(debug=True)