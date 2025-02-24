import logging
import os
import hmac
import hashlib
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv  
from modules import enviar_mensaje, registrar_usuario, verificar_usuario_bd, mensaje_opcion, verificar_status, actualizar_status,agregar_mensaje, enviar_mensaje_template
from reminder import modificar_confirmacion
import mysql.connector

load_dotenv()

# Obtener las variables de entorno
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
SQL = os.getenv("SQL")
APP_SECRET = os.getenv("APP_SECRET")

conn = mysql.connector.connect(
    host="localhost",
    user="Ale",
    password=SQL,   
    database="wpp"
)

cursor = conn.cursor()

logging.basicConfig(
    filename="webhook_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)

def verify_signature(request):
    """Verifica la firma del encabezado X-Hub-Signature-256."""
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        logging.warning("Firma no encontrada en el encabezado")
        abort(403, "Firma no encontrada")

    try:
        mac = hmac.new(APP_SECRET.encode(), request.data, hashlib.sha256).hexdigest()
        expected_signature = f"sha256={mac}"
        if not hmac.compare_digest(signature, expected_signature):
            logging.warning("Firma no válida")
            abort(403, "Firma no válida")
    except Exception as e:
        logging.error(f"Error al verificar la firma")
        abort(403, "Error al verificar la firma")



@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logging.info(f"Webhook verificado con token: {token}")
            return challenge, 200
        else:
            logging.warning(f"Intento de verificación fallido con token: {token}")
            return "Error de verificación", 403
    logging.error("Solicitud inválida en la ruta de verificación")
    return "Ruta no válida", 404


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    verify_signature(request)
    data = request.json
    logging.info(f"Mensaje recibido {data}")
    

    try:
        # Verificar si el campo 'messages' existe en el JSON
        if 'messages' in data['entry'][0]['changes'][0]['value']:
            phone_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
            # Verificar si el mensaje es interactivo
            if data['entry'][0]['changes'][0]['value']['messages'][0]['type'] == 'button':
                payload = data["entry"][0]["changes"][0]["value"]["messages"][0]["button"]["payload"]
                if payload == "Confirmo":
                    modificar_confirmacion(phone_number[2:])
                    print("La cita ha sido confirmada")
                    enviar_mensaje(phone_number, "¡Cita confirmada! 🎉")

                else:
                    print("El payload no es 'Confirmo'")

        else:
            logging.warning("El webhook recibido no contiene el campo 'messages'")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Error al manejar el webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    enviar_mensaje_template(573046692933, "Alejandro", "Laura", "2022-12-12", "13:00 PM")
    app.run(debug=True, host="0.0.0.0", port=5000)
