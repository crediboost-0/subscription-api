from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Route for the web portal UI
@app.route('/')
def index():
    return render_template('index.html')

# API route to handle subscription cancellation
@app.route('/cancel_subscription', methods=['POST'])
def cancel_subscription():
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Placeholder logic for canceling subscription (replace with actual implementation)
    success = True  # Change based on real cancellation logic

    if success:
        return jsonify({"message": "Subscription canceled successfully"})
    else:
        return jsonify({"error": "Failed to cancel subscription"}), 500

# API route to handle user login details submission
@app.route('/submit_credentials', methods=['POST'])
def submit_credentials():
    data = request.json
    mt5_login = data.get('mt5_login')
    mt5_password = data.get('mt5_password')
    server_name = data.get('server_name')
    api_key = data.get('api_key')

    if not all([mt5_login, mt5_password, server_name, api_key]):
        return jsonify({"error": "All fields are required"}), 400

    # Placeholder logic to store credentials (Replace with actual implementation)
    print(f"Received login: {mt5_login}, Server: {server_name}, API Key: {api_key}")
    
    return jsonify({"message": "Credentials submitted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
