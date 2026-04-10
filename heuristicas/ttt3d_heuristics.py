from typing import Any, Callable, Tuple
from base.juego import Juego
from juegos.tictactoe3d import JuegoTicTacToe3D

CENTRO_INDICES = [x + 4*y + 16*z for x in (1,2) for y in (1,2) for z in (1,2)]

def get_evaluador_ttt3d(pesos: Tuple[float, float, float, float]) -> Callable[[Juego, Any, int], float]:
    """
    Pesos:
    0: Líneas de 1 ficha (y 0 del rival)
    1: Líneas de 2 fichas (y 0 del rival)
    2: Líneas de 3 fichas (y 0 del rival)
    3: Control del centro (fichas en el centro 2x2x2)
    """
    w1, w2, w3, w_centro = pesos

    def evaluador(juego: JuegoTicTacToe3D, estado: Any, jugador_max: int) -> float:
        tablero, turn = estado
        
        score_max = 0.0
        score_min = 0.0
        
        # 1-3. Evaluar líneas
        for linea in juego.lineas_ganadoras:
            fichas_max = 0
            fichas_min = 0
            for pos in linea:
                val = tablero[pos]
                if val == jugador_max:
                    fichas_max += 1
                elif val == -jugador_max:
                    fichas_min += 1
                    
            # Si solo tiene fichas de un jugador, es una línea "abierta" prometedora
            if fichas_max > 0 and fichas_min == 0:
                if fichas_max == 1: score_max += w1
                elif fichas_max == 2: score_max += w2
                elif fichas_max == 3: score_max += w3
            elif fichas_min > 0 and fichas_max == 0:
                if fichas_min == 1: score_min += w1
                elif fichas_min == 2: score_min += w2
                elif fichas_min == 3: score_min += w3
                
        # 4. Control del centro
        centro_max = 0
        centro_min = 0
        for pos in CENTRO_INDICES:
            if tablero[pos] == jugador_max:
                centro_max += 1
            elif tablero[pos] == -jugador_max:
                centro_min += 1
                
        score_max += centro_max * w_centro
        score_min += centro_min * w_centro
        
        return score_max - score_min

    return evaluador
