# Implementación de Agentes Inteligentes para Othello y 3D Tic-Tac-Toe

Este documento describe el plan de implementación para la práctica sobre agentes inteligente en juegos computacionales, abordando el desarrollo modular por fases según los requerimientos solicitados (Minimax con Poda Alfa-Beta, funciones heurísticas y optimización por Algoritmos Genéticos).

## User Review Required

> [!IMPORTANT]
> **Aprobación del Plan:** Por favor, revisa la arquitectura y los módulos propuestos. Una vez apruebes el plan, comenzaré con la *Fase 1* correspondiente a la base arquitectónica y el algoritmo Minimax con Poda Alfa-Beta, para posteriormente ir ejecutando las demás fases. ¿Estás de acuerdo con la estructuración del proyecto en los paquetes descritos a continuación?

## Proposed Changes

Propongo estructurar el código de manera modular bajo el workspace actual (`c:\Users\baka\Downloads\sisInt\Practica_ia1_busquedas`), utilizando Python.

### Paquete Base (Core)
Establece las clases abstractas fundamentales que guiarán la implementación.

#### [NEW] `base/juego.py`
- Clase abstracta `Juego` (métodos: `estado_inicial`, `jugadas_legales`, `aplicar_jugada`, `es_terminal`, `obtener_resultado`).

#### [NEW] `base/agente.py`
- Clase abstracta `Agente` con `seleccionar_movimiento()`.
- Implementación de `AgenteAleatorio`.

---

### Paquete de Juegos (Reglas)
#### [NEW] `juegos/othello.py`
- Lógica de Othello usando bitboards (enteros 64-bit python) para las fichas propias y rivales (muy eficiente).

#### [NEW] `juegos/tictactoe3d.py`
- Lógica de TTT 4x4x4 en matrices 3D, iterando hiperlíneas ganadoras para detección del final de juego.

---

### Búsqueda (Algoritmos)
#### [NEW] `algoritmos/minimax.py`
- Implementación del motor genérico de `AgenteMinimaxAlfaBeta`.

---

### Heurísticas (Fase 2)
#### [NEW] `heuristicas/othello_heuristics.py`
- Diferencia de fichas, esquinas, movilidad, paridad. Evaluador parametrizado por matriz de pesos $W$.

#### [NEW] `heuristicas/ttt3d_heuristics.py`
- Líneas abiertas con m>0 fichas, centro, etc.

---

### Optimización (Fase 3 - AG)
#### [NEW] `optimizacion/genetico.py`
- Algoritmo genético trabajando sobre un vector generacional de reales. Función fitness mide ratio de victorias vs oponente basal.
- Operadores: Torneo, BLX-Alpha / Crossover Uniforme, Mutación normal.

---

### Orquestación (Fase 4)
#### [NEW] `simulacion/torneo.py`
- Módulo para ejecutar sets de 100 partidas y recolectar KPIs.

#### [NEW] `main.py`
- Runner principal (CLI interactiva o scripts segmentados de Fase1..4).

## Open Questions
- En el Algoritmo Genético, para evaluar el fitness frente a un oponente. ¿Estás de acuerdo si probamos contra un oponente aleatorio primero para validarlo rápidamente, o prefieres enfrentar directamente contra métricas manuales para que la evolución produzca gentes potentes desde el inicio?

## Verification Plan

### Automated Tests
- Scripts de validación en `main.py` para ver si Minimax vence a Random.
- Prints de convergencia (Fitness Generacional).
- Comparativa tabular reproducible como la requerida.
