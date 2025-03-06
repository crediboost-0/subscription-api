from flask import Flask, request, jsonify
import os
import secrets
from models import db, User  # Import database and User model

app = Flask(__name__)

# Ensure the correct database connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)  # Correctly initialize SQLAlchemy

# Ensure tables are created at startup
with app.app_context():
    db.create_all()

@app.route('/shopify-webhook', methods=['POST'])
def shopify_webhook():
    """Handle Shopify webhook for customer creation and updates."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid data"}), 400

    # Extract webhook topic from headers
    webhook_topic = request.headers.get('X-Shopify-Topic', '')

    # Extract customer details from the payload
    customer_data = data.get('customer', {})
    email = customer_data.get('email', '')

    if not email:
        return jsonify({"error": "No customer email provided"}), 400

    user = User.query.filter_by(email=email).first()

    if webhook_topic == "customers/create":
        # Handle new customer creation
        if not user:
            user = User(
                email=email,
                first_name=customer_data.get('first_name', ''),
                last_name=customer_data.get('last_name', ''),
                api_key=secrets.token_hex(16),  # Generate a new API key
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            return jsonify({"message": "Customer created", "api_key": user.api_key}), 200
        else:
            return jsonify({"error": "Customer already exists"}), 400

    elif webhook_topic == "customers/update":
        # Handle customer updates
        if user:
            user.first_name = customer_data.get('first_name', user.first_name)
            user.last_name = customer_data.get('last_name', user.last_name)
            db.session.commit()
            return jsonify({"message": "Customer updated"}), 200
        else:
            return jsonify({"error": "Customer not found"}), 404

    return jsonify({"error": "Unknown event"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'api_key' not in data:
        return jsonify({"error": "Email and API key required"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or user.api_key != data['api_key']:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful", "user": {"email": user.email, "api_key": user.api_key}}), 200

# Add a test route to verify if Flask is running
@app.route('/test')
def test():
    return "Flask is running!"

# Route to retrieve API key by email
@app.route('/api/get_api_key', methods=['GET'])
def get_api_key():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"email": email, "api_key": user.api_key})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
