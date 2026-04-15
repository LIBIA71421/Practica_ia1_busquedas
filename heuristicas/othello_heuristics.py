from typing import Any, Callable, Tuple
from base.juego import Juego
from juegos.othello import JuegoOthello

CORNERS_MASK = (1 << 0) | (1 << 7) | (1 << 56) | (1 << 63)


def _contar_bits(n: int) -> int:
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count


def _normalizar_diff(a: int, b: int) -> float:
    total = a + b
    if total == 0:
        return 0.0
    return (a - b) / total


def _contar_movimientos(juego: JuegoOthello, black: int, white: int, jugador: int) -> int:
    jugadas = juego.jugadas_legales((black, white, jugador, 0))
    if not jugadas or jugadas == [None]:
        return 0
    return len(jugadas)


def _contar_esquinas_jugables(juego: JuegoOthello, black: int, white: int, jugador: int) -> int:
    jugadas = juego.jugadas_legales((black, white, jugador, 0))
    if not jugadas or jugadas == [None]:
        return 0
    return sum(1 for j in jugadas if j is not None and j[0] in (0, 7, 56, 63))


def _frontera(board: int, empty_mask: int) -> int:
    # Fichas propias que tocan al menos una casilla vacia.
    adyacentes_a_vacias = 0
    adyacentes_a_vacias |= ((empty_mask << 1) & 0xFEFEFEFEFEFEFEFE)
    adyacentes_a_vacias |= ((empty_mask >> 1) & 0x7F7F7F7F7F7F7F7F)
    adyacentes_a_vacias |= (empty_mask << 8) & 0xFFFFFFFFFFFFFFFF
    adyacentes_a_vacias |= (empty_mask >> 8) & 0xFFFFFFFFFFFFFFFF
    adyacentes_a_vacias |= ((empty_mask << 9) & 0xFEFEFEFEFEFEFEFE)
    adyacentes_a_vacias |= ((empty_mask << 7) & 0x7F7F7F7F7F7F7F7F)
    adyacentes_a_vacias |= ((empty_mask >> 7) & 0xFEFEFEFEFEFEFEFE)
    adyacentes_a_vacias |= ((empty_mask >> 9) & 0x7F7F7F7F7F7F7F7F)
    return _contar_bits(board & adyacentes_a_vacias)


def _riesgo_casillas(black: int, white: int, jugador_max: int) -> float:
    my_board = black if jugador_max == 1 else white
    opp_board = white if jugador_max == 1 else black

    corners = [0, 7, 56, 63]
    x_by_corner = {0: 9, 7: 14, 56: 49, 63: 54}
    c_by_corner = {
        0: (1, 8),
        7: (6, 15),
        56: (48, 57),
        63: (55, 62),
    }

    my_riesgo = 0
    opp_riesgo = 0
    for c in corners:
        corner_mask = 1 << c
        if (black | white) & corner_mask:
            continue

        x = x_by_corner[c]
        x_mask = 1 << x
        if my_board & x_mask:
            my_riesgo += 2
        elif opp_board & x_mask:
            opp_riesgo += 2

        c1, c2 = c_by_corner[c]
        for c_sq in (c1, c2):
            c_mask = 1 << c_sq
            if my_board & c_mask:
                my_riesgo += 1
            elif opp_board & c_mask:
                opp_riesgo += 1

    return _normalizar_diff(opp_riesgo, my_riesgo)


def get_evaluador_othello(pesos: Tuple[float, float, float, float]) -> Callable[[Juego, Any, int], float]:
    """
    Retorna una funcion de evaluacion robusta manteniendo 4 pesos de entrada.

    Pesos:
    0: Diferencia de fichas (más fuerte en final)
    1: Movilidad y frontera
    2: Esquinas y riesgo X/C
    3: Paridad/tempo en final
    """
    w_fichas, w_mov, w_esq, w_paridad = pesos

    def evaluador(juego: JuegoOthello, estado: Any, jugador_max: int) -> float:
        black, white, turn, _passes = estado

        my_board = black if jugador_max == 1 else white
        opp_board = white if jugador_max == 1 else black

        my_count = _contar_bits(my_board)
        opp_count = _contar_bits(opp_board)
        ocupadas = my_count + opp_count
        vacias = 64 - ocupadas
        empty_mask = (~(black | white)) & 0xFFFFFFFFFFFFFFFF

        # 1) Material: en apertura evitar codicia de discos ayuda a dominar luego.
        diff_fichas = _normalizar_diff(my_count, opp_count)

        # 2) Movilidad exacta de ambos jugadores.
        my_moves = _contar_movimientos(juego, black, white, jugador_max)
        opp_moves = _contar_movimientos(juego, black, white, -jugador_max)
        diff_movilidad = _normalizar_diff(my_moves, opp_moves)

        # 3) Esquinas propias y riesgo en casillas X/C.
        my_esq = _contar_bits(my_board & CORNERS_MASK)
        opp_esq = _contar_bits(opp_board & CORNERS_MASK)
        diff_esquinas = _normalizar_diff(my_esq, opp_esq)
        riesgo_esquinas = _riesgo_casillas(black, white, jugador_max)

        # 4) Presion de esquina: quien puede tomar esquina en el siguiente turno.
        my_corner_moves = _contar_esquinas_jugables(juego, black, white, jugador_max)
        opp_corner_moves = _contar_esquinas_jugables(juego, black, white, -jugador_max)
        diff_corner_moves = _normalizar_diff(my_corner_moves, opp_corner_moves)
        amenaza_esquina = (
            (1.10 if my_corner_moves > 0 else 0.0)
            - (1.60 if opp_corner_moves > 0 else 0.0)
            + (1.60 * diff_corner_moves)
        )

        # 5) Frontera: menos frontera propia suele ser mejor.
        my_frontier = _frontera(my_board, empty_mask)
        opp_frontier = _frontera(opp_board, empty_mask)
        diff_frontera = _normalizar_diff(opp_frontier, my_frontier)

        # 6) Paridad/tempo sencillo para finales cerrados.
        paridad = 1.0 if (vacias % 2 == 1 and turn == jugador_max) or (vacias % 2 == 0 and turn != jugador_max) else -1.0

        fase = ocupadas / 64.0
        if fase < 0.35:
            peso_fichas_fase = -0.30
            peso_mov_fase = 1.35
            peso_esq_fase = 2.10
            peso_paridad_fase = 0.10
        elif fase < 0.75:
            peso_fichas_fase = 0.45
            peso_mov_fase = 1.00
            peso_esq_fase = 2.35
            peso_paridad_fase = 0.30
        else:
            peso_fichas_fase = 1.00
            peso_mov_fase = 0.65
            peso_esq_fase = 2.60
            peso_paridad_fase = 1.00

        movilidad_total = (0.60 * diff_movilidad) + (0.40 * diff_frontera)
        esquinas_total = (0.60 * diff_esquinas) + (0.15 * riesgo_esquinas) + (0.25 * amenaza_esquina)

        # Sesgo agresivo global: presionar movilidad y esquinas aun sin ventaja material.
        sesgo_agresivo = (0.25 * diff_movilidad) + (0.75 * amenaza_esquina)

        return (
            (w_fichas * peso_fichas_fase * diff_fichas)
            + (w_mov * peso_mov_fase * movilidad_total)
            + (w_esq * peso_esq_fase * esquinas_total)
            + (w_paridad * peso_paridad_fase * paridad)
            + (0.55 * sesgo_agresivo)
        )

    return evaluador
