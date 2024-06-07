from flask import Flask, jsonify, request, redirect, url_for
from config import Config
from models import db, Category, Product, PriceHistory, Branch, ProductAvailability
from paypalrestsdk import Payment
import paypalrestsdk
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

paypalrestsdk.configure({
    "mode": app.config['PAYPAL_MODE'],
    "client_id": app.config['PAYPAL_CLIENT_ID'],
    "client_secret": app.config['PAYPAL_CLIENT_SECRET']
})

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

@app.route('/products/<int:product_id>/prices', methods=['POST'])
def add_price_history(product_id):
    product = Product.query.get_or_404(product_id)
    new_price_data = request.json
    new_price = PriceHistory(
        product_id=product.id,
        price=new_price_data['price']
    )
    db.session.add(new_price)
    db.session.commit()
    return jsonify({"message": "Price history added successfully"}), 201

@app.route('/branches', methods=['POST'])
def add_branch():
    new_branch_data = request.json
    new_branch = Branch(
        name=new_branch_data['name'],
        location=new_branch_data['location']
    )
    db.session.add(new_branch)
    db.session.commit()
    return jsonify({"message": "Branch added successfully"}), 201

@app.route('/branches/<int:branch_id>/products/<int:product_id>', methods=['PUT'])
def update_product_availability(branch_id, product_id):
    data = request.json
    availability = ProductAvailability.query.filter_by(branch_id=branch_id, product_id=product_id).first()
    if availability:
        availability.quantity = data['quantity']
    else:
        availability = ProductAvailability(
            branch_id=branch_id,
            product_id=product_id,
            quantity=data['quantity']
        )
        db.session.add(availability)
    db.session.commit()
    return jsonify({"message": "Product availability updated successfully"}), 200

@app.route('/branches/<int:branch_id>/products', methods=['GET'])
def get_branch_products(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    availability = ProductAvailability.query.filter_by(branch_id=branch.id).all()
    return jsonify([{
        "product_id": item.product_id,
        "product_name": item.product.name,
        "quantity": item.quantity
    } for item in availability])

@app.route('/products/<int:product_id>/branches', methods=['GET'])
def get_product_availability(product_id):
    product = Product.query.get_or_404(product_id)
    availability = ProductAvailability.query.filter_by(product_id=product.id).all()
    return jsonify([{
        "branch_id": item.branch_id,
        "branch_name": item.branch.name,
        "quantity": item.quantity
    } for item in availability])

@app.route('/pay', methods=['POST'])
def pay():
    payment_info = request.json
    product = Product.query.get_or_404(payment_info['product_id'])

    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for('payment_executed', _external=True),
            "cancel_url": url_for('payment_cancelled', _external=True)
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": product.name,
                    "sku": str(product.id),
                    "price": str(payment_info['price']),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(payment_info['price']),
                "currency": "USD"
            },
            "description": f"Compra del producto {product.name}"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                return jsonify({"approval_url": approval_url})
    else:
        return jsonify({"error": payment.error}), 400

@app.route('/payment_executed', methods=['GET'])
def payment_executed():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    payment = Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        return jsonify({"message": "Payment executed successfully"})
    else:
        return jsonify({"error": payment.error}), 400

@app.route('/payment_cancelled', methods=['GET'])
def payment_cancelled():
    return jsonify({"message": "Payment cancelled"}), 200

if __name__ == '__main__':
    app.run(debug=True)