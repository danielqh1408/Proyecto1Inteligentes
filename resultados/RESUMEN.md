# Resultados de los experimentos

Generado: 2026-10-21 04:00 · commit `b92963f + cambios locales` · Python 3.11.16

Regenerar con: `python -m tacticalgrid experimentos`. Todo es determinista salvo las columnas de tiempo. tiempo_total_ms = tiempo_ms + preparacion_ms; incluye preparar la heurística, no cargar el JSON. Las evaluaciones totales incluyen hojas, ordenamiento y desglose del hijo elegido.

## Casos mínimos del enunciado (esperado vs obtenido)

### ✔ Caso 1: BFS y DFS encuentran solución pero recorren el espacio de forma diferente.

**Esperado:** Ambos con éxito; orden de expansión distinto; DFS da un camino más largo que BFS.

| algoritmo | exito | costo | longitud | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms | preparacion_ms | tiempo_total_ms |
|---|---|---|---|---|---|---|---|---|---|
| BFS | True | 55 | 29 | 344 | 340 | 22 | 0.411 | 0 | 0.411 |
| DFS | True | 312 | 137 | 350 | 206 | 152 | 0.251 | 0 | 0.251 |

### ✔ Caso 2: BFS cruza el pantano (menos pasos); UCS rodea por el camino (menos costo).

**Esperado:** BFS: menos movimientos y más costo. UCS: más movimientos y menos costo.

| algoritmo | exito | costo | longitud | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms | preparacion_ms | tiempo_total_ms |
|---|---|---|---|---|---|---|---|---|---|
| BFS | True | 83 | 17 | 299 | 279 | 23 | 0.309 | 0 | 0.309 |
| UCS | True | 33 | 33 | 272 | 242 | 35 | 0.343 | 0 | 0.343 |

### ✔ Caso 3: el objetivo (10,12) está a 10 pasos en línea recta, pero un muro en U obliga a rodear por la derecha.

**Esperado:** A* con 'obstaculos' expande muchos menos estados que con 'manhattan'; ambos óptimos (mismo costo que UCS).

| algoritmo | exito | costo | longitud | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms | preparacion_ms | tiempo_total_ms | heuristica |
|---|---|---|---|---|---|---|---|---|---|---|
| UCS | True | 32 | 32 | 371 | 366 | 20 | 0.476 | 0 | 0.476 |  |
| A_ESTRELLA | True | 32 | 32 | 314 | 282 | 32 | 0.405 | 0.015 | 0.42 | manhattan |
| A_ESTRELLA | True | 32 | 32 | 248 | 177 | 71 | 0.297 | 0.268 | 0.564 | obstaculos |

### ✔ Caso 4: A* con las dos heurísticas (y UCS como referencia) sobre el mismo escenario.

**Esperado:** Mismo costo óptimo con ambas heurísticas; 'obstaculos' expande menos o igual que 'manhattan'.

| algoritmo | exito | costo | longitud | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms | preparacion_ms | tiempo_total_ms | heuristica |
|---|---|---|---|---|---|---|---|---|---|---|
| UCS | True | 64 | 34 | 350 | 332 | 27 | 0.434 | 0 | 0.434 |  |
| A_ESTRELLA | True | 64 | 34 | 327 | 294 | 36 | 0.388 | 0.012 | 0.401 | manhattan |
| A_ESTRELLA | True | 64 | 34 | 323 | 289 | 32 | 0.387 | 0.237 | 0.624 | obstaculos |

### ✔ Caso 5: un pasillo sin salida (fila 10, columnas 3-14) apunta al objetivo. Con k=1 Beam entra y se queda sin salida.

**Esperado:** k=1 falla; con k mayores encuentra camino; los estados expandidos cambian con k.

