from flask import Flask, request, jsonify
import os
import secrets
from models import db, User  # Import database and User model

app = Flask(__name__)

@app.route('/shopify-webhook', methods=['POST'])
def shopify_webhook():
    """Handle Shopify webhook for customer creation and updates."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid data"}), 400

    # Extract the webhook topic from the headers
    webhook_topic = request.headers.get('X-Shopify-Topic', '')

    # Extract customer details from the payload
    customer_data = data.get('customer', {})
    email = customer_data.get('email', '')

    if not email:
        return jsonify({"error": "No customer email provided"}), 400

    user = User.query.filter_by(email=email).first()

    if webhook_topic == "customers/create":  # Corrected topic name
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

if __name__ == '__main__':
    app.run(debug=True)