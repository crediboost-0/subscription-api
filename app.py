from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock database (replace with real DB later)
subscriptions = {
    "user1_api_key": {"status": "active"},
    "user2_api_key": {"status": "inactive"}
}

@app.route('/check-subscription', methods=['POST'])
def check_subscription():
    data = request.json
    api_key = data.get("api_key")

    if api_key in subscriptions and subscriptions[api_key]["status"] == "active":
        return jsonify({"access": "granted"}), 200
    else:
        return jsonify({"access": "denied"}), 403

if __name__ == '__main__':
    app.run(debug=True)
