from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_credentials', methods=['POST'])
def submit_credentials():
    data = request.get_json()
    mt5_login = data.get('mt5_login')
    mt5_password = data.get('mt5_password')
    server_name = data.get('server_name')
    api_key = data.get('api_key')

    # Here you would add logic to handle the received credentials
    # For example, validate them and store them in a database

    # For now, we'll just return a success message
    return jsonify({"message": "Credentials submitted successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
