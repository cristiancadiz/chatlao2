from flask import Flask, request, jsonify
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "clave123")

@app.route('/', methods=['GET'])
def home():
    return "Webhook de WhatsApp activo"

# Ruta del webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == VERIFY_TOKEN:
            return challenge
        return "Token inválido", 403

    elif request.method == 'POST':
        data = request.get_json()
        print("Mensaje recibido:", data)
        return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
