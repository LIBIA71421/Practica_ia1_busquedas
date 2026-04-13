"""
Pipeline de Entrenamiento y Evaluación — Agentes Inteligentes
Othello & TicTacToe 3D (4x4x4) con Minimax Alfa-Beta + Algoritmo Genético

Genera gráficas de:
  1. Evolución del fitness durante el entrenamiento genético
  2. Resultados de experimentos finales (victorias/derrotas/empates)
  3. Pesos optimizados por el algoritmo genético
"""
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from juegos.othello import JuegoOthello
from juegos.tictactoe3d import JuegoTicTacToe3D
from algoritmos.minimax import AgenteMinimaxAlfaBeta
from base.agente import AgenteAleatorio
from heuristicas.othello_heuristics import get_evaluador_othello
from heuristicas.ttt3d_heuristics import get_evaluador_ttt3d
from optimizacion.genetico import AlgoritmoGenetico
from simulacion.torneo import simular_torneo


# ─── Configuración de estilo de gráficas ─────────────────────────────────────
plt.style.use('dark_background')
COLORS = {
    'primary':   '#6c63ff',
    'secondary': '#ff6584',
    'success':   '#43e97b',
    'warning':   '#ffb347',
    'bg_card':   '#1a1f2e',
    'text':      '#f0f0f8',
    'grid':      '#2d3255',
}


# ─── Funciones de entrenamiento ───────────────────────────────────────────────

def entrenar_othello_ag(poblacion=10, generaciones=5, partidas=10) -> tuple:
    print("\n[AG] Iniciando optimización genética para Othello...")
    print(f"   Población: {poblacion} | Generaciones: {generaciones} | Partidas/eval: {partidas}")
    juego = JuegoOthello()
    agente_aleatorio = AgenteAleatorio()

    def evaluar_fitness(pesos):
        evaluador = get_evaluador_othello(pesos)
        agente_minimax = AgenteMinimaxAlfaBeta(profundidad_maxima=2, evaluador=evaluador)
        v, d, e = simular_torneo(juego, agente_minimax, agente_aleatorio, num_partidas=partidas)
        return (v + 0.5 * e) / partidas

    ag = AlgoritmoGenetico(tam_poblacion=poblacion, tam_cromosoma=4)
    mejor_ind, mejor_fit, historial = ag.ejecutar(evaluar_fitness, generaciones=generaciones)
    print(f"   [OK] Mejores pesos Othello: {tuple(round(w, 4) for w in mejor_ind)}")
    print(f"   [OK] Fitness: {mejor_fit:.3f}")
    return mejor_ind, historial


def entrenar_ttt3d_ag(poblacion=10, generaciones=5, partidas=10) -> tuple:
    print("\n[AG] Iniciando optimización genética para TicTacToe 3D...")
    print(f"   Población: {poblacion} | Generaciones: {generaciones} | Partidas/eval: {partidas}")
    juego = JuegoTicTacToe3D()
    agente_aleatorio = AgenteAleatorio()

    def evaluar_fitness(pesos):
        evaluador = get_evaluador_ttt3d(pesos)
        agente_minimax = AgenteMinimaxAlfaBeta(profundidad_maxima=1, evaluador=evaluador)
        v, d, e = simular_torneo(juego, agente_minimax, agente_aleatorio, num_partidas=partidas)
        return (v + 0.5 * e) / partidas

    ag = AlgoritmoGenetico(tam_poblacion=poblacion, tam_cromosoma=4)
    mejor_ind, mejor_fit, historial = ag.ejecutar(evaluar_fitness, generaciones=generaciones)
    print(f"   [OK] Mejores pesos TTT3D: {tuple(round(w, 4) for w in mejor_ind)}")
    print(f"   [OK] Fitness: {mejor_fit:.3f}")
    return mejor_ind, historial


