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



if __name__ == "__main__":
    citas = citas_de_manana() 
    print("Citas para mañana:")
    for c in citas:
        cliente = obtener_detalles_cliente(c['client'])
        profesional = obtener_detalles_profesion(c['profesional'])
        nombre_profesional = profesional["nombre"]
        telefono_cliente = cliente["telefono"]
        nombre_cliente = cliente["nombre"]
        print(telefono_cliente)
        enviar_mensaje_template(str(telefono_cliente), str(nombre_cliente), str(nombre_profesional), str(c['date']), str(c['start_time']))