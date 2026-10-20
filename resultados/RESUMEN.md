# Resultados de los experimentos

Generado: 2026-10-20 16:46 · commit `32ce138` · Python 3.12.14

Regenerar con: `python -m tacticalgrid experimentos`. Todo es determinista salvo `tiempo_ms`.

## Casos mínimos del enunciado (esperado vs obtenido)

### ✔ Caso 1: BFS y DFS encuentran solución pero recorren el espacio de forma diferente.

**Esperado:** Ambos con éxito; orden de expansión distinto; DFS da un camino más largo que BFS.

| algoritmo | exito | costo | longitud | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms |
|---|---|---|---|---|---|---|---|
| BFS | True | 55 | 29 | 344 | 340 | 22 | 0.473 |
| DFS | True | 312 | 137 | 350 | 206 | 152 | 0.259 |

### ✔ Caso 2: BFS cruza el pantano (menos pasos); UCS rodea por el camino (menos costo).

**Esperado:** BFS: menos movimientos y más costo. UCS: más movimientos y menos costo.

| algoritmo | exito | costo | longitud | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms |
|---|---|---|---|---|---|---|---|
| BFS | True | 83 | 17 | 299 | 279 | 23 | 0.282 |
| UCS | True | 33 | 33 | 272 | 242 | 35 | 0.306 |

### ✔ Caso 3: el objetivo (10,12) está a 10 pasos en línea recta, pero un muro en U obliga a rodear por la derecha.

**Esperado:** A* con 'obstaculos' expande muchos menos estados que con 'manhattan'; ambos óptimos (mismo costo que UCS).

| algoritmo | exito | costo | longitud | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms | heuristica |
|---|---|---|---|---|---|---|---|---|
| UCS | True | 32 | 32 | 371 | 366 | 20 | 0.424 |  |
| A_ESTRELLA | True | 32 | 32 | 314 | 282 | 32 | 0.35 | manhattan |
| A_ESTRELLA | True | 32 | 32 | 248 | 177 | 71 | 0.266 | obstaculos |

### ✔ Caso 4: A* con las dos heurísticas (y UCS como referencia) sobre el mismo escenario.

**Esperado:** Mismo costo óptimo con ambas heurísticas; 'obstaculos' expande menos o igual que 'manhattan'.

| algoritmo | exito | costo | longitud | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms | heuristica |
|---|---|---|---|---|---|---|---|---|
| UCS | True | 64 | 34 | 350 | 332 | 27 | 0.388 |  |
| A_ESTRELLA | True | 64 | 34 | 327 | 294 | 36 | 0.37 | manhattan |
| A_ESTRELLA | True | 64 | 34 | 323 | 289 | 32 | 0.384 | obstaculos |

### ✔ Caso 5: un pasillo sin salida (fila 10, columnas 3-14) apunta al objetivo. Con k=1 Beam entra y se queda sin salida.

**Esperado:** k=1 falla; con k mayores encuentra camino; los estados expandidos cambian con k.

| algoritmo | exito | costo | longitud | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms | k | criterio | descartados | heuristica |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BEAM | False | 0 | 0 | 19 | 14 | 4 | 0.026 | 1 | h | 5 | manhattan |
| BEAM | True | 21 | 21 | 67 | 41 | 5 | 0.052 | 2 | h | 24 | manhattan |
| BEAM | True | 21 | 21 | 126 | 81 | 8 | 0.093 | 4 | h | 41 | manhattan |
| BEAM | True | 21 | 21 | 200 | 155 | 12 | 0.164 | 8 | h | 37 | manhattan |

### ✔ Caso 6: A1 debe recoger el recurso al fondo del pasillo (1,12) y volver a su base (1,1) por las mismas celdas: cada celda del pasillo aparece dos veces en el camino, con lleva_recurso False y True.

**Esperado:** El camino de la misión repite posiciones con distinto valor de lleva_recurso.

| algoritmo | exito | costo | longitud | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms |
|---|---|---|---|---|---|---|---|
| UCS | True | 22 | 20 | 133 | 113 | 20 | 0.153 |

### ✔ Caso 7: B1 está al lado del recurso (10,10) y un pasillo lo lleva a su base (10,14). A no puede llegar primero al recurso. El agente voraz (1 jugada) mueve A2 a (8,11), directo hacia el recurso. Minimax con profundidad 4 ve que B1 lo recogerá primero y mueve A2 a (9,12), la entrada del pasillo por donde B1 debe pasar para llegar a su base (bloquear / interceptar).

