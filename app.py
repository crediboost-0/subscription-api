from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import os
import secrets
from models import db, User  # Import database and User model

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")  # Session handling

@app.route('/shopify-webhook', methods=['POST'])
def shopify_webhook():
    """Handle Shopify webhook for customer creation and updates."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid data"}), 400

    webhook_topic = request.headers.get('X-Shopify-Topic', '')
    customer_data = data.get('customer', {})
    email = customer_data.get('email', '')

    if not email:
        return jsonify({"error": "No customer email provided"}), 400

    user = User.query.filter_by(email=email).first()

    if webhook_topic == "customers/create":
        if not user:
            user = User(
                email=email,
                first_name=customer_data.get('first_name', ''),
                last_name=customer_data.get('last_name', ''),
                api_key=secrets.token_hex(16),
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            return jsonify({"message": "Customer created", "api_key": user.api_key}), 200
        else:
            return jsonify({"error": "Customer already exists"}), 400

    elif webhook_topic == "customers/update":
        if user:
            user.first_name = customer_data.get('first_name', user.first_name)
            user.last_name = customer_data.get('last_name', user.last_name)
            db.session.commit()
            return jsonify({"message": "Customer updated"}), 200
        else:
            return jsonify({"error": "Customer not found"}), 404

    return jsonify({"error": "Unknown event"}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            session['user_id'] = user.id  # Store user in session
            return redirect(url_for('dashboard'))
        else:
            return jsonify({"error": "User not found. Ensure you used the same email as your Shopify account."}), 400
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard to display API key."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    return render_template('dashboard.html', api_key=user.api_key, email=user.email)

@app.route('/logout')
def logout():
    """Logout the user and clear session."""
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