| algoritmo | exito | costo | longitud | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms | preparacion_ms | tiempo_total_ms | k | criterio | descartados | heuristica |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BEAM | False | 0 | 0 | 19 | 14 | 4 | 0.03 | 0.012 | 0.041 | 1 | h | 5 | manhattan |
| BEAM | True | 21 | 21 | 67 | 41 | 5 | 0.059 | 0.011 | 0.07 | 2 | h | 24 | manhattan |
| BEAM | True | 21 | 21 | 126 | 81 | 8 | 0.108 | 0.011 | 0.119 | 4 | h | 41 | manhattan |
| BEAM | True | 21 | 21 | 200 | 155 | 12 | 0.193 | 0.011 | 0.205 | 8 | h | 37 | manhattan |

### ✔ Caso 6: A1 debe recoger el recurso al fondo del pasillo (1,12) y volver a su base (1,1) por las mismas celdas: cada celda del pasillo aparece dos veces en el camino, con lleva_recurso False y True.

**Esperado:** El camino de la misión repite posiciones con distinto valor de lleva_recurso.

| algoritmo | exito | costo | longitud | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms | preparacion_ms | tiempo_total_ms |
|---|---|---|---|---|---|---|---|---|---|
| UCS | True | 22 | 20 | 133 | 113 | 20 | 0.172 | 0 | 0.172 |

### ✔ Caso 7: B1 está al lado del recurso (10,10) y un pasillo lo lleva a su base (10,14). A no puede llegar primero al recurso. El agente voraz (1 jugada) mueve A2 a (8,11), directo hacia el recurso. Minimax con profundidad 4 ve que B1 lo recogerá primero y mueve A2 a (9,12), la entrada del pasillo por donde B1 debe pasar para llegar a su base (bloquear / interceptar).

**Esperado:** La acción de Minimax (profundidad 4) no es la del agente VORAZ (avanzar directo al recurso).

| algoritmo | accion | valor | nodos_generados | nodos_evaluados | nodos_podados | evaluaciones_ordenamiento | evaluaciones_desglose | evaluaciones_totales | nodos_generados_totales | profundidad_alcanzada | tiempo_ms | profundidad | orden |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALFA_BETA | A2 → (9, 12) | -113.0 | 1956 | 1492 | 3561 | 0 | 1 | 1493 | 1956 | 4 | 28.994 | 4 | natural |
| VORAZ | A2 → (8, 11) | -90.1 | 13 | 12 | 0 | 0 | 1 | 13 | 13 | 1 | 0.202 | 1 | natural |

### ✔ Caso 8: B1 lleva el recurso; juega A. Minimax y alfa-beta con la misma profundidad y orden.

**Esperado:** Misma acción y mismo valor; alfa-beta evalúa menos nodos.

| algoritmo | accion | valor | nodos_generados | nodos_evaluados | nodos_podados | evaluaciones_ordenamiento | evaluaciones_desglose | evaluaciones_totales | nodos_generados_totales | profundidad_alcanzada | tiempo_ms | profundidad | orden |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MINIMAX | A2 → (12, 6) | -47.0 | 22360 | 20478 | 0 | 0 | 1 | 20479 | 22360 | 4 | 390.19 | 4 | natural |
| ALFA_BETA | A2 → (12, 6) | -47.0 | 640 | 427 | 1911 | 0 | 1 | 428 | 640 | 4 | 9.777 | 4 | natural |

### ✔ Caso 9: mismo estado del caso 8 con distintos órdenes de generación de acciones (natural, inverso, heuristico).

**Esperado:** Misma acción y valor con cada orden; cambia la cantidad de nodos podados.

| algoritmo | accion | valor | nodos_generados | nodos_evaluados | nodos_podados | evaluaciones_ordenamiento | evaluaciones_desglose | evaluaciones_totales | nodos_generados_totales | profundidad_alcanzada | tiempo_ms | profundidad | orden |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALFA_BETA | A2 → (12, 6) | -47.0 | 640 | 427 | 1911 | 0 | 1 | 428 | 640 | 4 | 11.561 | 4 | natural |
| ALFA_BETA | A2 → (11, 7) | -47.0 | 11318 | 10234 | 1562 | 0 | 1 | 10235 | 11318 | 4 | 193.375 | 4 | inverso |
| ALFA_BETA | A2 → (12, 6) | -47.0 | 639 | 426 | 1911 | 2549 | 1 | 2976 | 3188 | 4 | 54.337 | 4 | heuristico |

