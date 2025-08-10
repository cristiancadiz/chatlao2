from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Cargar variables desde el entorno
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "clave123")  # Por defecto "clave123" si no está definida

if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
    raise Exception("Faltan variables de entorno: WHATSAPP_TOKEN o WHATSAPP_PHONE_NUMBER_ID")

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

    try:
        phone_number = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        message_body = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

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
