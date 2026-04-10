import random
from abc import ABC, abstractmethod
from typing import Any
from base.juego import Juego

class Agente(ABC):
    @abstractmethod
    def seleccionar_movimiento(self, juego: Juego, estado: Any) -> Any:
        """Selecciona una jugada legal dado un juego y un estado."""
        pass

class AgenteAleatorio(Agente):
    def seleccionar_movimiento(self, juego: Juego, estado: Any) -> Any:
        jugadas = juego.jugadas_legales(estado)
        if not jugadas:
            return None
        return random.choice(jugadas)
