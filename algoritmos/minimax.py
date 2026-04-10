from typing import Any, Callable
from base.juego import Juego
from base.agente import Agente

class AgenteMinimaxAlfaBeta(Agente):
    def __init__(self, profundidad_maxima: int, evaluador: Callable[[Juego, Any, int], float]):
        """
        :param profundidad_maxima: Nivel máximo de exploración del árbol.
        :param evaluador: Función que recibe (juego, estado, jugador_maximizador) y retorna un valor heurístico.
        """
        self.profundidad_maxima = profundidad_maxima
        self.evaluador = evaluador
        self.nodos_explorados = 0
        self.nodos_podados = 0
        self.jugador_max = None

    def seleccionar_movimiento(self, juego: Juego, estado: Any) -> Any:
        self.nodos_explorados = 0
        self.nodos_podados = 0
        self.jugador_max = juego.jugador_actual(estado)
        
        mejor_valor = float('-inf')
        mejor_jugada = None
        alfa = float('-inf')
        beta = float('inf')
        
        jugadas = juego.jugadas_legales(estado)
        if not jugadas:
            return None
            
        for jugada in jugadas:
            nuevo_estado = juego.aplicar_jugada(estado, jugada)
            valor = self._minimax(juego, nuevo_estado, self.profundidad_maxima - 1, alfa, beta, False)
            
            if valor > mejor_valor or mejor_jugada is None:
                mejor_valor = valor
                mejor_jugada = jugada
                
            alfa = max(alfa, mejor_valor)
        
        return mejor_jugada

    def _minimax(self, juego: Juego, estado: Any, profundidad: int, alfa: float, beta: float, es_maximizador: bool) -> float:
        self.nodos_explorados += 1
        
        if profundidad == 0 or juego.es_terminal(estado):
            if juego.es_terminal(estado):
                utilidad = juego.obtener_resultado(estado, self.jugador_max)
                # Usamos una magnitud grande para la victoria/derrota absoluta, manteniéndolo como float
                return utilidad * 100000.0 
            return self.evaluador(juego, estado, self.jugador_max)
            
        jugadas = juego.jugadas_legales(estado)
        if not jugadas:
            return self.evaluador(juego, estado, self.jugador_max)

        if es_maximizador:
            valor = float('-inf')
            for jugada in jugadas:
                nuevo_estado = juego.aplicar_jugada(estado, jugada)
                v = self._minimax(juego, nuevo_estado, profundidad - 1, alfa, beta, False)
                valor = max(valor, v)
                alfa = max(alfa, valor)
                if beta <= alfa:
                    self.nodos_podados += 1
                    break
            return valor
        else:
            valor = float('inf')
            for jugada in jugadas:
                nuevo_estado = juego.aplicar_jugada(estado, jugada)
                v = self._minimax(juego, nuevo_estado, profundidad - 1, alfa, beta, True)
                valor = min(valor, v)
                beta = min(beta, valor)
                if beta <= alfa:
                    self.nodos_podados += 1
                    break
            return valor
