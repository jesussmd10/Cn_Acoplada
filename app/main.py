# app/main.py (Versión para Docker/ECS usando Flask con CORS manual)

from flask import Flask, jsonify, request, Response
from pydantic import ValidationError
from functools import wraps

from app.db.factory import get_db
from app.model.pokemon import Pokemon, PokemonUpdate

# 1. Inicializa la aplicación Flask
app = Flask(__name__)

# 2. Inicializa la conexión a la base de datos
try:
    print("--- [DEBUG] main.py: Intentando llamar a get_db() ---")
    db = get_db()
    print("--- [DEBUG] main.py: get_db() finalizado. 'db' está inicializado.")
except Exception as e:
    print(f"--- [ERROR FATAL] main.py: Fallo al inicializar get_db(): {e} ---")
    db = None

# 🔹 Función helper para añadir headers CORS a cada respuesta
def cors_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = f(*args, **kwargs)
        if isinstance(resp, tuple):
            data, status = resp
        else:
            data, status = resp, 200
        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,x-api-key,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        }
        return jsonify(data), status, headers
    return decorated_function

# 3. Endpoints con CORS aplicado

@app.route("/pokemon", methods=["POST", "OPTIONS"])
@cors_response
def create_pokemon():
    if request.method == "OPTIONS":
        return {}
    if not db:
        return {"error": "Base de datos no inicializada"}, 500
    
    try:
        data = request.json
        pokemon_in = Pokemon(**data)
        created_pokemon = db.create_pokemon(pokemon_in)
        return created_pokemon.model_dump(), 201
    except ValidationError as e:
        return {"error": "Input inválido", "detalles": e.errors()}, 400
    except Exception as e:
        print(f"Error en create_pokemon: {e}")
        return {"error": "Error interno del servidor"}, 500

@app.route("/pokemon/<int:id>", methods=["GET", "OPTIONS"])
@cors_response
def get_pokemon(id: int):
    if request.method == "OPTIONS":
        return {}
    if not db:
        return {"error": "Base de datos no inicializada"}, 500
    pokemon = db.get_pokemon(id)
    if pokemon:
        return pokemon.model_dump()
    else:
        return {"error": "Pokémon no encontrado"}, 404

@app.route("/pokemon", methods=["GET", "OPTIONS"])
@cors_response
def get_all_pokemon():
    if request.method == "OPTIONS":
        return {}
    if not db:
        return {"error": "Base de datos no inicializada"}, 500
    pokemon_list = db.get_all_pokemon()
    return [p.model_dump() for p in pokemon_list]

@app.route("/pokemon/<int:id>", methods=["PUT", "OPTIONS"])
@cors_response
def update_pokemon(id: int):
    if request.method == "OPTIONS":
        return {}
    if not db:
        return {"error": "Base de datos no inicializada"}, 500
    try:
        data = request.json
        pokemon_data = PokemonUpdate(**data)
        updated_pokemon = db.update_pokemon(id, pokemon_data)
        if updated_pokemon:
            return updated_pokemon.model_dump()
        else:
            return {"error": "Pokémon no encontrado o actualización fallida"}, 404
    except ValidationError as e:
        return {"error": "Input inválido", "detalles": e.errors()}, 400
    except Exception as e:
        print(f"Error en update_pokemon: {e}")
        return {"error": "Error interno del servidor"}, 500

@app.route("/pokemon/<int:id>", methods=["DELETE", "OPTIONS"])
@cors_response
def delete_pokemon(id: int):
    if request.method == "OPTIONS":
        return {}
    if not db:
        return {"error": "Base de datos no inicializada"}, 500
    success = db.delete_pokemon(id)
    if success:
        return {}, 204
    else:
        return {"error": "Pokémon no encontrado"}, 404

@app.route("/health", methods=["GET", "OPTIONS"])
@cors_response
def health_check():
    if request.method == "OPTIONS":
        return {}
    return {"status": "ok"}, 200

# 🔹 Ejecutable local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