**Esperado:** La acción de Minimax (profundidad 4) no es la del agente VORAZ (avanzar directo al recurso).

| algoritmo | accion | valor | nodos_generados | nodos_evaluados | nodos_podados | profundidad_alcanzada | tiempo_ms | profundidad | orden |
|---|---|---|---|---|---|---|---|---|---|
| ALFA_BETA | A2 → (9, 12) | -113.0 | 1956 | 1492 | 3561 | 4 | 28.888 | 4 | natural |
| VORAZ | A2 → (8, 11) | -90.1 | 13 | 12 | 0 | 1 | 0.218 | 1 | natural |

### ✔ Caso 8: B1 lleva el recurso; juega A. Minimax y alfa-beta con la misma profundidad y orden.

**Esperado:** Misma acción y mismo valor; alfa-beta evalúa menos nodos.

| algoritmo | accion | valor | nodos_generados | nodos_evaluados | nodos_podados | profundidad_alcanzada | tiempo_ms | profundidad | orden |
|---|---|---|---|---|---|---|---|---|---|
| MINIMAX | A2 → (12, 6) | -47.0 | 22360 | 20478 | 0 | 4 | 382.621 | 4 | natural |
| ALFA_BETA | A2 → (12, 6) | -47.0 | 640 | 427 | 1911 | 4 | 9.454 | 4 | natural |

### ✔ Caso 9: mismo estado del caso 8 con distintos órdenes de generación de acciones (natural, inverso, heuristico).

**Esperado:** Misma acción y valor con cada orden; cambia la cantidad de nodos podados.

| algoritmo | accion | valor | nodos_generados | nodos_evaluados | nodos_podados | profundidad_alcanzada | tiempo_ms | profundidad | orden |
|---|---|---|---|---|---|---|---|---|---|
| ALFA_BETA | A2 → (12, 6) | -47.0 | 640 | 427 | 1911 | 4 | 11.386 | 4 | natural |
| ALFA_BETA | A2 → (11, 7) | -47.0 | 11318 | 10234 | 1562 | 4 | 197.545 | 4 | inverso |
| ALFA_BETA | A2 → (12, 6) | -47.0 | 639 | 426 | 1911 | 4 | 55.373 | 4 | heuristico |

### ✔ Caso 10: mismo estado del caso 8 evaluado con profundidades 1 a 5.

**Esperado:** Nodos y tiempo crecen con la profundidad; se registra si cambia la acción.

| algoritmo | accion | valor | nodos_generados | nodos_evaluados | nodos_podados | profundidad_alcanzada | tiempo_ms | profundidad | orden |
|---|---|---|---|---|---|---|---|---|---|
| ALFA_BETA | A1 → (9, 8) | -35.0 | 13 | 12 | 0 | 1 | 1.909 | 1 | natural |
| ALFA_BETA | A2 → (11, 7) | -41.0 | 47 | 34 | 110 | 2 | 0.758 | 2 | natural |
| ALFA_BETA | A2 → (11, 7) | -38.0 | 213 | 166 | 352 | 3 | 3.437 | 3 | natural |
| ALFA_BETA | A2 → (12, 6) | -47.0 | 640 | 427 | 1911 | 4 | 9.64 | 4 | natural |
| ALFA_BETA | A2 → (12, 6) | -44.0 | 2652 | 2012 | 5013 | 5 | 43.218 | 5 | natural |

## E1_busqueda — E1: los 5 algoritmos (A* y Beam con las dos heurísticas) en los casos 1 a 6.

Archivo: `E1_busqueda.csv`

