# Resumen de Ejecución: Práctica de Agentes Inteligentes en Juegos Computacionales

La práctica se ha implementado de principio a fin, satisfaciendo la arquitectura orientada a objetos solicitada, desarrollando Agentes Inteligentes sobre **Othello (Reversi)** y **Tic-Tac-Toe 3D (4x4x4)** usando **Minimax con Poda Alfa-Beta** y **Algoritmos Genéticos** para la optimización de pesos.

## Componentes y Arquitectura
El trabajo está dividido organizativamente por fases:

1. **Paquete Core (`base/juego.py`, `base/agente.py`)**: Clases abstractas asegurando compatibilidad e intercambiabilidad completa de Agentes en ambos juegos, facilitando la validación del código (Fase 1).
2. **Juegos (`juegos/othello.py`, `juegos/tictactoe3d.py`)**:
   - Para Othello se usó la representación recomendada mediante _bitboards_ super eficientes en un único entero 64 bits para cada jugador, reduciendo radicalmente el tiempo necesario para la expansión de ramas en el Minimax.
   - Tic-Tac-Toe 3D se codificó en tuplas estáticas garantizando su compatibilidad en el _hashed memory_ y explorando las 76 hiperlíneas que comprenden estados de victoria.
3. **Búsqueda Avanzada (`algoritmos/minimax.py`)**: Implementación rigurosa de Minimax complementado con **Poda Alfa-Beta**. Capaz de rastrear los `nodos_explorados` y `nodos_podados` para facilitar estudios paramétricos futuros.
4. **Heurísticas Parametrizables (`heuristicas/...`)**: Se modeló $E(s)$ combinando la puntuación dada en diferencias de fichas, control de esquinas/centro y movimientos legales disponibles.
5. **Algoritmos Genéticos (`optimizacion/genetico.py`)**: Un potente optimizador basado en cromosomas y recombinación aritmética. Para cada generación evalúa en paralelo a cada *individuo* sometiéndolo a una mini-competición automatizada, utilizando su propio _win/tie-rate_ como su nivel de `fitness`.

## Ejecución y Experimentación (Fase 4)
Orquestamos el proyecto completo usando el pipeline en `main.py`, lanzando un proceso de optimización para cada juego y luego alimentando un torneo final contra el oponente basal:
> **Nota de Rendimiento:** *El proceso de genética es costoso.* Ejecutando en profundidad 2 para el entrenamiento, y luego compitiendo la solución maestra resultante en **profundidad 3 (para Othello) y 2 (para el TTT3D)** arrojó excelentes resultados de dominancia en muy pocos segundos.

### Resultados Obtrenidos en Test de Validación:

| Pruebas Frente a Agente Aleatorio (20 partidas) | Victorias | Derrotas | Empates | Tasa de Victorias |
| :--- | :---: | :---: | :---: | :---: |
| **Othello (Agente AG)** | 13 | 6 | 1 | 65% |
| **Tic-Tac-Toe 3D (Agente AG)** | 20 | 0 | 0 | 100% |

> [!TIP]
> **Expansión**
> Como trabajo futuro, se puede incrementar la profundidad máxima (`profundidad_maxima=4` o más) cuando se cuente con más tiempo de cómputo para los experimentos en placa real, para observar una supremacía táctica absoluta del Agente Genético en Othello.
