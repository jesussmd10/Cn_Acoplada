# app/db/dynamodb_db.py
import os
import boto3
from typing import List, Optional
from app.model.pokemon import Pokemon, PokemonUpdate
from app.db.db import DBInterface
from botocore.exceptions import ClientError

class DynamoDB(DBInterface):
    """
    Implementación de la interfaz de BD para Amazon DynamoDB.
    Esta clase ASUME que la tabla ya existe y es definida 
    por una variable de entorno.
    """

    def __init__(self):
        # --- NUEVO CÓDIGO DE DEPURACIÓN ---
        print("--- [DEBUG] DynamoDB __init__ ---")
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('DYNAMODB_TABLE')
        
        if not self.table_name:
            print("-> ERROR: DYNAMODB_TABLE no está definida en el entorno.")
            raise ValueError("La variable de entorno DYNAMODB_TABLE no está definida.")
            
        print(f"-> Conectando a la tabla: {self.table_name}")
        self.table = self.dynamodb.Table(self.table_name)
        print("-> Conexión a la tabla exitosa.")

    def create_pokemon(self, pokemon: Pokemon) -> Pokemon:
        item = pokemon.model_dump()
        self.table.put_item(Item=item)
        return pokemon

    def get_pokemon(self, pokedex_id: int) -> Optional[Pokemon]:
        try:
            response = self.table.get_item(Key={'pokedex_id': pokedex_id})
            if 'Item' in response:
                return Pokemon(**response['Item'])
            return None
        except ClientError as e:
            print(f"Error al obtener item: {e}")
            return None

    def get_all_pokemon(self) -> List[Pokemon]:
        response = self.table.scan() # Advertencia: Ineficiente para tablas grandes
        items = response.get('Items', [])
        # Quitamos el 'sort' que tenías, ya que 'position' no existe en Pokémon
        return [Pokemon(**item) for item in items]

    def update_pokemon(self, pokedex_id: int, pokemon_data: PokemonUpdate) -> Optional[Pokemon]:
        """
        Esta versión usa update_item para una actualización parcial y eficiente.
        """
        # Excluye campos nulos para no sobrescribir con 'None'
        update_values = pokemon_data.model_dump(exclude_unset=True)
        
        if not update_values:
            # No hay nada que actualizar
            return self.get_pokemon(pokedex_id) 

        # Construye la expresión de actualización de DynamoDB
        update_expression = "SET " + ", ".join(f"#{k}=:{k}" for k in update_values)
        expression_attribute_names = {f"#{k}": k for k in update_values}
        expression_attribute_values = {f":{k}": v for k, v in update_values.items()}

        try:
            response = self.table.update_item(
                Key={'pokedex_id': pokedex_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW", # Devuelve el item actualizado
                ConditionExpression="attribute_exists(pokedex_id)" # Asegura que el item exista
            )
            return Pokemon(**response['Attributes'])
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(f"Pokémon no encontrado: {pokedex_id}")
            else:
                print(f"Error al actualizar item: {e}")
            return None

    def delete_pokemon(self, pokedex_id: int) -> bool:
        try:
            # Usamos la misma lógica que tenías, pero con la key correcta
            self.table.delete_item(
                Key={'pokedex_id': pokedex_id},
                ConditionExpression="attribute_exists(pokedex_id)"
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(f"Pokémon no encontrado: {pokedex_id}")
            else:
                print(f"Error al eliminar item: {e}")
            return False