| caso | algoritmo | heuristica | k | exito | longitud | costo | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms |
|---|---|---|---|---|---|---|---|---|---|---|
| caso01_bfs_vs_dfs | BFS |  |  | True | 29 | 55 | 344 | 340 | 22 | 0.382 |
| caso01_bfs_vs_dfs | DFS |  |  | True | 137 | 312 | 350 | 206 | 152 | 0.219 |
| caso01_bfs_vs_dfs | UCS |  |  | True | 29 | 54 | 341 | 337 | 26 | 0.43 |
| caso01_bfs_vs_dfs | A_ESTRELLA | manhattan |  | True | 29 | 54 | 346 | 294 | 35 | 0.406 |
| caso01_bfs_vs_dfs | A_ESTRELLA | obstaculos |  | True | 29 | 54 | 333 | 281 | 35 | 0.395 |
| caso01_bfs_vs_dfs | BEAM | manhattan | 2 | True | 29 | 55 | 109 | 57 | 5 | 0.082 |
| caso01_bfs_vs_dfs | BEAM | obstaculos | 2 | True | 29 | 55 | 106 | 57 | 5 | 0.081 |
| caso02_ruta_corta_vs_economica | BFS |  |  | True | 17 | 83 | 299 | 279 | 23 | 0.293 |
| caso02_ruta_corta_vs_economica | DFS |  |  | True | 25 | 97 | 208 | 166 | 99 | 0.172 |
| caso02_ruta_corta_vs_economica | UCS |  |  | True | 33 | 33 | 272 | 242 | 35 | 0.32 |
| caso02_ruta_corta_vs_economica | A_ESTRELLA | manhattan |  | True | 33 | 33 | 179 | 92 | 68 | 0.151 |
| caso02_ruta_corta_vs_economica | A_ESTRELLA | obstaculos |  | True | 33 | 33 | 179 | 92 | 68 | 0.168 |
| caso02_ruta_corta_vs_economica | BEAM | manhattan | 2 | True | 17 | 83 | 70 | 33 | 5 | 0.048 |
| caso02_ruta_corta_vs_economica | BEAM | obstaculos | 2 | True | 17 | 83 | 70 | 33 | 5 | 0.048 |
| caso03_obstaculo_heuristica | BFS |  |  | True | 32 | 32 | 371 | 366 | 20 | 0.371 |
| caso03_obstaculo_heuristica | DFS |  |  | True | 76 | 76 | 375 | 299 | 144 | 0.306 |
| caso03_obstaculo_heuristica | UCS |  |  | True | 32 | 32 | 371 | 366 | 20 | 0.459 |
| caso03_obstaculo_heuristica | A_ESTRELLA | manhattan |  | True | 32 | 32 | 314 | 282 | 32 | 0.38 |
| caso03_obstaculo_heuristica | A_ESTRELLA | obstaculos |  | True | 32 | 32 | 248 | 177 | 71 | 0.256 |
| caso03_obstaculo_heuristica | BEAM | manhattan | 2 | True | 34 | 34 | 118 | 67 | 5 | 0.092 |
| caso03_obstaculo_heuristica | BEAM | obstaculos | 2 | True | 32 | 32 | 120 | 63 | 6 | 0.088 |
| caso04_comparacion_heuristicas | BFS |  |  | True | 32 | 112 | 354 | 350 | 23 | 0.365 |
| caso04_comparacion_heuristicas | DFS |  |  | True | 106 | 372 | 307 | 186 | 145 | 0.198 |
| caso04_comparacion_heuristicas | UCS |  |  | True | 34 | 64 | 350 | 332 | 27 | 0.427 |
| caso04_comparacion_heuristicas | A_ESTRELLA | manhattan |  | True | 34 | 64 | 327 | 294 | 36 | 0.431 |
| caso04_comparacion_heuristicas | A_ESTRELLA | obstaculos |  | True | 34 | 64 | 323 | 289 | 32 | 0.387 |
| caso04_comparacion_heuristicas | BEAM | manhattan | 2 | True | 34 | 81 | 107 | 63 | 5 | 0.098 |
| caso04_comparacion_heuristicas | BEAM | obstaculos | 2 | True | 32 | 112 | 115 | 63 | 5 | 0.084 |
| caso05_beam | BFS |  |  | True | 21 | 21 | 329 | 312 | 21 | 0.301 |
| caso05_beam | DFS |  |  | True | 25 | 25 | 195 | 166 | 86 | 0.159 |
| caso05_beam | UCS |  |  | True | 21 | 21 | 329 | 312 | 21 | 0.365 |
| caso05_beam | A_ESTRELLA | manhattan |  | True | 21 | 21 | 108 | 65 | 43 | 0.086 |
| caso05_beam | A_ESTRELLA | obstaculos |  | True | 21 | 21 | 97 | 50 | 47 | 0.07 |
| caso05_beam | BEAM | manhattan | 2 | True | 21 | 21 | 67 | 41 | 5 | 0.052 |
| caso05_beam | BEAM | obstaculos | 2 | True | 21 | 21 | 71 | 41 | 6 | 0.053 |
| caso06_estado_compuesto | BFS |  |  | True | 20 | 22 | 307 | 285 | 25 | 0.315 |
| caso06_estado_compuesto | DFS |  |  | True | 20 | 22 | 392 | 387 | 164 | 0.419 |
| caso06_estado_compuesto | UCS |  |  | True | 20 | 22 | 133 | 113 | 20 | 0.167 |
| caso06_estado_compuesto | A_ESTRELLA | manhattan |  | True | 20 | 22 | 26 | 20 | 6 | 0.028 |
| caso06_estado_compuesto | A_ESTRELLA | obstaculos |  | True | 20 | 22 | 26 | 20 | 6 | 0.028 |
| caso06_estado_compuesto | BEAM | manhattan | 2 | True | 20 | 22 | 70 | 39 | 5 | 0.06 |
| caso06_estado_compuesto | BEAM | obstaculos | 2 | True | 20 | 22 | 79 | 39 | 4 | 0.063 |

