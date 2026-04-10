# 🤖 Práctica IA1 — Agentes Inteligentes con Búsquedas

Implementación de agentes inteligentes para juegos de adversario utilizando el algoritmo **Minimax con Poda Alfa-Beta**.  
Incluye dos juegos clásicos: **Othello** y **TicTacToe 3D (4×4×4)**, con interfaz gráfica interactiva y optimización de heurísticas mediante **Algoritmos Genéticos**.

---

## 🎮 Juegos Implementados

### ⚫ Othello (8×8)
- Representación del tablero con **bitboards** de 64 bits para máxima eficiencia
- Cálculo de volteos en las 8 direcciones
- Detección automática de paso de turno

### 🎯 TicTacToe 3D (4×4×4)
- Tablero cúbico con **64 celdas** (4 capas × 4×4)
- **76 líneas ganadoras** (ortogonales, diagonales 2D y diagonales 3D)
- Victoria al formar una línea de 4 en cualquier dirección

---

## 🧠 Algoritmos

### Minimax con Poda Alfa-Beta (`algoritmos/minimax.py`)
- Exploración en profundidad configurable
- Poda alfa-beta para reducir el espacio de búsqueda
- Estadísticas de nodos explorados y podas realizadas

### Heurísticas (`heuristicas/`)

| Juego | Características evaluadas |
|---|---|
| **Othello** | Diferencia de fichas, movilidad, control de esquinas, paridad |
| **TTT 3D** | Líneas abiertas (1, 2, 3 fichas), control del centro 2×2×2 |

### Optimización Genética (`optimizacion/genetico.py`)
- Evolución de los pesos de las funciones heurísticas
- Evaluación de fitness mediante torneos simulados

---

## 🖥️ Interfaz Gráfica (`interfaz.py`)

Interfaz premium con **Tkinter** en modo oscuro.

**Características:**
- 🎨 Diseño moderno con modo oscuro y colores armoniosos
- ♟️ Tablero interactivo con hover y resaltado de movimientos válidos
- ⚙️ Configuración en tiempo real (profundidad IA, lado del jugador)
- 📊 Estadísticas en vivo (nodos explorados, podas)
- 🤖 IA en hilo separado (la UI no se congela)
- ▶️ Botón para forzar turno de la IA

### Ejecutar la interfaz

```bash
python interfaz.py
```

---

## 📁 Estructura del Proyecto

```
Practica_ia1_busquedas/
│
├── interfaz.py               # Interfaz gráfica principal
├── main.py                   # Script de entrenamiento y experimentos
│
├── base/
│   ├── juego.py              # Clase abstracta Juego
│   └── agente.py             # Clase abstracta Agente + AgenteAleatorio
│
├── juegos/
│   ├── othello.py            # Implementación de Othello
│   └── tictactoe3d.py        # Implementación de TicTacToe 3D
│
├── algoritmos/
│   └── minimax.py            # Agente Minimax con Poda Alfa-Beta
│
├── heuristicas/
│   ├── othello_heuristics.py # Función de evaluación para Othello
│   └── ttt3d_heuristics.py   # Función de evaluación para TTT3D
│
├── optimizacion/
│   └── genetico.py           # Algoritmo Genético para optimizar pesos
│
└── simulacion/
    └── torneo.py             # Simulación de torneos entre agentes
```

---

## ▶️ Ejecución

### Requisitos
- Python 3.8+
- Tkinter (incluido en la instalación estándar de Python)

### Interfaz gráfica (recomendado)
```bash
python interfaz.py
```

### Entrenamiento con Algoritmo Genético + Experimentos
```bash
python main.py
```

---

## 📐 Arquitectura

```
Juego (ABC)
  ├── JuegoOthello
  └── JuegoTicTacToe3D

Agente (ABC)
  ├── AgenteAleatorio
  └── AgenteMinimaxAlfaBeta
        ├── evaluador: get_evaluador_othello(pesos)
        └── evaluador: get_evaluador_ttt3d(pesos)
```

---

## 👩‍💻 Autora

**LIBIA71421** — Práctica de Inteligencia Artificial 1  
Universidad — Sistemas Inteligentes
