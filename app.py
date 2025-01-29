import logging
import os
import hmac
import hashlib
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv  
from modules import enviar_mensaje, registrar_usuario, verificar_usuario_bd, mensaje_opcion, verificar_status, actualizar_status,agregar_mensaje
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
            # Extraer el número del JSON
            phone_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
            logging.info(f"Número de teléfono extraído: {phone_number}")
            print(f"Número de teléfono extraído: {phone_number}")
            
            user_number = data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
            try:
                mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                agregar_mensaje(cursor, conn, user_number, mensaje)
                logging.info(f"Mensaje agregado a la base de datos: {mensaje}")

                if mensaje.lower() == "inicio":
                    actualizar_status(cursor, conn, phone_number, "inicio")
            except KeyError as e:
                logging.warning(f"No fue posible extraer el mensaje de: {str(e)}")
            usuarioEnBase = verificar_usuario_bd(cursor, phone_number)
            if phone_number == '573115118989':
                enviar_mensaje(phone_number, "Hola, soy un la conciencia de Alejadro y estoy pensando: Hola mi gatito te amo mucho me gustaria casarme contigo y estar juntos para la vida, te extrraño mi cielo, eres lo mas hermosos del mundo y deseo pasar el resto de mi vida contigo")
                
            elif usuarioEnBase:
                pass
            else:
                enviar_mensaje(phone_number, "Bienvenido, estas siendo registrado en nuestra base de datos")

                # Extraer el usuario de wpp del JSON
                profile_name = data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
                logging.info(f"Usuario registrado: Num {phone_number}, Usuario wpp {profile_name}")
                registrar_usuario(cursor, conn, profile_name, phone_number)

            # Verificar el estado del usuario
            estado_actual = verificar_status(cursor, phone_number)
            logging.info(f"Estado actual del usuario {phone_number}: {estado_actual}")
            
            if estado_actual == "inicio":
                mensaje_opcion(phone_number)
                # Actualizar el estado del usuario después de mostrar las opciones
                actualizar_status(cursor, conn, phone_number, "opciones_mostradas")

            # Verificar si el mensaje es interactivo
            if data['entry'][0]['changes'][0]['value']['messages'][0]['type'] == 'interactive':
                selected_option_id = data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['list_reply']['id']
                logging.info(f"Opción seleccionada por el usuario {phone_number}: {selected_option_id}")
                
                if estado_actual == "opciones_mostradas":
                    if selected_option_id == "1":
                        enviar_mensaje(phone_number, "Has seleccionado la opción 1, para volver escirba inicio")
                        actualizar_status(cursor, conn, phone_number, "opcion1")
                    elif selected_option_id == "2":
                        enviar_mensaje(phone_number, "Has seleccionado la opción 2, para volver escirba inicio")
                        actualizar_status(cursor, conn, phone_number, "opcion2")
                    elif selected_option_id == "3":
                        enviar_mensaje(phone_number, "Has seleccionado la opción 3, para volver escirba inicio")
                        actualizar_status(cursor, conn, phone_number, "opcion3")
                    elif selected_option_id == "4":
                        enviar_mensaje(phone_number, "Has seleccionado la opción 4, para volver escirba inicio")
                        actualizar_status(cursor, conn, phone_number, "opcion4")
                    else:
                        enviar_mensaje(phone_number, "Opción no válida, por favor selecciona una opción válida")
            else:
                logging.info(f"Mensaje no interactivo recibido de {phone_number}: {mensaje}")

        else:
            logging.warning("El webhook recibido no contiene el campo 'messages'")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Error al manejar el webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