## E2_beam — E2: Beam Search con k = 1, 2, 4, 8, 16 y criterio h o f (casos 3 y 5).

Archivo: `E2_beam.csv`

| caso | k | criterio | descartados | exito | longitud | costo | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms |
|---|---|---|---|---|---|---|---|---|---|---|
| caso03_obstaculo_heuristica | 1 | h | 49 | True | 36 | 36 | 86 | 36 | 4 | 0.067 |
| caso03_obstaculo_heuristica | 2 | h | 49 | True | 34 | 34 | 118 | 67 | 5 | 0.086 |
| caso03_obstaculo_heuristica | 4 | h | 55 | True | 32 | 32 | 184 | 125 | 8 | 0.145 |
| caso03_obstaculo_heuristica | 8 | h | 52 | True | 32 | 32 | 305 | 245 | 13 | 0.272 |
| caso03_obstaculo_heuristica | 16 | h | 9 | True | 32 | 32 | 371 | 357 | 18 | 0.393 |
| caso03_obstaculo_heuristica | 1 | f | 49 | True | 36 | 36 | 86 | 36 | 4 | 0.06 |
| caso03_obstaculo_heuristica | 2 | f | 49 | True | 34 | 34 | 118 | 67 | 5 | 0.09 |
| caso03_obstaculo_heuristica | 4 | f | 55 | True | 32 | 32 | 184 | 125 | 8 | 0.146 |
| caso03_obstaculo_heuristica | 8 | f | 52 | True | 32 | 32 | 305 | 245 | 13 | 0.279 |
| caso03_obstaculo_heuristica | 16 | f | 9 | True | 32 | 32 | 371 | 357 | 18 | 0.381 |
| caso05_beam | 1 | h | 5 | False | 0 | 0 | 19 | 14 | 4 | 0.019 |
| caso05_beam | 2 | h | 24 | True | 21 | 21 | 67 | 41 | 5 | 0.053 |
| caso05_beam | 4 | h | 41 | True | 21 | 21 | 126 | 81 | 8 | 0.092 |
| caso05_beam | 8 | h | 37 | True | 21 | 21 | 200 | 155 | 12 | 0.165 |
| caso05_beam | 16 | h | 20 | True | 21 | 21 | 311 | 275 | 19 | 0.297 |
| caso05_beam | 1 | f | 5 | False | 0 | 0 | 19 | 14 | 4 | 0.017 |
| caso05_beam | 2 | f | 24 | True | 21 | 21 | 67 | 41 | 5 | 0.05 |
| caso05_beam | 4 | f | 41 | True | 21 | 21 | 126 | 81 | 8 | 0.098 |
| caso05_beam | 8 | f | 37 | True | 21 | 21 | 200 | 155 | 12 | 0.175 |
| caso05_beam | 16 | f | 20 | True | 21 | 21 | 311 | 275 | 19 | 0.294 |

## E3_sensibilidad — E3: costo del pantano de 1 a 20 en el caso 2 (el ejemplo del profesor: 7 -> 15).

Archivo: `E3_sensibilidad.csv`

