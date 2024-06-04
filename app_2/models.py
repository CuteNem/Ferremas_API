from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

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
