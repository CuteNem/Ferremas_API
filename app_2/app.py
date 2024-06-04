from flask import Flask, jsonify, request
from config import Config
from models import db, Category, Product, PriceHistory
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Crear las tablas de la base de datos si no existen
with app.app_context():
    db.drop_all()  # Borrar todas las tablas existentes
    db.create_all()  # Crear todas las tablas de nuevo

@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{"id": category.id, "name": category.name} for category in categories])

@app.route('/categories/<int:category_id>/products', methods=['GET'])
def get_products_by_category(category_id):
    category = Category.query.get_or_404(category_id)
    return jsonify([{"id": product.id, "name": product.name} for product in category.products])

@app.route('/products', methods=['POST'])
def add_product():
    new_product_data = request.json
    new_product = Product(
        name=new_product_data['name'],
        category_id=new_product_data['category_id']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added successfully"}), 201

@app.route('/products/<int:product_id>/promotion', methods=['PUT'])
def add_product_to_promotion(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_promotion = True
    product.category_id = None
    product.added_to_promotion = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Product added to promotion"}), 200

@app.route('/products/<int:product_id>/promotion', methods=['DELETE'])
def remove_product_from_promotion(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_promotion = False
    # Reassign the category if necessary
    product.category_id = request.json.get('category_id', product.category_id)
    product.added_to_promotion = None
    db.session.commit()
    return jsonify({"message": "Product removed from promotion"}), 200

@app.route('/products/<int:product_id>/new_release', methods=['PUT'])
def add_product_to_new_release(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_new_release = True
    product.category_id = None
    product.added_to_new_release = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Product added to new release"}), 200

@app.route('/products/<int:product_id>/new_release', methods=['DELETE'])
def remove_product_from_new_release(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_new_release = False
    # Reassign the category if necessary
    product.category_id = request.json.get('category_id', product.category_id)
    product.added_to_new_release = None
    db.session.commit()
    return jsonify({"message": "Product removed from new release"}), 200

@app.route('/promotions', methods=['GET'])
def get_promotions():
    promotions = Product.query.filter_by(is_promotion=True).all()
    return jsonify([{"id": product.id, "name": product.name} for product in promotions])

@app.route('/new_releases', methods=['GET'])
def get_new_releases():
    new_releases = Product.query.filter_by(is_new_release=True).all()
    return jsonify([{"id": product.id, "name": product.name} for product in new_releases])

@app.route('/products/<int:product_id>/prices', methods=['GET'])
def get_price_history(product_id):
    product = Product.query.get_or_404(product_id)
    prices = PriceHistory.query.filter_by(product_id=product.id).order_by(PriceHistory.date_added.desc()).all()
    return jsonify([{"price": price.price, "date_added": price.date_added} for price in prices])

if __name__ == '__main__':
    app.run(debug=True)