### ✔ Caso 10: mismo estado del caso 8 evaluado con profundidades 1 a 5.

**Esperado:** Nodos y tiempo crecen con la profundidad; se registra si cambia la acción.

| algoritmo | accion | valor | nodos_generados | nodos_evaluados | nodos_podados | evaluaciones_ordenamiento | evaluaciones_desglose | evaluaciones_totales | nodos_generados_totales | profundidad_alcanzada | tiempo_ms | profundidad | orden |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALFA_BETA | A1 → (9, 8) | -35.0 | 13 | 12 | 0 | 0 | 1 | 13 | 13 | 1 | 1.974 | 1 | natural |
| ALFA_BETA | A2 → (11, 7) | -41.0 | 47 | 34 | 110 | 0 | 1 | 35 | 47 | 2 | 0.742 | 2 | natural |
| ALFA_BETA | A2 → (11, 7) | -38.0 | 213 | 166 | 352 | 0 | 1 | 167 | 213 | 3 | 3.732 | 3 | natural |
| ALFA_BETA | A2 → (12, 6) | -47.0 | 640 | 427 | 1911 | 0 | 1 | 428 | 640 | 4 | 10.34 | 4 | natural |
| ALFA_BETA | A2 → (12, 6) | -44.0 | 2652 | 2012 | 5013 | 0 | 1 | 2013 | 2652 | 5 | 44.185 | 5 | natural |

## E1_busqueda — E1: los 5 algoritmos (A* y Beam con las dos heurísticas) en los casos 1 a 6.

Archivo: `E1_busqueda.csv`

