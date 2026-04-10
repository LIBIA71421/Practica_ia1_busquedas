from typing import Any, List, Tuple
from base.juego import Juego

class JuegoOthello(Juego):
    # Direcciones de movimiento en un bitboard 8x8: offset y máscara para no salir del borde
    DIRECTIONS = [
        (1, 0xfefefefefefefefe),    # Izquierda a derecha (+1)
        (-1, 0x7f7f7f7f7f7f7f7f),   # Derecha a izquierda (-1)
        (8, 0xffffffffffffffff),    # Arriba a abajo (+8)
        (-8, 0xffffffffffffffff),   # Abajo a arriba (-8)
        (9, 0xfefefefefefefefe),    # Diagonal abajo-derecha (+9)
        (-9, 0x7f7f7f7f7f7f7f7f),   # Diagonal arriba-izquierda (-9)
        (7, 0x7f7f7f7f7f7f7f7f),    # Diagonal abajo-izquierda (+7)
        (-7, 0xfefefefefefefefe)    # Diagonal arriba-derecha (-7)
    ]

    def estado_inicial(self) -> Any:
        # Fichas iniciales:
        # Negras (1) en 28 (d5), 35 (e4)
        # Blancas (-1) en 27 (d4), 36 (e5)
        # bitboards se indexan así: bit 0 es a1, bit 63 es h8.
        black = (1 << 28) | (1 << 35)
        white = (1 << 27) | (1 << 36)
        # tupla de estado: (black_board, white_board, jugador_actual, pases_seguidos)
        return (black, white, 1, 0)

    def _get_flips(self, move_pos: int, player_board: int, opp_board: int) -> int:
        flips_total = 0
        for offset, mask in self.DIRECTIONS:
            flips_dir = 0
            pos = move_pos
            while True:
                pos += offset
                # Verificar que el movimiento se mantiene en los límites dados por la máscara para la pos anterior
                prev_pos = pos - offset
                # Usamos la máscara en el bit shift de la posición anterior para ver si podíamos movernos
                if not ((1 << prev_pos) & mask):
                    flips_dir = 0
                    break
                
                if pos < 0 or pos > 63:
                    flips_dir = 0
                    break

                bit = 1 << pos
                if bit & opp_board:
                    flips_dir |= bit
                elif bit & player_board:
                    break # Ficha propia que encierra a los oponentes
                else:
                    flips_dir = 0 # Casilla vacía, no se encierra nada
                    break
            flips_total |= flips_dir
        return flips_total

    def jugadas_legales(self, estado: Any) -> List[Any]:
        black, white, turn, pases = estado
        if pases >= 2:
            return [] # Juego terminado
            
        player_b = black if turn == 1 else white
        opp_b = white if turn == 1 else black
        empty = ~(black | white) & 0xffffffffffffffff
        
        moves = []
        for i in range(64):
            if (empty & (1 << i)):
                flips = self._get_flips(i, player_b, opp_b)
                if flips > 0:
                    moves.append((i, flips))
        
        if not moves:
            # Paso de turno
            return [None]
        return moves

    def aplicar_jugada(self, estado: Any, jugada: Any) -> Any:
        black, white, turn, pases = estado
        if jugada is None:
            return (black, white, -turn, pases + 1)
            
        pos, flips = jugada
        move_mask = (1 << pos)
        
        if turn == 1:
            new_black = black | move_mask | flips
            new_white = white & ~flips
        else:
            new_white = white | move_mask | flips
            new_black = black & ~flips
            
        return (new_black, new_white, -turn, 0)

    def es_terminal(self, estado: Any) -> bool:
        black, white, turn, pases = estado
        if pases >= 2:
            return True
        if (black | white) == 0xffffffffffffffff:
            return True
        if black == 0 or white == 0:
            return True
        return False

    def _contar_bits(self, n: int) -> int:
        count = 0
        while n:
            n &= n - 1
            count += 1
        return count

    def obtener_resultado(self, estado: Any, jugador: int) -> float:
        black, white, turn, pases = estado
        b_count = self._contar_bits(black)
        w_count = self._contar_bits(white)
        
        if b_count > w_count:
            ganador = 1
        elif w_count > b_count:
            ganador = -1
        else:
            ganador = 0
            
        if ganador == jugador:
            return 1.0
        elif ganador == -jugador:
            return -1.0
        else:
            return 0.0

    def jugador_actual(self, estado: Any) -> int:
        return estado[2]

    def pases_seguidos(self, estado: Any) -> int:
        return estado[3]

    def tableros(self, estado: Any) -> Tuple[int, int]:
        return estado[0], estado[1]
