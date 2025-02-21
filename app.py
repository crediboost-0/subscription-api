from flask import Flask, request, jsonify
import os
import secrets
from models import db, User  
from flask_sqlalchemy import SQLAlchemy
from threading import Thread

app = Flask(__name__)

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def handle_customer_event(data):
    """Process Shopify webhook asynchronously."""
    webhook_topic = request.headers.get('X-Shopify-Topic', '').lower()
    email = data.get('email', '')

    if not email:
        return  

    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if webhook_topic == "customers/create":
            if not user:
                user = User(
                    email=email,
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    api_key=secrets.token_hex(16),  
                    is_active=True
                )
                db.session.add(user)
                db.session.commit()

        elif webhook_topic == "customers/update" and user:
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            db.session.commit()

@app.route('/shopify-webhook', methods=['POST'])
def shopify_webhook():
    """Handle Shopify webhooks."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    Thread(target=handle_customer_event, args=(data,)).start()
    return jsonify({"message": "Webhook received"}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10000)
