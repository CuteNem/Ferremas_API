from flask import Flask, jsonify, request
from config import Config
from models import db, Category, Product

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Crear las tablas de la base de datos si no existen
with app.app_context():
    db.create_all()

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

if __name__ == '__main__':
    app.run(debug=True)
