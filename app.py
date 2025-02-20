from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config  # Import configuration settings

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)  # Load configuration

# Initialize database
db = SQLAlchemy(app)

# Homepage route
@app.route('/')
def home():
    return render_template('index.html')

# API route to test database connection
@app.route('/test_db')
def test_db():
    try:
        db.session.execute('SELECT 1')  # Simple test query
        return jsonify({"message": "Database connected successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
