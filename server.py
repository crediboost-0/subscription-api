from flask import Flask, request, jsonify

app = Flask(__name__)

# Webhook route
@app.route('/webhook', methods=['POST'])
def receive_webhook():
    data = request.json  # Shopify webhook data
    print("Webhook received:", data)  # Log the data (optional)

    # Respond to Shopify
    return jsonify({"message": "Webhook received successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
