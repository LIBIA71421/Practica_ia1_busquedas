from typing import Tuple
from base.juego import Juego
from base.agente import Agente

def jugar_partida(juego: Juego, agente1: Agente, agente2: Agente) -> float:
    """
    Juega una partida usando agente1 (jugador 1) vs agente2 (jugador -1).
    Retorna el resultado para el jugador 1.
    """
    estado = juego.estado_inicial()
    
    while not juego.es_terminal(estado):
        jugador_actual = juego.jugador_actual(estado)
        
        if jugador_actual == 1:
            jugada = agente1.seleccionar_movimiento(juego, estado)
        else:
            jugada = agente2.seleccionar_movimiento(juego, estado)
            
        estado = juego.aplicar_jugada(estado, jugada)
        
    return juego.obtener_resultado(estado, 1)

def simular_torneo(juego: Juego, agente1: Agente, agente2: Agente, num_partidas: int = 100) -> Tuple[int, int, int]:
    """
    Alterna turnos. Retorna (victorias, derrotas, empates) desde la perspectiva de agente1.
    """
    victorias_a1 = 0
    derrotas_a1 = 0
    empates = 0
    
    for i in range(num_partidas):
        if i % 2 == 0:
            res = jugar_partida(juego, agente1, agente2)
            if res > 0: victorias_a1 += 1
            elif res < 0: derrotas_a1 += 1
            else: empates += 1
        else:
            # agente2 es el jugador 1, agente1 es el jugador -1
            res = jugar_partida(juego, agente2, agente1)
            if res < 0: victorias_a1 += 1  # agente2 perdió, por ende a1 ganó
            elif res > 0: derrotas_a1 += 1
            else: empates += 1
            
    return victorias_a1, derrotas_a1, empates