def experimento_final(pesos_othello, pesos_ttt3d, num_partidas=20):
    print(f"\n[Final] Experimentos Finales ({num_partidas} partidas c/u)")
    juego_othello = JuegoOthello()
    juego_ttt3d = JuegoTicTacToe3D()
    agente_aleatorio = AgenteAleatorio()

    # Othello
    evaluador_o = get_evaluador_othello(pesos_othello)
    agente_o = AgenteMinimaxAlfaBeta(profundidad_maxima=3, evaluador=evaluador_o)
    print("   Jugando Othello: AG optimizado (Prof 3) vs Aleatorio...")
    v_o, d_o, e_o = simular_torneo(juego_othello, agente_o, agente_aleatorio, num_partidas=num_partidas)
    print(f"   Othello -> V:{v_o} D:{d_o} E:{e_o} | WinRate: {v_o/num_partidas:.1%}")

    # TTT3D
    evaluador_t = get_evaluador_ttt3d(pesos_ttt3d)
    agente_t = AgenteMinimaxAlfaBeta(profundidad_maxima=2, evaluador=evaluador_t)
    print("   Jugando TTT3D: AG optimizado (Prof 2) vs Aleatorio...")
    v_t, d_t, e_t = simular_torneo(juego_ttt3d, agente_t, agente_aleatorio, num_partidas=num_partidas)
    print(f"   TTT3D  -> V:{v_t} D:{d_t} E:{e_t} | WinRate: {v_t/num_partidas:.1%}")

    return (v_o, d_o, e_o), (v_t, d_t, e_t)


# ─── Funciones de graficado ───────────────────────────────────────────────────

def graficar_entrenamiento(hist_othello, hist_ttt3d):
    """Gráfica de evolución del fitness durante entrenamiento genético."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Evolución del Fitness — Algoritmo Genético', 
                 fontsize=16, fontweight='bold', color=COLORS['text'], y=1.02)

    for ax, hist, titulo in [
        (axes[0], hist_othello, 'Othello'),
        (axes[1], hist_ttt3d, 'TicTacToe 3D (4×4×4)')
    ]:
        gens = range(1, len(hist['mejor_fitness']) + 1)

        # Área sombreada entre promedio y mejor
        ax.fill_between(gens, hist['prom_fitness'], hist['mejor_fitness'],
                         alpha=0.15, color=COLORS['primary'])

        # Líneas
        ax.plot(gens, hist['mejor_fitness'], 'o-', color=COLORS['primary'],
                linewidth=2.5, markersize=8, label='Mejor fitness', zorder=5)
        ax.plot(gens, hist['prom_fitness'], 's--', color=COLORS['secondary'],
                linewidth=1.8, markersize=6, label='Promedio población', zorder=4)

        # Anotaciones en el mejor y último punto
        best_val = max(hist['mejor_fitness'])
        best_gen = hist['mejor_fitness'].index(best_val) + 1
        ax.annotate(f'{best_val:.3f}', xy=(best_gen, best_val),
                    xytext=(0, 14), textcoords='offset points',
                    ha='center', fontsize=10, fontweight='bold',
                    color=COLORS['success'],
                    arrowprops=dict(arrowstyle='->', color=COLORS['success'], lw=1.5))

        ax.set_title(titulo, fontsize=13, fontweight='bold', pad=10)
        ax.set_xlabel('Generación', fontsize=11)
        ax.set_ylabel('Fitness', fontsize=11)
        ax.set_xticks(list(gens))
        ax.legend(loc='lower right', framealpha=0.7, fontsize=9)
        ax.grid(True, alpha=0.2, color=COLORS['grid'])
        ax.set_facecolor('#0d0f14')
        ax.set_ylim(bottom=0, top=1.05)

    fig.patch.set_facecolor('#0d0f14')
    plt.tight_layout()
    plt.savefig('entrenamiento_fitness.png', dpi=150, bbox_inches='tight',
                facecolor='#0d0f14', edgecolor='none')
    plt.close()

def graficar_experimentos(res_othello, res_ttt3d, num_partidas):
    """Gráfica de barras con resultados de experimentos finales."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle('Resultados — AG Optimizado vs Agente Aleatorio',
                 fontsize=16, fontweight='bold', color=COLORS['text'], y=1.02)

    categorias = ['Victorias', 'Derrotas', 'Empates']
    colores = [COLORS['success'], COLORS['secondary'], COLORS['primary']]

    for ax, res, titulo in [
        (axes[0], res_othello, 'Othello (Prof. 3)'),
        (axes[1], res_ttt3d, 'TicTacToe 3D (Prof. 2)')
    ]:
        valores = list(res)
        bars = ax.bar(categorias, valores, color=colores,
                      edgecolor='white', linewidth=0.5, width=0.6, zorder=3)

        # Valor encima de cada barra
        for bar, val in zip(bars, valores):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.4,
                    str(val), ha='center', fontweight='bold', fontsize=13,
                    color=COLORS['text'])

        # Win rate como subtítulo
        winrate = valores[0] / num_partidas
        ax.set_title(f'{titulo}\nWin Rate: {winrate:.0%}',
                     fontsize=12, fontweight='bold', pad=10)
        ax.set_ylabel('Partidas', fontsize=11)
        ax.set_ylim(0, max(valores) * 1.25 + 1)
        ax.grid(True, axis='y', alpha=0.2, color=COLORS['grid'], zorder=0)
        ax.set_facecolor('#0d0f14')

    fig.patch.set_facecolor('#0d0f14')
    plt.tight_layout()
    plt.savefig('experimento_resultados.png', dpi=150, bbox_inches='tight',
                facecolor='#0d0f14', edgecolor='none')
    plt.close()