| costo_pantano | algoritmo | exito | longitud | costo | estados_generados | estados_expandidos | maximo_frontera | tiempo_ms |
|---|---|---|---|---|---|---|---|---|
| 1 | BFS | True | 17 | 23 | 299 | 279 | 23 | 0.283 |
| 1 | UCS | True | 17 | 23 | 334 | 311 | 30 | 0.389 |
| 1 | A_ESTRELLA | True | 17 | 23 | 104 | 55 | 45 | 0.113 |
| 2 | BFS | True | 17 | 33 | 299 | 279 | 23 | 0.283 |
| 2 | UCS | True | 17 | 33 | 345 | 334 | 26 | 0.409 |
| 2 | A_ESTRELLA | True | 17 | 33 | 298 | 156 | 93 | 0.234 |
| 3 | BFS | True | 17 | 43 | 299 | 279 | 23 | 0.283 |
| 3 | UCS | True | 33 | 33 | 319 | 300 | 28 | 0.359 |
| 3 | A_ESTRELLA | True | 33 | 33 | 219 | 116 | 76 | 0.171 |
| 5 | BFS | True | 17 | 63 | 299 | 279 | 23 | 0.269 |
| 5 | UCS | True | 33 | 33 | 289 | 263 | 32 | 0.313 |
| 5 | A_ESTRELLA | True | 33 | 33 | 185 | 98 | 68 | 0.143 |
| 7 | BFS | True | 17 | 83 | 299 | 279 | 23 | 0.276 |
| 7 | UCS | True | 33 | 33 | 272 | 242 | 35 | 0.304 |
| 7 | A_ESTRELLA | True | 33 | 33 | 179 | 92 | 68 | 0.136 |
| 10 | BFS | True | 17 | 113 | 299 | 279 | 23 | 0.27 |
| 10 | UCS | True | 33 | 33 | 257 | 222 | 38 | 0.268 |
| 10 | A_ESTRELLA | True | 33 | 33 | 176 | 89 | 68 | 0.131 |
| 15 | BFS | True | 17 | 163 | 299 | 279 | 23 | 0.281 |
| 15 | UCS | True | 33 | 33 | 246 | 209 | 40 | 0.255 |
| 15 | A_ESTRELLA | True | 33 | 33 | 172 | 85 | 68 | 0.138 |
| 20 | BFS | True | 17 | 213 | 299 | 279 | 23 | 0.288 |
| 20 | UCS | True | 33 | 33 | 239 | 201 | 41 | 0.241 |
| 20 | A_ESTRELLA | True | 33 | 33 | 172 | 85 | 68 | 0.124 |

## E4_profundidad — E4: Minimax vs alfa-beta con profundidad 1 a 5 en el estado del caso 8 (Minimax hasta 4).

Archivo: `E4_profundidad.csv`

| profundidad | algoritmo | accion | valor | nodos_generados | nodos_evaluados | nodos_podados | profundidad_alcanzada | tiempo_ms |
|---|---|---|---|---|---|---|---|---|
| 1 | MINIMAX | A1 → (9, 8) | -35.0 | 13 | 12 | 0 | 1 | 1.724 |
| 1 | ALFA_BETA | A1 → (9, 8) | -35.0 | 13 | 12 | 0 | 1 | 0.262 |
| 2 | MINIMAX | A2 → (11, 7) | -41.0 | 157 | 144 | 0 | 2 | 2.677 |
| 2 | ALFA_BETA | A2 → (11, 7) | -41.0 | 47 | 34 | 110 | 2 | 0.723 |
| 3 | MINIMAX | A2 → (11, 7) | -38.0 | 1882 | 1725 | 0 | 3 | 32.322 |
| 3 | ALFA_BETA | A2 → (11, 7) | -38.0 | 213 | 166 | 352 | 3 | 3.54 |
| 4 | MINIMAX | A2 → (12, 6) | -47.0 | 22360 | 20478 | 0 | 4 | 385.261 |
| 4 | ALFA_BETA | A2 → (12, 6) | -47.0 | 640 | 427 | 1911 | 4 | 10.137 |
| 5 | ALFA_BETA | A2 → (12, 6) | -44.0 | 2652 | 2012 | 5013 | 5 | 43.452 |

## E5_orden — E5: efecto del orden de generación de acciones en la poda (caso 9).

Archivo: `E5_orden.csv`

| profundidad | orden | accion | valor | nodos_generados | nodos_evaluados | nodos_podados | profundidad_alcanzada | tiempo_ms |
|---|---|---|---|---|---|---|---|---|
| 2 | natural | A2 → (11, 7) | -41.0 | 47 | 34 | 110 | 2 | 2.321 |
| 2 | inverso | A2 → (11, 7) | -41.0 | 131 | 118 | 26 | 2 | 2.287 |
| 2 | heuristico | A2 → (11, 7) | -41.0 | 47 | 34 | 110 | 2 | 3.499 |
| 3 | natural | A2 → (11, 7) | -38.0 | 213 | 166 | 352 | 3 | 3.542 |
| 3 | inverso | A2 → (11, 7) | -38.0 | 1144 | 1013 | 426 | 3 | 19.909 |
| 3 | heuristico | A2 → (11, 7) | -38.0 | 213 | 166 | 352 | 3 | 13.888 |
| 4 | natural | A2 → (12, 6) | -47.0 | 640 | 427 | 1911 | 4 | 9.844 |
| 4 | inverso | A2 → (11, 7) | -47.0 | 11318 | 10234 | 1562 | 4 | 196.75 |
| 4 | heuristico | A2 → (12, 6) | -47.0 | 639 | 426 | 1911 | 4 | 54.323 |

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
