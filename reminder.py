import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from modules import enviar_mensaje_template
load_dotenv()

SUPABASE_URL = os.getenv("URL")
SUPABASE_KEY = os.getenv("KEY")

supabase: Client = create_client(SUPABASE_URL,SUPABASE_KEY)

def citas_de_manana():
    manana = datetime.now() + timedelta(days=1)
    fecha_m = manana.strftime('%Y-%m-%d')
    
    try:
        response = supabase.table('appointment').select('*').eq('date', fecha_m).execute()
        
        if response.data:
            return response.data
        else:
            return []
    except Exception as e:
        logging.error(f"Error al verificar las citas de mañana: {str(e)}")
        return []

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
    

def obtener_detalles_profesion(profesional_id):
    try:
        response = supabase.table('profesional').select('*').eq('id', profesional_id).execute()
        
        if response.data:
            return response.data[0] 
        else:
            return None
    except Exception as e:
        logging.error(f"Error al obtener detalles del profesional: {str(e)}")
        return None
    

def modificar_confirmacion(phone_number):
    try:
        response = supabase.table('client').select('id').eq('telefono', phone_number).execute()
        if response.data:
            client_id = response.data[0]['id']
            
            citas_response = supabase.table('appointment').select('*').eq('client', client_id).execute()
            
            if citas_response.data:
                update_response = supabase.table('appointment').update({'confirmed': True}).eq('client', client_id).execute()
                if update_response.data:
                    logging.info(f"Confirmación de la cita de {phone_number} actualizada")
                else:
                    logging.error(f"Error al actualizar la confirmación de la cita: {update_response}")
            else:
                logging.error(f"No se encontraron citas para el cliente con ID {client_id}")
        else:
            logging.error(f"No se encontró el cliente con el teléfono {phone_number}")
    except Exception as e:
        logging.error(f"Error al actualizar la confirmación de la cita: {str(e)}")

