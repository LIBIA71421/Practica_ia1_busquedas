from abc import ABC, abstractmethod
from typing import Any, List

class Juego(ABC):
    @abstractmethod
    def estado_inicial(self) -> Any:
        """Devuelve el estado inicial del juego."""
        pass

    @abstractmethod
    def jugadas_legales(self, estado: Any) -> List[Any]:
        """Devuelve la lista de movimientos legales para el jugador actual en el estado dado.
        Si el jugador no tiene movimientos pero el juego no ha terminado, puede retornar [None]."""
        pass

    @abstractmethod
    def aplicar_jugada(self, estado: Any, jugada: Any) -> Any:
        """Aplica la jugada al estado y devuelve el nuevo estado (sin modificar el original)."""
        pass

    @abstractmethod
    def es_terminal(self, estado: Any) -> bool:
        """Verifica si el estado es final (fin del juego)."""
        pass

    @abstractmethod
    def obtener_resultado(self, estado: Any, jugador: int) -> float:
        """Devuelve un valor de utilidad al finalizar el juego para el jugador especificado.
        Generalmente 1.0 (victoria), -1.0 (derrota), 0.0 (empate)."""
        pass
    
    @abstractmethod
    def jugador_actual(self, estado: Any) -> int:
        """Devuelve el identificador del jugador que debe mover en el estado actual (ej. 1 o -1)."""
        pass
