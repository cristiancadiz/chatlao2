from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Variables de entorno
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "clave123")

if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
    raise Exception("Faltan variables de entorno: WHATSAPP_TOKEN o WHATSAPP_PHONE_NUMBER_ID")

# Rutas de salud/raíz (para evitar 'Not Found')
@app.route("/", methods=["GET"])
def root():
    return "OK - WhatsApp webhook running", 200

@app.route("/health", methods=["GET"])
def health():
    return "healthy", 200

# Verificación del webhook (usada por Meta)
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Token de verificación inválido", 403

# Recepción de mensajes (usada por Meta)
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Mensaje recibido:", data)

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return "EVENT_RECEIVED", 200

        msg = messages[0]
        if msg.get("type") == "text":
            phone_number = msg["from"]
            message_body = msg["text"]["body"]
            send_message(phone_number, f"Recibi tu mensaje: {message_body}")
    except Exception as e:
        print("Error procesando el mensaje:", e)

    return "EVENT_RECEIVED", 200

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
    port = int(os.getenv("PORT", 10000))  # Render setea PORT
    app.run(host="0.0.0.0", port=port)
