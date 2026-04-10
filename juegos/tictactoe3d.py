from typing import Any, List, Tuple
from base.juego import Juego

class JuegoTicTacToe3D(Juego):
    def __init__(self):
        self.lineas_ganadoras = self._generar_lineas_ganadoras()

    def _generar_lineas_ganadoras(self) -> List[List[int]]:
        lineas = []
        # Líneas ortogonales
        for i in range(4):
            for j in range(4):
                # Paralelas a X (variando x, fijando y=j, z=i)
                lineas.append([x + 4*j + 16*i for x in range(4)])
                # Paralelas a Y (variando y, fijando x=j, z=i)
                lineas.append([j + 4*y + 16*i for y in range(4)])
                # Paralelas a Z (variando z, fijando x=j, y=i)
                lineas.append([j + 4*i + 16*z for z in range(4)])
                
        # Diagonales de planos (2D)
        for i in range(4):
            # Plano XY (fijando z=i)
            lineas.append([k + 4*k + 16*i for k in range(4)])
            lineas.append([(3-k) + 4*k + 16*i for k in range(4)])
            # Plano XZ (fijando y=i)
            lineas.append([k + 4*i + 16*k for k in range(4)])
            lineas.append([(3-k) + 4*i + 16*k for k in range(4)])
            # Plano YZ (fijando x=i)
            lineas.append([i + 4*k + 16*k for k in range(4)])
            lineas.append([i + 4*(3-k) + 16*k for k in range(4)])
            
        # Diagonales principales (3D)
        lineas.append([k + 4*k + 16*k for k in range(4)])         # (0,0,0) a (3,3,3)
        lineas.append([(3-k) + 4*k + 16*k for k in range(4)])     # (3,0,0) a (0,3,3)
        lineas.append([k + 4*(3-k) + 16*k for k in range(4)])     # (0,3,0) a (3,0,3)
        lineas.append([(3-k) + 4*(3-k) + 16*k for k in range(4)]) # (3,3,0) a (0,0,3)
        
        return lineas

    def estado_inicial(self) -> Any:
        # tablero es una tupla de 64 ceros. 1 es jugador_1, -1 es jugador_2
        tablero = tuple([0] * 64)
        return (tablero, 1) # (tablero, jugador_actual)

    def jugadas_legales(self, estado: Any) -> List[Any]:
        tablero, turn = estado
        if self.es_terminal(estado):
            return []
            
        jugadas = [i for i, val in enumerate(tablero) if val == 0]
        return jugadas

    def aplicar_jugada(self, estado: Any, jugada: Any) -> Any:
        tablero, turn = estado
        # Crear nuevo tablero con la jugada
        nuevo_tablero = list(tablero)
        nuevo_tablero[jugada] = turn
        return (tuple(nuevo_tablero), -turn)

    def es_terminal(self, estado: Any) -> bool:
        tablero, turn = estado
        return self._comprobar_ganador(tablero) != 0 or 0 not in tablero

    def _comprobar_ganador(self, tablero: Tuple[int, ...]) -> int:
        for linea in self.lineas_ganadoras:
            suma = sum(tablero[i] for i in linea)
            if suma == 4:
                return 1
            elif suma == -4:
                return -1
        return 0

    def obtener_resultado(self, estado: Any, jugador: int) -> float:
        tablero, turn = estado
        ganador = self._comprobar_ganador(tablero)
        if ganador == jugador:
            return 1.0
        elif ganador == -jugador:
            return -1.0
        else:
            return 0.0

    def jugador_actual(self, estado: Any) -> int:
        return estado[1]
