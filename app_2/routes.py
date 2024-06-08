from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, bcrypt, User, Customer, Seller

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], email=data['email'], password=hashed_password, role=data['role'])
    db.session.add(user)
    db.session.commit()

    if data['role'] == 'customer':
        customer = Customer(id=user.id_user)
        db.session.add(customer)
    elif data['role'] == 'seller':
        seller = Seller(id=user.id_user)
        db.session.add(seller)

    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'})
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

# Ejemplo de una ruta protegida
@auth_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return jsonify({'message': f'Welcome {current_user.username}, this is your dashboard'})


users_bp = Blueprint('users', __name__)
#GET DEL USUARIO
@users_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_data = []
    for user in users:
        user_data = {
            'id': user.id_user,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        users_data.append(user_data)
    return jsonify(users_data)