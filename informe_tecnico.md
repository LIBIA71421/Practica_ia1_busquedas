# 📄 Informe Técnico: Agentes Inteligentes y Búsquedas Adversariales

## 1. Introducción y Objetivos

Este documento técnico detalla la arquitectura, el funcionamiento algorítmico y el diseño visual del proyecto **Agentes Inteligentes con Búsquedas**. El propósito principal del software es proporcionar un entorno de evaluación y juego interactivo para dos problemas de naturaleza zero-sum (suma cero) y adversariales: **Othello (8x8)** y **Tic-Tac-Toe Cúbico (4x4x4)**. 

Se emplean aproximaciones clásicas de la Inteligencia Artificial (IA) estructurada, específicamente el algoritmo **Minimax con Poda Alfa-Beta**, suplementado con funciones heurísticas especializadas y calibradas mediante **Algoritmos Genéticos**.

---

## 2. Minimax con Poda Alfa-Beta

El núcleo del motor de IA para ambos juegos es el algoritmo adversarial **Minimax**.

### 2.1. Naturaleza del Algoritmo
El algoritmo Minimax asume un juego de dos participantes donde los intereses son estrictamente opuestos: el jugador *Maximizer* (busca maximizar la utilidad del estado) y el jugador *Minimizer* (busca minimizarla).
Dado que el espacio de estados tanto de Othello como de Tic-Tac-Toe 3D excede la memoria y tiempo de computación práctico, se establece un **límite de profundidad**. Cuando el árbol de exploración alcanza este límite, el estado se evalúa con una **función heurística estática**.

### 2.2. Optimización Alfa-Beta
Para incrementar la profundidad que la IA puede calcular en el mismo tiempo, se implementó la **Poda Alfa-Beta**.
- **$\alpha$ (Alfa):** Es el mejor valor (el más alto) que el *Maximizer* puede garantizar en el camino actual o superior.
- **$\beta$ (Beta):** Es el mejor valor (el más bajo) que el *Minimizer* puede garantizar en el camino actual o superior.
Si durante la exploración se detecta que un camino dará peores resultados de los que el oponente ya puede forzar o garantizar previamente ($\alpha \ge \beta$), la rama completa se **poda**, evitando calcular miles de nodos que matemáticamente nunca ocurrirán en el escenario óptimo.

**Impacto del rendimiento:** Othello y TTT3D lograron calcular profundidades completas de 5 y 3 plies respectivamente entre 1 a 3 segundos gracias a la poda, reduciendo la explosión combinatoria significativamente.

---

## 3. Implementación Subyacente de Othello (8x8)

### 3.1. Arquitectura de Datos (Bitboards)
La gran innovación en el módulo de Othello es el uso extensivo de **Bitboards**.
En lugar de representar el tablero con una matriz dinámica en memoria o listas dobles, Othello asume que el tablero mide 64 celdas. Esto encaja de manera perfecta en un **entero de 64 bits** del procesador.
- Las fichas del Jugador 1 se guardan en el entero $B$.
- Las fichas del Jugador 2 se guardan en el entero $W$.
Las operaciones de validación (saber qué celdas son legales en una dirección geométrica) se transforman en **desplazamientos de bits (Bitshifts `<<` y `>>`)** combinados con operaciones lógicas `AND/OR` ultrarrápidas, llevando el cálculo de "piezas volteadas" a tiempo casi $O(1)$.

### 3.2. Función Heurística
Para Othello, la IA no se rige solo por la cantidad de fichas ganadas (lo cual es perjudicial en mediano juego). Se evalúan cuatro ejes ponderados:
1. **Diferencia de Discos:** Cantidad actual ponderada con un valor bajo durante el mid-game.
2. **Movilidad:** Número de jugadas legales disponibles para nosotros en comparación contra el enemigo. Restringir penaliza fuertemente al rival.
3. **Control de Esquinas:** Las esquinas jamás pueden ser flanqueadas una vez aseguradas. Factor vital y de alto impacto.
4. **Estabilidad y Bordes:** Evaluar las posiciones estables que limitan opciones ajenas sin comprometer el dominio futuro de tableros adyacentes.

---

## 4. Implementación Subyacente de Tic-Tac-Toe 3D (4x4x4)

### 4.1. Complejidad del Entorno
Mientras que el Tic-Tac-Toe tradicional de 3x3x1 tiene 8 rutas posibles de ganar, el modelo extendido tridimensional de $4 \times 4 \times 4$ proporciona **76 líneas de impacto posible**:
- 16 columnas en el eje vertical Z.
- 16 filas en el eje X para cada nivel.
- 16 columnas en el eje Y para cada nivel.
- 24 diagonales cruzadas 2D que viajan dentro de capas planas y paredes de profundidad.
- 4 diagonales mayores tridimensionales que recorren los extremos opuestos del cubo interior.

### 4.2. Renderizado Isométrico e Interacción Cúbica (Gráficos)
Para mitigar la natural incomprensión de las jugadas en mallas espaciales, la nueva UI proporciona una **proyección tridimensional analítica** generada matemáticamente al vuelo nativa en su frame:
- **Proyección Computarizada:** Transforma espacios matemáticos ortonormales en proyecciones angulares (Pitch y Yaw rotativo vía Cursor Drag) manejando los senos y cosenos cartesianos que renderizan el campo perspectivo.
- **Iluminación e Índice Z:** Los cristales, mallas y piezas se componen y ordenan de más distante a más cercano *(Z-Sorting Algorithm)* logrando transparencia semiótica profunda durante jugadas.

### 4.3. Función Heurística (Amenazas)
Con cientos de variaciones abiertas en su volumen, las métricas son de contención de fuego:
1. **Celdas Centrales:** El core interior $2 \times 2 \times 2$ dictamina el máximo cruce de vectores, ganar estas celdas pondera altamente.
2. **Threat Mapping (Mapeo de Amenazas):** La evaluación detecta escaneos de peligro. Busca secuencias interrumpidas de *1 alineación*, *2 componentes* y crucialmente *3 componentes libres*, aplicando castigos algorítmicos dramáticos ante líneas críticas de victoria inminente expuestas.

---

## 5. El Algoritmo Genético de Optimización Automática

Para que el modelo decida de forma empírica si *poseer una esquina pesa un 89% y la movilidad un 11%*, se diseñó en el proyecto un esquema de calibración de **Algoritmo Genético** automatizado.

1. **Población Inicial Dinámica:** Un conjunto distribuido de N agentes heurísticos iniciales aleatorios.
2. **Torneo de Fitness:** Se compilan en "Arenas" de ejecución multihilo, compitiendo unos contra otros.
3. **Cruce (Crossover) y Mutación Estocástica:** Los genomas ganadores distribuyen el ADN (valores de peso decimales en un vector de tupla) y se les inyecta un porcentaje de mutación en ruido Gaussiano, evitando converger con el mínimo local.
4. **Dominancia Final Alcanzada:** Aquellos valores predeterminados cargados en el código de Othello / TTT3D corresponden al individuo final que logró la máxima robustez combativa post cientos de generaciones exhaustivas.

---
**Proyecto "Practica de Inteligencia Artificial 1 - Busquedas y Algoritmos Adversariales"**
