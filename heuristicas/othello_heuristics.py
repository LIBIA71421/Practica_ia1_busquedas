from typing import Any, Callable, Tuple
import math
from base.juego import Juego
from juegos.othello import JuegoOthello

CORNERS_MASK = (1 << 0) | (1 << 7) | (1 << 56) | (1 << 63)

def _contar_bits(n: int) -> int:
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count

def get_evaluador_othello(pesos: Tuple[float, float, float, float]) -> Callable[[Juego, Any, int], float]:
    """
    Retorna una función de evaluación que usa un vector de pesos.
    Características:
    0: Diferencia de fichas.
    1: Movilidad (estimada simplificadamente o usando la api del juego).
    2: Esquinas controladas.
    3: Paridad de fichas (si hay menos fichas totales, puede ser distinto).
    """
    w_fichas, w_mov, w_esq, w_paridad = pesos

    def evaluador(juego: JuegoOthello, estado: Any, jugador_max: int) -> float:
        black, white, turn, passes = estado
        
        my_board = black if jugador_max == 1 else white
        opp_board = white if jugador_max == 1 else black
        
        my_count = _contar_bits(my_board)
        opp_count = _contar_bits(opp_board)
        
        # 0. Diferencia de fichas (-1 a 1)
        total = my_count + opp_count
        diff_fichas = (my_count - opp_count) / total if total > 0 else 0
        
        # 1. Movilidad (diferencia de jugadas legales)
        # Nota: calcular movilidad real del rival requiere simular cambio de turno,
        # simplificaremos evaluando movilidad si es nuestro turno, sino negamos si es suyo.
        my_moves = 0
        opp_moves = 0
        
        # Un aproximado rápido para Othello es contar la frontera vacía, pero usaremos jugadas si es posible
        if turn == jugador_max:
            jugadas = juego.jugadas_legales(estado)
            my_moves = 0 if jugadas == [None] else len(jugadas)
        else:
            jugadas = juego.jugadas_legales(estado)
            opp_moves = 0 if jugadas == [None] else len(jugadas)
        
        diff_movilidad = 0
        if my_moves + opp_moves > 0:
            diff_movilidad = (my_moves - opp_moves) / (my_moves + opp_moves)
            
        # 2. Control de esquinas
        my_esq = _contar_bits(my_board & CORNERS_MASK)
        opp_esq = _contar_bits(opp_board & CORNERS_MASK)
        diff_esquinas = 0
        if my_esq + opp_esq > 0:
            diff_esquinas = (my_esq - opp_esq) / (my_esq + opp_esq)
            
        # 3. Paridad
        # Paridad es buena si hemos jugado una ficha, normalmente es 1 en Othello si total es par (depende)
        # Una paridad simple es si quedan casillas pares e inician moviendo el rival.
        casillas_vacias = 64 - total
        paridad = 1 if casillas_vacias % 2 == 0 else -1

        return (w_fichas * diff_fichas) + (w_mov * diff_movilidad) + (w_esq * diff_esquinas) + (w_paridad * paridad)

    return evaluador
