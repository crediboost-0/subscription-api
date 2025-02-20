import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, User

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create database tables if they don’t exist
@app.before_first_request
def create_tables():
    db.create_all()

# Home Page (Frontend UI)
@app.route('/')
def index():
    return render_template('index.html')

# API Route: Register User
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or not all(k in data for k in ('email', 'mt5_login', 'mt5_password', 'mt5_server', 'api_key')):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    new_user = User(
        email=data['email'],
        mt5_login=data['mt5_login'],
        mt5_password=data['mt5_password'],
        mt5_server=data['mt5_server'],
        api_key=data['api_key'],
        is_active=True
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# API Route: Get User Details
@app.route('/user/<email>', methods=['GET'])
def get_user(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'email': user.email,
        'mt5_login': user.mt5_login,
        'mt5_server': user.mt5_server,
        'api_key': user.api_key,
        'is_active': user.is_active
    })

# API Route: Activate/Deactivate User
@app.route('/user/<email>/status', methods=['PUT'])
def update_status(email):
    data = request.json
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.is_active = data.get('is_active', user.is_active)
    db.session.commit()

    return jsonify({'message': 'User status updated successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
