import requests  
import logging
from dotenv import load_dotenv  
import os
from supabase import create_client, Client

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
URL = os.getenv("URL")
KEY = os.getenv("KEY")

supabase: Client = create_client(URL, KEY)

def agregar_mensaje(phone_number, message):
    try:
        response = supabase.table('mensajes').insert({
            'celular': phone_number,
            'mensaje': message
        }).execute()
        if response.status_code == 201:
            logging.info(f"Mensaje agregado a la base de datos para {phone_number}")
        else:
            logging.error(f"Error al agregar el mensaje a la base de datos: {response.data}")
    except Exception as e:
        logging.error(f"Error al agregar el mensaje a la base de datos: {str(e)}")

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
                            { "id": "1", "title": "Opción 1", "description": "" },
                            { "id": "2", "title": "Opción 2", "description": "" },
                            { "id": "3", "title": "Opción 3", "description": "" },
                            { "id": "4", "title": "Opción 4", "description": "" }
                        ]
                    }
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
        print("Mensaje opción enviado correctamente:", response.json())
        logging.info(f"Mensaje opción enviado con éxito a {phone_number}")
    else:
        print("Error al enviar el mensaje:", response.status_code, response.text)
        logging.error(f"Error al enviar el mensaje a {phone_number}: {response.text}")

def registrar_usuario(profile_name, phone_number):
    try:
        response = supabase.table('usuarios').insert({
            'name': profile_name,
            'phone_number': phone_number
        }).execute()
        if response.status_code == 201:
            logging.info(f"Usuario {profile_name} registrado con éxito")
        else:
            logging.error(f"Error al registrar el usuario: {response.data}")
    except Exception as e:
        logging.error(f"Error al registrar el usuario: {str(e)}")

def verificar_usuario_bd(phone_number):
    try:
        response = supabase.table('usuarios').select('*').eq('phone_number', phone_number).execute()
        return len(response.data) > 0
    except Exception as e:
        logging.error(f"Error al verificar el usuario en la base de datos: {str(e)}")
        return False

def verificar_status(phone_number):
    try:
        response = supabase.table('usuarios').select('user_status').eq('phone_number', phone_number).execute()
        if response.data:
            return response.data[0]['user_status']
        else:
            return None
    except Exception as e:
        logging.error(f"Error al verificar el estado del usuario: {str(e)}")
        return None

def actualizar_status(phone_number, nuevo_status):
    try:
        response = supabase.table('usuarios').update({'user_status': nuevo_status}).eq('phone_number', phone_number).execute()
        if response.status_code == 200:
            logging.info(f"Estado del usuario {phone_number} actualizado a {nuevo_status}")
        else:
            logging.error(f"Error al actualizar el estado del usuario: {response.data}")
    except Exception as e:
        logging.error(f"Error al actualizar el estado del usuario: {str(e)}")

def verificar_citas_manana():
    try:
        response = supabase.table('citas').select('*').eq('fecha', '2022-12-01').execute()
        return response.data
    except Exception as e:
        logging.error(f"Error al verificar las citas de mañana: {str(e)}")
        return []


def enviar_mensaje_template(nombre_template,phone_number, nombre, nombre_profesional, fecha, hora):
    try:
        message_data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual", 
            "to": phone_number,
            "type": "template",
            "template": {
                "name": nombre_template,  
                "language": {
                    "code": "es_CO"  
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "parameter_name": "nombre",
                                "text": nombre
                            },
                            {
                                "type": "text",
                                "parameter_name": "nombre_profesional",
                                "text": nombre_profesional
                            },
                            {
                                "type": "text",
                                "parameter_name": "fecha",
                                "text": fecha
                            },
                            {
                                "type": "text",
                                "parameter_name": "hora",
                                "text": hora
                            }
                        ]
                    }
                ]
            }
        }

        url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=message_data, headers=headers)
        
        if response.status_code == 200:
            logging.info(f"Mensaje template enviado con éxito a {phone_number}")
            return True
        else:
            logging.error(f"Error al enviar mensaje template: {response.text}")
            return False

    except Exception as e:
        logging.error(f"Error al enviar mensaje template: {str(e)}")
        return False

    









def obtener_datos_cliente(phone_number):
    try:
        response = supabase.table('client').select('id').eq('telefono', phone_number).execute()
        if response.data:
            return response.data[0]['id']
        else:
            logging.error(f"No se encontró el cliente con el teléfono {phone_number}")
            return None
    except Exception as e:
        logging.error(f"Error al obtener datos del cliente: {str(e)}")
        return None
    


def obtener_detalles_profesional(profesional_id):
    try:
        response = supabase.table('profesional').select('*').eq('id', profesional_id).execute()
        
        if response.data:
            return response.data[0] 
        else:
            return None
    except Exception as e:
        logging.error(f"Error al obtener detalles del profesional: {str(e)}")
        return None
    

def obtener_detalles_cliente(client_id):
    try:
        response = supabase.table('client').select('*').eq('id', client_id).execute()
        
        if response.data:
            return response.data[0]  
        else:
            return None
    except Exception as e:
        logging.error(f"Error al obtener detalles del cliente: {str(e)}")
        return None
    