| caso | algoritmo | heuristica | k | exito | longitud | costo | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms | preparacion_ms | tiempo_total_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| caso01_bfs_vs_dfs | BFS |  |  | True | 29 | 55 | 344 | 340 | 22 | 0.393 | 0 | 0.393 |
| caso01_bfs_vs_dfs | DFS |  |  | True | 137 | 312 | 350 | 206 | 152 | 0.248 | 0 | 0.248 |
| caso01_bfs_vs_dfs | UCS |  |  | True | 29 | 54 | 341 | 337 | 26 | 0.46 | 0 | 0.46 |
| caso01_bfs_vs_dfs | A_ESTRELLA | manhattan |  | True | 29 | 54 | 346 | 294 | 35 | 0.751 | 0.014 | 0.764 |
| caso01_bfs_vs_dfs | A_ESTRELLA | obstaculos |  | True | 29 | 54 | 333 | 281 | 35 | 0.431 | 0.273 | 0.705 |
| caso01_bfs_vs_dfs | BEAM | manhattan | 2 | True | 29 | 55 | 109 | 57 | 5 | 0.09 | 0.014 | 0.104 |
| caso01_bfs_vs_dfs | BEAM | obstaculos | 2 | True | 29 | 55 | 106 | 57 | 5 | 0.084 | 0.251 | 0.335 |
| caso02_ruta_corta_vs_economica | BFS |  |  | True | 17 | 83 | 299 | 279 | 23 | 0.326 | 0 | 0.326 |
| caso02_ruta_corta_vs_economica | DFS |  |  | True | 25 | 97 | 208 | 166 | 99 | 0.187 | 0 | 0.187 |
| caso02_ruta_corta_vs_economica | UCS |  |  | True | 33 | 33 | 272 | 242 | 35 | 0.335 | 0 | 0.335 |
| caso02_ruta_corta_vs_economica | A_ESTRELLA | manhattan |  | True | 33 | 33 | 179 | 92 | 68 | 0.156 | 0.013 | 0.169 |
| caso02_ruta_corta_vs_economica | A_ESTRELLA | obstaculos |  | True | 33 | 33 | 179 | 92 | 68 | 0.151 | 0.275 | 0.426 |
| caso02_ruta_corta_vs_economica | BEAM | manhattan | 2 | True | 17 | 83 | 70 | 33 | 5 | 0.055 | 0.012 | 0.067 |
| caso02_ruta_corta_vs_economica | BEAM | obstaculos | 2 | True | 17 | 83 | 70 | 33 | 5 | 0.051 | 0.277 | 0.328 |
| caso03_obstaculo_heuristica | BFS |  |  | True | 32 | 32 | 371 | 366 | 20 | 0.393 | 0 | 0.393 |
| caso03_obstaculo_heuristica | DFS |  |  | True | 76 | 76 | 375 | 299 | 144 | 0.324 | 0 | 0.324 |
| caso03_obstaculo_heuristica | UCS |  |  | True | 32 | 32 | 371 | 366 | 20 | 0.479 | 0 | 0.479 |
| caso03_obstaculo_heuristica | A_ESTRELLA | manhattan |  | True | 32 | 32 | 314 | 282 | 32 | 0.401 | 0.012 | 0.413 |
| caso03_obstaculo_heuristica | A_ESTRELLA | obstaculos |  | True | 32 | 32 | 248 | 177 | 71 | 0.254 | 0.25 | 0.504 |
| caso03_obstaculo_heuristica | BEAM | manhattan | 2 | True | 34 | 34 | 118 | 67 | 5 | 0.099 | 0.011 | 0.11 |
| caso03_obstaculo_heuristica | BEAM | obstaculos | 2 | True | 32 | 32 | 120 | 63 | 6 | 0.092 | 0.252 | 0.344 |
| caso04_comparacion_heuristicas | BFS |  |  | True | 32 | 112 | 354 | 350 | 23 | 0.381 | 0 | 0.381 |
| caso04_comparacion_heuristicas | DFS |  |  | True | 106 | 372 | 307 | 186 | 145 | 0.208 | 0 | 0.208 |
| caso04_comparacion_heuristicas | UCS |  |  | True | 34 | 64 | 350 | 332 | 27 | 0.443 | 0 | 0.443 |
| caso04_comparacion_heuristicas | A_ESTRELLA | manhattan |  | True | 34 | 64 | 327 | 294 | 36 | 0.424 | 0.012 | 0.436 |
| caso04_comparacion_heuristicas | A_ESTRELLA | obstaculos |  | True | 34 | 64 | 323 | 289 | 32 | 0.575 | 0.255 | 0.83 |
| caso04_comparacion_heuristicas | BEAM | manhattan | 2 | True | 34 | 81 | 107 | 63 | 5 | 0.166 | 0.015 | 0.181 |
| caso04_comparacion_heuristicas | BEAM | obstaculos | 2 | True | 32 | 112 | 115 | 63 | 5 | 0.095 | 0.258 | 0.353 |
| caso05_beam | BFS |  |  | True | 21 | 21 | 329 | 312 | 21 | 0.346 | 0 | 0.346 |
| caso05_beam | DFS |  |  | True | 25 | 25 | 195 | 166 | 86 | 0.18 | 0 | 0.18 |
| caso05_beam | UCS |  |  | True | 21 | 21 | 329 | 312 | 21 | 0.411 | 0 | 0.411 |
| caso05_beam | A_ESTRELLA | manhattan |  | True | 21 | 21 | 108 | 65 | 43 | 0.106 | 0.011 | 0.117 |
| caso05_beam | A_ESTRELLA | obstaculos |  | True | 21 | 21 | 97 | 50 | 47 | 0.089 | 0.267 | 0.356 |
| caso05_beam | BEAM | manhattan | 2 | True | 21 | 21 | 67 | 41 | 5 | 0.072 | 0.011 | 0.083 |
| caso05_beam | BEAM | obstaculos | 2 | True | 21 | 21 | 71 | 41 | 6 | 0.065 | 0.255 | 0.321 |
| caso06_estado_compuesto | BFS |  |  | True | 20 | 22 | 307 | 285 | 25 | 0.354 | 0 | 0.354 |
| caso06_estado_compuesto | DFS |  |  | True | 20 | 22 | 392 | 387 | 164 | 0.458 | 0 | 0.458 |
| caso06_estado_compuesto | UCS |  |  | True | 20 | 22 | 133 | 113 | 20 | 0.172 | 0 | 0.172 |
| caso06_estado_compuesto | A_ESTRELLA | manhattan |  | True | 20 | 22 | 26 | 20 | 6 | 0.034 | 0.023 | 0.057 |
| caso06_estado_compuesto | A_ESTRELLA | obstaculos |  | True | 20 | 22 | 26 | 20 | 6 | 0.031 | 0.52 | 0.551 |
| caso06_estado_compuesto | BEAM | manhattan | 2 | True | 20 | 22 | 70 | 39 | 5 | 0.067 | 0.021 | 0.088 |
| caso06_estado_compuesto | BEAM | obstaculos | 2 | True | 20 | 22 | 79 | 39 | 4 | 0.068 | 0.509 | 0.578 |

