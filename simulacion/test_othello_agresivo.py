import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algoritmos.minimax import AgenteMinimaxAlfaBeta
from base.agente import AgenteAleatorio
from config.perfiles_ia import obtener_perfil
from heuristicas.othello_heuristics import get_evaluador_othello
from juegos.othello import JuegoOthello
from simulacion.torneo import simular_torneo


def _buscar_estado_con_esquina_legal(juego: JuegoOthello, max_intentos: int = 200, pasos_max: int = 120):
    for seed in range(max_intentos):
        random.seed(seed)
        estado = juego.estado_inicial()
        for _ in range(pasos_max):
            if juego.es_terminal(estado):
                break
            jugadas = juego.jugadas_legales(estado)
            esquinas = [j for j in jugadas if j is not None and isinstance(j, tuple) and j[0] in (0, 7, 56, 63)]
            if esquinas:
                return estado, esquinas
            estado = juego.aplicar_jugada(estado, random.choice(jugadas))
    return None, []


def main() -> None:
    juego = JuegoOthello()
    perfil = obtener_perfil("agresivo")["othello"]
    agente_agresivo = AgenteMinimaxAlfaBeta(
        profundidad_maxima=3,
        evaluador=get_evaluador_othello(perfil["pesos"]),
        modo="agresivo",
    )

    estado, esquinas_legales = _buscar_estado_con_esquina_legal(juego)
    if estado is None:
        print("[WARN] No se encontro estado con esquina legal en la busqueda aleatoria.")
    else:
        jugada = agente_agresivo.seleccionar_movimiento(juego, estado)
        ok_esquina = isinstance(jugada, tuple) and jugada[0] in (0, 7, 56, 63)
        print(f"[Check esquina] jugada={jugada} | es_esquina={ok_esquina}")
        if not ok_esquina:
            raise AssertionError("El agente agresivo no priorizo esquina cuando era legal.")

    random.seed(42)
    aleatorio = AgenteAleatorio()
    v, d, e = simular_torneo(juego, agente_agresivo, aleatorio, num_partidas=12)
    print(f"[Torneo corto] Agresivo vs Aleatorio -> V:{v} D:{d} E:{e}")


if __name__ == "__main__":
    main()

