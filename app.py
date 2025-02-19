import os
from flask import Flask

app = Flask(__name__)

# Home route to check if the app is working
@app.route('/')
def home():
    return "API is running!"

# Additional API endpoint to test with
@app.route('/test')
def test():
    return "Test API endpoint working!"

# Main entry point for the Flask app
if __name__ == "__main__":
    # Ensuring it binds to the right port that Render expects
    port = int(os.environ.get("PORT", 10000))  # Use Render's default port
    app.run(host="0.0.0.0", port=port)
