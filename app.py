import logging
import os
import hmac
import hashlib
import mysql.connector
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from modules import (
    enviar_mensaje,
    registrar_usuario,
    verificar_usuario_bd,
    mensaje_opcion,
    verificar_status,
    actualizar_status,
    agregar_mensaje,
    enviar_mensaje_template,
)
from reminder import modificar_confirmacion

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
SQL = os.getenv("SQL")
APP_SECRET = os.getenv("APP_SECRET")



logging.basicConfig(
    filename="webhook_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

def verify_signature(req: Request, body: bytes):
    signature = req.headers.get("X-Hub-Signature-256")
    if not signature:
        logging.warning("Firma no encontrada en el encabezado")
        raise HTTPException(status_code=403, detail="Firma no encontrada")

    try:
        mac = hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
        expected_signature = f"sha256={mac}"
        if not hmac.compare_digest(signature, expected_signature):
            logging.warning("Firma no válida")
            raise HTTPException(status_code=403, detail="Firma no válida")
    except Exception:
        logging.error("Error al verificar la firma")
        raise HTTPException(status_code=403, detail="Error al verificar la firma")

@app.get("/webhook")
def verify_webhook(mode: str = None, token: str = None, challenge: str = None):
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logging.info(f"Webhook verificado con token: {token}")
            return challenge
        else:
            logging.warning(f"Intento de verificación fallido con token: {token}")
            raise HTTPException(status_code=403, detail="Error de verificación")
    logging.error("Solicitud inválida en la ruta de verificación")
    raise HTTPException(status_code=404, detail="Ruta no válida")

@app.post("/webhook")
async def handle_webhook(request: Request):
    body = await request.body()
    verify_signature(request, body)

    try:
        data = await request.json()
        logging.info(f"Mensaje recibido {data}")

        if "messages" in data["entry"][0]["changes"][0]["value"]:
            phone_number = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
            if data["entry"][0]["changes"][0]["value"]["messages"][0]["type"] == "button":
                payload = data["entry"][0]["changes"][0]["value"]["messages"][0]["button"]["payload"]
                if payload == "Confirmo":
                    modificar_confirmacion(phone_number[2:])
                    print("La cita ha sido confirmada")
                    enviar_mensaje(phone_number, "¡Cita confirmada! 🎉")
                else:
                    print("El payload no es 'Confirmo'")
        else:
            logging.warning("El webhook recibido no contiene el campo 'messages'")

        return {"status": "success"}
    except Exception as e:
        logging.error(f"Error al manejar el webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.on_event("startup")
async def startup_event():
    enviar_mensaje_template(573046692933, "Alejandro", "Laura", "2022-12-12", "13:00 PM")