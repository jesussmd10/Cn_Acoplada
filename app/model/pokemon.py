
from pydantic import BaseModel, Field
from typing import Optional

class Pokemon(BaseModel):
    """
    Modelo de datos para un Pokémon.
    El 'pokedex_id' es la clave principal.
    """
    pokedex_id: int = Field(..., gt=0) # ID positivo
    name: str
    pokemon_type: str # Para simplicidad, usamos un solo tipo.

class PokemonUpdate(BaseModel):
    """
    Modelo para actualizar un Pokémon.
    Todos los campos son opcionales. No permitimos cambiar el ID.
    """
    name: Optional[str] = None
    pokemon_type: Optional[str] = None