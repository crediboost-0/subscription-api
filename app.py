from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User  # Import database and User model

app = Flask(__name__)

# Ensure the correct database connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")  # Add a secret key for sessions

db.init_app(app)  # Correctly initialize SQLAlchemy

# Ensure tables are created at startup
with app.app_context():
    db.create_all()

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        # Removed MetaTrader 5 related logic
        # Instead of storing MT5 credentials, you can handle other configurations here
        # For example, saving bot configurations or user preferences
        bot_configuration = request.form['bot_configuration']
        api_key = secrets.token_hex(16)  # Generate a new API key

        current_user.api_key = api_key
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('home.html')

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
