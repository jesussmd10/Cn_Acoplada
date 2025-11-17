from abc import ABC, abstractmethod
from typing import List, Optional
# Importamos los nuevos modelos
from app.model.pokemon import Pokemon, PokemonUpdate

class DBInterface(ABC):
    """Interfaz abstracta para operaciones de base de datos de Pokémon."""

    @abstractmethod
    def create_pokemon(self, pokemon: Pokemon) -> Pokemon:
        """Crea un nuevo Pokémon en la BD."""
        pass

    @abstractmethod
    def get_pokemon(self, pokedex_id: int) -> Optional[Pokemon]:
        """Obtiene un Pokémon por su ID (número de Pokédex)."""
        pass

    @abstractmethod
    def get_all_pokemon(self) -> List[Pokemon]:
        """Obtiene todos los Pokémon."""
        pass

    @abstractmethod
    def update_pokemon(self, pokedex_id: int, pokemon_data: PokemonUpdate) -> Optional[Pokemon]:
        """Actualiza un Pokémon existente."""
        pass

    @abstractmethod
    def delete_pokemon(self, pokedex_id: int) -> bool:
        """Elimina un Pokémon por su ID."""
        pass