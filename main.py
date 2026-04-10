import sys
from juegos.othello import JuegoOthello
from juegos.tictactoe3d import JuegoTicTacToe3D
from algoritmos.minimax import AgenteMinimaxAlfaBeta
from base.agente import AgenteAleatorio
from heuristicas.othello_heuristics import get_evaluador_othello
from heuristicas.ttt3d_heuristics import get_evaluador_ttt3d
from optimizacion.genetico import AlgoritmoGenetico
from simulacion.torneo import simular_torneo

def entrenar_othello_ag() -> tuple:
    print("Iniciando optimización genética para Othello...")
    juego = JuegoOthello()
    agente_aleatorio = AgenteAleatorio()

    def evaluar_fitness(pesos):
        evaluador = get_evaluador_othello(pesos)
        # Profundidad 2 para entrenamiento rápido
        agente_minimax = AgenteMinimaxAlfaBeta(profundidad_maxima=2, evaluador=evaluador) 
        v, d, e = simular_torneo(juego, agente_minimax, agente_aleatorio, num_partidas=10)
        return (v + 0.5 * e) / 10.0

    ag = AlgoritmoGenetico(tam_poblacion=5, tam_cromosoma=4)
    mejor_ind, mejor_fit = ag.ejecutar(evaluar_fitness, generaciones=3)
    print(f"Mejores pesos Othello: {mejor_ind} con fitness {mejor_fit}")
    return mejor_ind

def entrenar_ttt3d_ag() -> tuple:
    print("Iniciando optimización genética para TTT3D...")
    juego = JuegoTicTacToe3D()
    agente_aleatorio = AgenteAleatorio()

    def evaluar_fitness(pesos):
        evaluador = get_evaluador_ttt3d(pesos)
        # Profundidad 1 para entrenamiento rápido (el tablero es muy grande para simular masivamente)
        agente_minimax = AgenteMinimaxAlfaBeta(profundidad_maxima=1, evaluador=evaluador) 
        v, d, e = simular_torneo(juego, agente_minimax, agente_aleatorio, num_partidas=10)
        return (v + 0.5 * e) / 10.0

    ag = AlgoritmoGenetico(tam_poblacion=5, tam_cromosoma=4)
    mejor_ind, mejor_fit = ag.ejecutar(evaluar_fitness, generaciones=3)
    print(f"Mejores pesos TTT3D: {mejor_ind} con fitness {mejor_fit}")
    return mejor_ind

def experimento_final(pesos_othello: tuple, pesos_ttt3d: tuple):
    print("\n--- Fase 4: Experimentos Finales ---")
    juego_othello = JuegoOthello()
    juego_ttt3d = JuegoTicTacToe3D()
    
    agente_aleatorio = AgenteAleatorio()
    
    # Experimentos Othello
    evaluador_o = get_evaluador_othello(pesos_othello)
    agente_o = AgenteMinimaxAlfaBeta(profundidad_maxima=3, evaluador=evaluador_o)
    
    print("Jugando Othello: AG opt (Prof 3) vs Aleatorio (20 partidas)...")
    v_o, d_o, e_o = simular_torneo(juego_othello, agente_o, agente_aleatorio, num_partidas=20)
    print(f"Othello -> Victorias: {v_o}, Derrotas: {d_o}, Empates: {e_o} | WinRate: {v_o/20.0}")
    
    # Experimentos TTT3D
    evaluador_t = get_evaluador_ttt3d(pesos_ttt3d)
    agente_t = AgenteMinimaxAlfaBeta(profundidad_maxima=2, evaluador=evaluador_t)
    
    print("Jugando TicTacToe3D: AG opt (Prof 2) vs Aleatorio (20 partidas)...")
    v_t, d_t, e_t = simular_torneo(juego_ttt3d, agente_t, agente_aleatorio, num_partidas=20)
    print(f"TTT3D -> Victorias: {v_t}, Derrotas: {d_t}, Empates: {e_t} | WinRate: {v_t/20.0}")

if __name__ == "__main__":
    print("--------------------------------------------------")
    print(" Implementación de Agentes: Othello y 3D TTT")
    print("--------------------------------------------------\n")
    best_o = entrenar_othello_ag()
    print("\n")
    best_t = entrenar_ttt3d_ag()
    experimento_final(best_o, best_t)
    print("\nProceso finalizado.")