## E2_beam — E2: Beam Search con k = 1, 2, 4, 8, 16 y criterio h o f (casos 3 y 5).

Archivo: `E2_beam.csv`

| caso | k | criterio | descartados | exito | longitud | costo | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms | preparacion_ms | tiempo_total_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| caso03_obstaculo_heuristica | 1 | h | 49 | True | 36 | 36 | 86 | 36 | 4 | 0.082 | 0.013 | 0.094 |
| caso03_obstaculo_heuristica | 2 | h | 49 | True | 34 | 34 | 118 | 67 | 5 | 0.096 | 0.014 | 0.111 |
| caso03_obstaculo_heuristica | 4 | h | 55 | True | 32 | 32 | 184 | 125 | 8 | 0.17 | 0.011 | 0.181 |
| caso03_obstaculo_heuristica | 8 | h | 52 | True | 32 | 32 | 305 | 245 | 13 | 0.315 | 0.011 | 0.326 |
| caso03_obstaculo_heuristica | 16 | h | 9 | True | 32 | 32 | 371 | 357 | 20 | 0.447 | 0.011 | 0.458 |
| caso03_obstaculo_heuristica | 1 | f | 49 | True | 36 | 36 | 86 | 36 | 4 | 0.062 | 0.011 | 0.073 |
| caso03_obstaculo_heuristica | 2 | f | 49 | True | 34 | 34 | 118 | 67 | 5 | 0.096 | 0.011 | 0.107 |
| caso03_obstaculo_heuristica | 4 | f | 55 | True | 32 | 32 | 184 | 125 | 8 | 0.168 | 0.011 | 0.179 |
| caso03_obstaculo_heuristica | 8 | f | 52 | True | 32 | 32 | 305 | 245 | 13 | 0.318 | 0.011 | 0.329 |
| caso03_obstaculo_heuristica | 16 | f | 9 | True | 32 | 32 | 371 | 357 | 20 | 0.542 | 0.011 | 0.553 |
| caso05_beam | 1 | h | 5 | False | 0 | 0 | 19 | 14 | 4 | 0.027 | 0.012 | 0.039 |
| caso05_beam | 2 | h | 24 | True | 21 | 21 | 67 | 41 | 5 | 0.059 | 0.011 | 0.071 |
| caso05_beam | 4 | h | 41 | True | 21 | 21 | 126 | 81 | 8 | 0.236 | 0.011 | 0.246 |
| caso05_beam | 8 | h | 37 | True | 21 | 21 | 200 | 155 | 12 | 0.218 | 0.011 | 0.23 |
| caso05_beam | 16 | h | 20 | True | 21 | 21 | 311 | 275 | 20 | 0.344 | 0.011 | 0.355 |
| caso05_beam | 1 | f | 5 | False | 0 | 0 | 19 | 14 | 4 | 0.021 | 0.011 | 0.031 |
| caso05_beam | 2 | f | 24 | True | 21 | 21 | 67 | 41 | 5 | 0.059 | 0.011 | 0.069 |
| caso05_beam | 4 | f | 41 | True | 21 | 21 | 126 | 81 | 8 | 0.11 | 0.011 | 0.121 |
| caso05_beam | 8 | f | 37 | True | 21 | 21 | 200 | 155 | 12 | 0.197 | 0.011 | 0.208 |
| caso05_beam | 16 | f | 20 | True | 21 | 21 | 311 | 275 | 20 | 0.346 | 0.01 | 0.356 |

