import requests  
import logging
from dotenv import load_dotenv  
import os
import mysql.connector

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


def agregar_mensaje(cursor, conn, phone_number, message):
    cursor.execute('INSERT INTO mensajes (celular, mensaje) VALUES (%s, %s)', (phone_number, message))
    conn.commit()

def enviar_mensaje(phone_number, message):
    message_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "text",
        "text": {
            "preview_url": True,
            "body": f"{message}"
        }
    }

    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=message_data, headers=headers)
    if response.status_code == 200:
        print("Mensaje enviado con éxito:", response.json())
        logging.info(f"Mensaje enviado con éxito a {phone_number}")
    else:
        print("Error al enviar el mensaje:", response.status_code, response.text)
        logging.error(f"Error al enviar el mensaje a {phone_number}: {response.text}")


def mensaje_opcion(phone_number):
    message_data = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": phone_number,
    "type": "interactive",
    "interactive": {
        "type": "list",
        "header": {
            "type": "text",
            "text": "Elige una opción"
        },
        "body": {
            "text": "Cuerpo del mensaje"
        },
        "footer": {
            "text": "footer"
        },
        "action": {
            "sections": [
                {
                    "title": "Disponibles",
                    "rows": [
                        {
                            "id": "1",
                            "title": "Opción 1",
                            "description": ""
                        },
                        {
                            "id": "2",
                            "title": "Opción 2",
                            "description": ""
                        },
                        {
                            "id": "3",
                            "title": "Opción 3",
                            "description": ""
                        },
                        {
                            "id": "4",
                            "title": "Opción 4",
                            "description": ""
                        }
                    ]
                }
                # Additional sections would go here
            ],
            "button": "Opciones"
        }
    }
}

    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=message_data, headers=headers)
    if response.status_code == 200:
        print("Mensaje opcion enviado correctamente:", response.json())
        logging.info(f"Mensaje opcion enviado con éxito a {phone_number}")
    else:
        print("Error al enviar el mensaje:", response.status_code, response.text)
        logging.error(f"Error al enviar el mensaje a {phone_number}: {response.text}")




def registrar_usuario(cursor, conn, profile_name, phone_number):
    cursor.execute('INSERT INTO usuarios (name, phone_number) VALUES (%s, %s)', (profile_name, phone_number))
    conn.commit()

def verificar_usuario_bd(cursor, phone_number):
    cursor.execute('SELECT * FROM usuarios WHERE phone_number = %s', (phone_number,))
    usuarios = cursor.fetchall()
    return len(usuarios) > 0

def verificar_status(cursor, phone_number):
    cursor.execute('SELECT user_status FROM usuarios WHERE phone_number = %s', (phone_number,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def actualizar_status(cursor, conn, phone_number, nuevo_status):
    cursor.execute('UPDATE usuarios SET user_status = %s WHERE phone_number = %s', (nuevo_status, phone_number))
    conn.commit()
