from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Variables fijas para la prueba
WHATSAPP_TOKEN = "EAAXvFXJwAB8BPKPGqmegFpDzZCJX4sVx7E9QoMgZAKCCmbBOgQFz8X9bjQ2HuvLMqX1HQQ6mDDiZAlStUhn26cjo1dqlpeXfo1fAFpdtbUr7g9ovZBM9PJgtvOAlVxMzR7s8N6ZCWh8clvoNReDt5te2P9Od2oFwOuveUMVcRTQ0BhUPjQ5Ynd8xaaUREK6KQWLgcQWxuDZCB0kzq9k74LUERQZC7qyiGvRZAw7kCVmkIuSsPWnpV0qRX0vhln3s"
WHATSAPP_PHONE_NUMBER_ID = "1670250276847647"
VERIFY_TOKEN = "clave123"  # Para la verificación inicial

# Ruta para verificar el webhook
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Token de verificación inválido", 403

# Ruta para recibir mensajes
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Mensaje recibido:", data)

    # Extraer el número y mensaje
    try:
        phone_number = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        message_body = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

        # Enviar respuesta
        send_message(phone_number, f"Recibí tu mensaje: {message_body}")
    except Exception as e:
        print("Error procesando el mensaje:", e)

    return "EVENT_RECEIVED", 200

# Función para enviar un mensaje de WhatsApp
def send_message(to, text):
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    r = requests.post(url, headers=headers, json=payload)
    print("Respuesta de WhatsApp:", r.status_code, r.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