## E3_sensibilidad — E3: costo del pantano de 1 a 20 en el caso 2 (el ejemplo del profesor: 7 -> 15).

Archivo: `E3_sensibilidad.csv`

| costo_pantano | algoritmo | exito | longitud | costo | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms | preparacion_ms | tiempo_total_ms |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | BFS | True | 17 | 23 | 299 | 279 | 23 | 0.317 | 0 | 0.317 |
| 1 | UCS | True | 17 | 23 | 334 | 311 | 30 | 0.431 | 0 | 0.431 |
| 1 | A_ESTRELLA | True | 17 | 23 | 104 | 55 | 45 | 0.094 | 0.286 | 0.379 |
| 2 | BFS | True | 17 | 33 | 299 | 279 | 23 | 0.312 | 0 | 0.312 |
| 2 | UCS | True | 17 | 33 | 345 | 334 | 26 | 0.455 | 0 | 0.455 |
| 2 | A_ESTRELLA | True | 17 | 33 | 298 | 156 | 93 | 0.313 | 0.277 | 0.59 |
| 3 | BFS | True | 17 | 43 | 299 | 279 | 23 | 0.376 | 0 | 0.376 |
| 3 | UCS | True | 33 | 33 | 319 | 300 | 28 | 0.428 | 0 | 0.428 |
| 3 | A_ESTRELLA | True | 33 | 33 | 219 | 116 | 76 | 0.192 | 0.277 | 0.469 |
| 5 | BFS | True | 17 | 63 | 299 | 279 | 23 | 0.299 | 0 | 0.299 |
| 5 | UCS | True | 33 | 33 | 289 | 263 | 32 | 0.362 | 0 | 0.362 |
| 5 | A_ESTRELLA | True | 33 | 33 | 185 | 98 | 68 | 0.314 | 0.523 | 0.838 |
| 7 | BFS | True | 17 | 83 | 299 | 279 | 23 | 0.417 | 0 | 0.417 |
| 7 | UCS | True | 33 | 33 | 272 | 242 | 35 | 0.375 | 0 | 0.375 |
| 7 | A_ESTRELLA | True | 33 | 33 | 179 | 92 | 68 | 0.155 | 0.282 | 0.437 |
| 10 | BFS | True | 17 | 113 | 299 | 279 | 23 | 0.306 | 0 | 0.306 |
| 10 | UCS | True | 33 | 33 | 257 | 222 | 38 | 0.306 | 0 | 0.306 |
| 10 | A_ESTRELLA | True | 33 | 33 | 176 | 89 | 68 | 0.149 | 0.276 | 0.424 |
| 15 | BFS | True | 17 | 163 | 299 | 279 | 23 | 0.303 | 0 | 0.303 |
| 15 | UCS | True | 33 | 33 | 246 | 209 | 40 | 0.29 | 0 | 0.29 |
| 15 | A_ESTRELLA | True | 33 | 33 | 172 | 85 | 68 | 0.142 | 0.274 | 0.416 |
| 20 | BFS | True | 17 | 213 | 299 | 279 | 23 | 0.305 | 0 | 0.305 |
| 20 | UCS | True | 33 | 33 | 239 | 201 | 41 | 0.276 | 0 | 0.276 |
| 20 | A_ESTRELLA | True | 33 | 33 | 172 | 85 | 68 | 0.14 | 0.275 | 0.415 |

## E4_profundidad — E4: Minimax vs alfa-beta con profundidad 1 a 5 en el estado del caso 8 (Minimax hasta 4).

Archivo: `E4_profundidad.csv`

