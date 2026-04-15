from typing import Any, Callable, Dict, List, Tuple
from base.juego import Juego
from juegos.tictactoe3d import JuegoTicTacToe3D

CENTRO_INDICES = [x + 4 * y + 16 * z for x in (1, 2) for y in (1, 2) for z in (1, 2)]


def _lineas_por_celda(juego: JuegoTicTacToe3D) -> Dict[int, List[List[int]]]:
    cache_name = "_lineas_por_celda_cache"
    if hasattr(juego, cache_name):
        return getattr(juego, cache_name)

    mapeo: Dict[int, List[List[int]]] = {i: [] for i in range(64)}
    for linea in juego.lineas_ganadoras:
        for celda in linea:
            mapeo[celda].append(linea)

    setattr(juego, cache_name, mapeo)
    return mapeo


def _normalizar_diff(a: int, b: int) -> float:
    total = a + b
    if total == 0:
        return 0.0
    return (a - b) / total


def _conteo_tactico(tablero: Tuple[int, ...], juego: JuegoTicTacToe3D, jugador: int) -> Tuple[int, int]:
    """
    Retorna (amenazas_inmediatas, forks) para un jugador en el tablero actual.
    - amenaza inmediata: una jugada que gana al instante.
    - fork: una jugada que crea >=2 amenazas inmediatas para el siguiente turno.
    """
    por_celda = _lineas_por_celda(juego)
    vacias = [i for i, v in enumerate(tablero) if v == 0]

    amenazas = 0
    forks = 0

    for celda in vacias:
        amenazas_creadas = 0
        gana_ya = False

        for linea in por_celda[celda]:
            mias = 0
            rival = 0
            vacias_linea = 0
            for p in linea:
                val = jugador if p == celda else tablero[p]
                if val == jugador:
                    mias += 1
                elif val == -jugador:
                    rival += 1
                else:
                    vacias_linea += 1

            if rival == 0 and mias == 4:
                gana_ya = True
            elif rival == 0 and mias == 3 and vacias_linea == 1:
                amenazas_creadas += 1

        if gana_ya:
            amenazas += 1
        if amenazas_creadas >= 2:
            forks += 1

    return amenazas, forks


def get_evaluador_ttt3d(pesos: Tuple[float, float, float, float]) -> Callable[[Juego, Any, int], float]:
    """
    Pesos base del cromosoma:
    0: lineas abiertas con 1 ficha
    1: lineas abiertas con 2 fichas
    2: lineas abiertas con 3 fichas
    3: control del centro
    """
    w1, w2, w3, w_centro = pesos

    def evaluador(juego: JuegoTicTacToe3D, estado: Any, jugador_max: int) -> float:
        tablero, turn = estado

        score_max = 0.0
        score_min = 0.0
        lineas_3_max = 0
        lineas_3_min = 0

        # 1) Evaluacion estructural de lineas abiertas.
        for linea in juego.lineas_ganadoras:
            fichas_max = 0
            fichas_min = 0
            vacias = 0
            for pos in linea:
                val = tablero[pos]
                if val == jugador_max:
                    fichas_max += 1
                elif val == -jugador_max:
                    fichas_min += 1
                else:
                    vacias += 1

            if fichas_max > 0 and fichas_min == 0:
                if fichas_max == 1:
                    score_max += w1
                elif fichas_max == 2:
                    score_max += w2
                elif fichas_max == 3 and vacias == 1:
                    score_max += w3 * 1.5
                    lineas_3_max += 1
            elif fichas_min > 0 and fichas_max == 0:
                if fichas_min == 1:
                    score_min += w1
                elif fichas_min == 2:
                    score_min += w2
                elif fichas_min == 3 and vacias == 1:
                    score_min += w3 * 1.5
                    lineas_3_min += 1

        # 2) Control de centro con mayor importancia temprana.
        centro_max = 0
        centro_min = 0
        vacias_tablero = 0
        for i, val in enumerate(tablero):
            if val == 0:
                vacias_tablero += 1
            if i in CENTRO_INDICES:
                if val == jugador_max:
                    centro_max += 1
                elif val == -jugador_max:
                    centro_min += 1

        progreso = 1.0 - (vacias_tablero / 64.0)
        factor_centro = 1.35 if progreso < 0.35 else (1.0 if progreso < 0.75 else 0.65)
        score_max += centro_max * w_centro * factor_centro
        score_min += centro_min * w_centro * factor_centro

        # 3) Tactica explicita: ganar ahora / crear forks.
        amenazas_max, forks_max = _conteo_tactico(tablero, juego, jugador_max)
        amenazas_min, forks_min = _conteo_tactico(tablero, juego, -jugador_max)

        diff_amenazas = _normalizar_diff(amenazas_max, amenazas_min)
        diff_forks = _normalizar_diff(forks_max, forks_min)
        diff_lineas3 = _normalizar_diff(lineas_3_max, lineas_3_min)

        # 4) Iniciativa: pequeño bonus al jugador que tiene el turno.
        iniciativa = 0.20 if turn == jugador_max else -0.20

        base = score_max - score_min
        tactica = (abs(w3) + 1.0) * (0.65 * diff_amenazas + 0.35 * diff_lineas3)
        forks = (abs(w2) + 0.8) * diff_forks

        return base + tactica + forks + iniciativa

    return evaluador
