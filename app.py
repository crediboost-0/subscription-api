from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from functools import wraps

app = Flask(__name__)

# Configurations
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

db.init_app(app)

# Ensure tables are created
with app.app_context():
    db.create_all()

# Login-required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# API key-required decorator
def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "API key required"}), 401

        user = User.query.filter_by(api_key=api_key).first()
        if not user or not user.is_active:
            return jsonify({"error": "Invalid or inactive API key"}), 403

        request.user = user  # Attach user to request context
        return f(*args, **kwargs)
    return decorated_function

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
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        bot_configuration = request.form['bot_configuration']
        api_key = secrets.token_hex(16)

        user.api_key = api_key
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('home.html')

@app.route('/shopify-webhook', methods=['POST'])
def shopify_webhook():
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

@app.route('/api/get_api_key', methods=['GET'])
def get_api_key():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"email": email, "api_key": user.api_key})

@app.route('/api/validate_key', methods=['GET'])
def validate_key():
    api_key = request.args.get('api_key')
    if not api_key:
        return jsonify({"valid": False, "error": "API key is required"}), 400

    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({"valid": False, "error": "Invalid API key"}), 404

    if not user.is_active:
        return jsonify({"valid": False, "error": "Subscription inactive"}), 403

    return jsonify({
        "valid": True,
        "email": user.email,
        "bot_allowed": True
    }), 200

# ? Example protected endpoint
@app.route('/api/protected-bot-action', methods=['POST'])
@api_key_required
def protected_bot_action():
    user = request.user
    return jsonify({
        "message": f"Hello {user.email}, your API key is valid. Bot action allowed."
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
