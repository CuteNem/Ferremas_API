from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'customer' or 'seller'
    customer = db.relationship('Customer', backref='user_account', uselist=False)
    seller = db.relationship('Seller', backref='user_account', uselist=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    is_promotion = db.Column(db.Boolean, default=False)
    is_new_release = db.Column(db.Boolean, default=False)
    added_to_promotion = db.Column(db.DateTime, nullable=True)
    added_to_new_release = db.Column(db.DateTime, nullable=True)
    prices = db.relationship('PriceHistory', backref='product', lazy=True)
    availability = db.relationship('ProductAvailability', backref='product', lazy=True)

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

#SUCURSAL
class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    availability = db.relationship('ProductAvailability', backref='branch', lazy=True)

#INVENTARIO
class ProductAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


#PRUEBAS PUNTO 6
class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('query.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Seller(db.Model):
    __tablename__ = 'seller'
    #id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey('user.id_user'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    user = db.relationship('User', backref='customer', uselist=False)
    #id_user = db.Column(db.Integer, db.ForeignKey('user.id_user'), primary_key=True)
    # Otros campos de vendedor que desees agregar

class Customer(db.Model):
    __tablename__ = 'customer'
    #id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey('user.id_user'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    user = db.relationship('User', backref='customer', uselist=False)
    #id_user = db.Column(db.Integer, db.ForeignKey('user.id_user'), primary_key=True)
    # Otros campos de cliente que desees agregar
