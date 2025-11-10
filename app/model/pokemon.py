# app/model/pokemon.py
from pydantic import BaseModel, Field
from typing import Optional

class Pokemon(BaseModel):
    """
    Modelo de datos para un Pokémon.
    El 'pokedex_id' es la clave principal.
    """
    pokedex_id: int = Field(..., gt=0) # '...' significa que es obligatorio y 'gt=0' que debe ser > 0
    name: str
    pokemon_type: str # Para simplicidad, usamos un solo tipo. Podría ser List[str]

class PokemonUpdate(BaseModel):
    """
    Modelo para actualizar un Pokémon.
    Todos los campos son opcionales. No permitimos cambiar el ID.
    """
    name: Optional[str] = None
    pokemon_type: Optional[str] = None