# app/db/factory.py
import os
from app.db.db import DBInterface
from app.db.dynamodb_db import DynamoDB
# from app.db.postgres_db import PostgresDB 
from typing import Optional

_db_instance: Optional[DBInterface] = None

def get_db() -> DBInterface:
    global _db_instance
    
    if _db_instance:
        return _db_instance

    # --- NUEVO CÓDIGO DE DEPURACIÓN ---
    # Vamos a imprimir las variables que estamos recibiendo
    db_type = os.environ.get('DB_TYPE')
    table_name = os.environ.get('DYNAMODB_TABLE')
    
    print("--- [DEBUG] Factory get_db() ---")
    print(f"Variable DB_TYPE leída: {db_type}")
    print(f"Variable DYNAMODB_TABLE leída: {table_name}")
    
    # Si DB_TYPE está vacía o es 'dynamodb', forzamos 'DYNAMODB'
    # Esto soluciona el problema si el parámetro es 'postgres' por error.
    if not db_type or db_type.lower() == 'dynamodb':
        print("-> Decisión: Usar DynamoDB.")
        try:
            _db_instance = DynamoDB()
            print("-> Instancia de DynamoDB CREADA.")
        except Exception as e:
            print(f"-> ERROR: Fallo al crear la instancia de DynamoDB: {e}")
            raise e
    else:
        # Si DB_TYPE es 'postgres' o cualquier otra cosa
        print(f"-> Decisión: DB_TYPE '{db_type}' no es DYNAMODB.")
        raise ValueError(f"DB_TYPE '{db_type}' no soportado.")
    # --- FIN CÓDIGO DE DEPURACIÓN ---
    
    return _db_instance