def graficar_pesos(pesos_othello, pesos_ttt3d):
    """Gráfica de barras horizontales con los pesos optimizados."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle('Pesos Optimizados por el Algoritmo Genético',
                 fontsize=16, fontweight='bold', color=COLORS['text'], y=1.02)

    configs = [
        (axes[0], pesos_othello, 'Othello',
         ['Fichas', 'Movilidad', 'Esquinas', 'Paridad']),
        (axes[1], pesos_ttt3d, 'TicTacToe 3D',
         ['Línea 1 ficha', 'Línea 2 fichas', 'Línea 3 fichas', 'Centro']),
    ]

    for ax, pesos, titulo, labels in configs:
        vals = list(pesos)
        colors = [COLORS['primary'] if v >= 0 else COLORS['secondary'] for v in vals]

        bars = ax.barh(labels, vals, color=colors, edgecolor='white',
                       linewidth=0.5, height=0.55, zorder=3)

        # Valor al lado de cada barra
        for bar, val in zip(bars, vals):
            offset = 0.02 if val >= 0 else -0.02
            ha = 'left' if val >= 0 else 'right'
            ax.text(val + offset, bar.get_y() + bar.get_height() / 2.,
                    f'{val:.3f}', ha=ha, va='center', fontweight='bold',
                    fontsize=11, color=COLORS['text'])

        ax.axvline(x=0, color=COLORS['grid'], linewidth=1, zorder=2)
        ax.set_title(titulo, fontsize=13, fontweight='bold', pad=10)
        ax.set_xlabel('Peso', fontsize=11)
        ax.grid(True, axis='x', alpha=0.15, color=COLORS['grid'], zorder=0)
        ax.set_facecolor('#0d0f14')

        # Ajustar límites para que las etiquetas quepan
        margin = max(abs(v) for v in vals) * 0.35
        ax.set_xlim(min(vals) - margin, max(vals) + margin)

    fig.patch.set_facecolor('#0d0f14')
    plt.tight_layout()
    plt.savefig('pesos_optimizados.png', dpi=150, bbox_inches='tight',
                facecolor='#0d0f14', edgecolor='none')
    plt.close()

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  [IA] Agentes Inteligentes — Entrenamiento y Evaluación")
    print("=" * 60)

    # Fase 1: Entrenamiento con Algoritmo Genético
    best_o, hist_o = entrenar_othello_ag(poblacion=10, generaciones=5, partidas=10)
    best_t, hist_t = entrenar_ttt3d_ag(poblacion=10, generaciones=5, partidas=10)

    # Fase 2: Gráfica de evolución del fitness
    print("\n[Graf] Generando gráfica de entrenamiento...")
    graficar_entrenamiento(hist_o, hist_t)

    # Fase 3: Gráfica de pesos optimizados
    print("[Graf] Generando gráfica de pesos optimizados...")
    graficar_pesos(best_o, best_t)

    # Fase 4: Experimentos finales
    num_exp = 20
    res_o, res_t = experimento_final(best_o, best_t, num_partidas=num_exp)

    # Fase 5: Gráfica de resultados
    print("\n[Graf] Generando gráfica de resultados...")
    graficar_experimentos(res_o, res_t, num_exp)

    print("\n[OK] Proceso finalizado. Gráficas guardadas:")
    print("   • entrenamiento_fitness.png")
    print("   • pesos_optimizados.png")
    print("   • experimento_resultados.png")
