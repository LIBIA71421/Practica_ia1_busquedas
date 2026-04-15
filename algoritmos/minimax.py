from typing import Any, Callable, List
from base.juego import Juego
from base.agente import Agente


class AgenteMinimaxAlfaBeta(Agente):
    def __init__(self, profundidad_maxima: int, evaluador: Callable[[Juego, Any, int], float], modo: str = "balanceado"):
        """
        :param profundidad_maxima: Nivel maximo de exploracion del arbol.
        :param evaluador: Funcion que recibe (juego, estado, jugador_maximizador) y retorna un valor heuristico.
        :param modo: "balanceado" o "agresivo" para desempates y ordenacion.
        """
        self.profundidad_maxima = profundidad_maxima
        self.evaluador = evaluador
        self.modo = modo
        self.nodos_explorados = 0
        self.nodos_podados = 0
        self.jugador_max = None

    def _es_jugada_esquina_othello(self, jugada: Any) -> bool:
        if jugada is None or not isinstance(jugada, tuple) or not jugada:
            return False
        pos = jugada[0]
        return isinstance(pos, int) and pos in (0, 7, 56, 63)

    def _ordenar_jugadas(self, juego: Juego, estado: Any, jugadas: List[Any], es_maximizador: bool) -> List[Any]:
        if len(jugadas) <= 1:
            return jugadas

        ranking = []
        for jugada in jugadas:
            nuevo_estado = juego.aplicar_jugada(estado, jugada)
            score = self.evaluador(juego, nuevo_estado, self.jugador_max)

            # En modo agresivo y Othello, forzar prioridad de esquinas.
            if self.modo == "agresivo" and self._es_jugada_esquina_othello(jugada):
                score += 5000.0 if es_maximizador else -5000.0

            ranking.append((score, jugada))

        ranking.sort(key=lambda x: x[0], reverse=es_maximizador)
        return [j for _, j in ranking]

    def seleccionar_movimiento(self, juego: Juego, estado: Any) -> Any:
        self.nodos_explorados = 0
        self.nodos_podados = 0
        self.jugador_max = juego.jugador_actual(estado)

        mejor_valor = float("-inf")
        mejor_tie = float("-inf")
        mejor_jugada = None
        alfa = float("-inf")
        beta = float("inf")

        jugadas = juego.jugadas_legales(estado)
        if not jugadas:
            return None

        # Regla agresiva extrema para Othello: si hay esquina legal, solo compite entre esquinas.
        if self.modo == "agresivo":
            jugadas_esquina = [j for j in jugadas if self._es_jugada_esquina_othello(j)]
            if jugadas_esquina:
                jugadas = jugadas_esquina

        jugadas_ordenadas = self._ordenar_jugadas(juego, estado, jugadas, es_maximizador=True)

        for jugada in jugadas_ordenadas:
            nuevo_estado = juego.aplicar_jugada(estado, jugada)
            valor = self._minimax(juego, nuevo_estado, self.profundidad_maxima - 1, alfa, beta, False)

            tie = self.evaluador(juego, nuevo_estado, self.jugador_max)
            if self.modo == "agresivo":
                tie += 0.01 * len(juego.jugadas_legales(nuevo_estado))
                if self._es_jugada_esquina_othello(jugada):
                    tie += 1000.0

            if valor > mejor_valor or (valor == mejor_valor and tie > mejor_tie) or mejor_jugada is None:
                mejor_valor = valor
                mejor_tie = tie
                mejor_jugada = jugada

            alfa = max(alfa, mejor_valor)

        return mejor_jugada

    def _minimax(self, juego: Juego, estado: Any, profundidad: int, alfa: float, beta: float, es_maximizador: bool) -> float:
        self.nodos_explorados += 1

        if profundidad == 0 or juego.es_terminal(estado):
            if juego.es_terminal(estado):
                utilidad = juego.obtener_resultado(estado, self.jugador_max)
                if utilidad > 0:
                    return 100000.0 + profundidad
                if utilidad < 0:
                    return -100000.0 - profundidad
                return 0.0
            return self.evaluador(juego, estado, self.jugador_max)

        jugadas = juego.jugadas_legales(estado)
        if not jugadas:
            return self.evaluador(juego, estado, self.jugador_max)

        jugadas = self._ordenar_jugadas(juego, estado, jugadas, es_maximizador=es_maximizador)

        if es_maximizador:
            valor = float("-inf")
            for jugada in jugadas:
                nuevo_estado = juego.aplicar_jugada(estado, jugada)
                v = self._minimax(juego, nuevo_estado, profundidad - 1, alfa, beta, False)
                valor = max(valor, v)
                alfa = max(alfa, valor)
                if beta <= alfa:
                    self.nodos_podados += 1
                    break
            return valor

        valor = float("inf")
        for jugada in jugadas:
            nuevo_estado = juego.aplicar_jugada(estado, jugada)
            v = self._minimax(juego, nuevo_estado, profundidad - 1, alfa, beta, True)
            valor = min(valor, v)
            beta = min(beta, valor)
            if beta <= alfa:
                self.nodos_podados += 1
                break
        return valor
