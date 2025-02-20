from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import uuid
import hashlib
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Replace with actual secret key
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Initialize security extensions
csrf = CSRFProtect(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Temporary credential storage (Replace with database in production)
credentials_store = {}

# Security configurations
API_KEY_LENGTH = 32
PEPPER = 'your-pepper-string'  # Add random pepper value

def secure_hash(password: str) -> str:
    """Securely hash passwords with pepper and SHA-256"""
    peppered = password + PEPPER
    return hashlib.sha256(peppered.encode()).hexdigest()

@app.route('/')
@limiter.exempt
def index():
    return render_template('index.html')

@app.route('/submit_credentials', methods=['POST'])
@limiter.limit("5/minute")  # Rate limiting
@csrf.exempt  # Only if using API without frontend CSRF
def submit_credentials():
    try:
        # Validate content type
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415

        data = request.get_json()
        
        # Validate all fields
        required_fields = ['mt5_login', 'mt5_password', 'server_name', 'api_key']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate field formats
        if not data['mt5_login'].isdigit():
            return jsonify({"error": "MT5 login must be numeric"}), 400

        if data['server_name'] not in {'Broker1', 'Broker2', 'Broker3'}:
            return jsonify({"error": "Invalid server selection"}), 400

        if len(data['api_key']) != API_KEY_LENGTH:
            return jsonify({"error": "Invalid API key format"}), 400

        # Secure credential storage
        credential_id = str(uuid.uuid4())
        hashed_pw = secure_hash(data['mt5_password'])
        
        credentials_store[credential_id] = {
            'login': data['mt5_login'],
            'server': data['server_name'],
            'api_key': data['api_key'],
            'password_hash': hashed_pw,
            'timestamp': datetime.now().isoformat(),
            'expires': (datetime.now() + timedelta(minutes=15)).isoformat()  # Temp storage
        }

        return jsonify({
            "message": "Credentials received securely",
            "credential_id": credential_id,
            "expires_at": credentials_store[credential_id]['expires']
        }), 200

    except Exception as e:
        app.logger.error(f"Credential submission error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # Remove in production