| profundidad | algoritmo | accion | valor | nodos_generados | nodos_evaluados | nodos_podados | evaluaciones_ordenamiento | evaluaciones_desglose | evaluaciones_totales | nodos_generados_totales | profundidad_alcanzada | tiempo_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | MINIMAX | A1 → (9, 8) | -35.0 | 13 | 12 | 0 | 0 | 1 | 13 | 13 | 1 | 1.945 |
| 1 | ALFA_BETA | A1 → (9, 8) | -35.0 | 13 | 12 | 0 | 0 | 1 | 13 | 13 | 1 | 0.238 |
| 2 | MINIMAX | A2 → (11, 7) | -41.0 | 157 | 144 | 0 | 0 | 1 | 145 | 157 | 2 | 3.176 |
| 2 | ALFA_BETA | A2 → (11, 7) | -41.0 | 47 | 34 | 110 | 0 | 1 | 35 | 47 | 2 | 0.76 |
| 3 | MINIMAX | A2 → (11, 7) | -38.0 | 1882 | 1725 | 0 | 0 | 1 | 1726 | 1882 | 3 | 34.351 |
| 3 | ALFA_BETA | A2 → (11, 7) | -38.0 | 213 | 166 | 352 | 0 | 1 | 167 | 213 | 3 | 3.504 |
| 4 | MINIMAX | A2 → (12, 6) | -47.0 | 22360 | 20478 | 0 | 0 | 1 | 20479 | 22360 | 4 | 413.122 |
| 4 | ALFA_BETA | A2 → (12, 6) | -47.0 | 640 | 427 | 1911 | 0 | 1 | 428 | 640 | 4 | 13.337 |
| 5 | ALFA_BETA | A2 → (12, 6) | -44.0 | 2652 | 2012 | 5013 | 0 | 1 | 2013 | 2652 | 5 | 57.06 |

## E5_orden — E5: efecto del orden de generación de acciones en la poda (caso 9).

Archivo: `E5_orden.csv`

| profundidad | orden | accion | valor | nodos_generados | nodos_evaluados | nodos_podados | evaluaciones_ordenamiento | evaluaciones_desglose | evaluaciones_totales | nodos_generados_totales | profundidad_alcanzada | tiempo_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | natural | A2 → (11, 7) | -41.0 | 47 | 34 | 110 | 0 | 1 | 35 | 47 | 2 | 2.738 |
| 2 | inverso | A2 → (11, 7) | -41.0 | 131 | 118 | 26 | 0 | 1 | 119 | 131 | 2 | 2.293 |
| 2 | heuristico | A2 → (11, 7) | -41.0 | 47 | 34 | 110 | 156 | 1 | 191 | 203 | 2 | 3.782 |
| 3 | natural | A2 → (11, 7) | -38.0 | 213 | 166 | 352 | 0 | 1 | 167 | 213 | 3 | 4.344 |
| 3 | inverso | A2 → (11, 7) | -38.0 | 1144 | 1013 | 426 | 0 | 1 | 1014 | 1144 | 3 | 21.665 |
| 3 | heuristico | A2 → (11, 7) | -38.0 | 213 | 166 | 352 | 564 | 1 | 731 | 777 | 3 | 19.495 |
| 4 | natural | A2 → (12, 6) | -47.0 | 640 | 427 | 1911 | 0 | 1 | 428 | 640 | 4 | 13.983 |
| 4 | inverso | A2 → (11, 7) | -47.0 | 11318 | 10234 | 1562 | 0 | 1 | 10235 | 11318 | 4 | 295.136 |
| 4 | heuristico | A2 → (12, 6) | -47.0 | 639 | 426 | 1911 | 2549 | 1 | 2976 | 3188 | 4 | 114.485 |

## E6_torneo — E6: partidas completas en un mapa simétrico entre agentes con distinta profundidad.

Archivo: `E6_torneo.csv`

| agente_A | agente_B | resultado | jugadas | intercepciones |
|---|---|---|---|---|
| VORAZ(1) | VORAZ(1) | Gana el bando B en 74 turnos | 74 | 1 |
| ALFA_BETA(3) | VORAZ(1) | Gana el bando A en 75 turnos | 75 | 1 |
| VORAZ(1) | ALFA_BETA(3) | Gana el bando B en 74 turnos | 74 | 1 |
| ALFA_BETA(1) | ALFA_BETA(3) | Gana el bando B en 74 turnos | 74 | 1 |
| ALFA_BETA(3) | ALFA_BETA(1) | Gana el bando A en 75 turnos | 75 | 1 |
| ALFA_BETA(3) | ALFA_BETA(3) | Empate (límite de turnos) | 200 | 0 |
