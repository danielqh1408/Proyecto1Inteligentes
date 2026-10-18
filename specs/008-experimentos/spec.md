# 008 — Casos mínimos, experimentación y evidencia reproducible

| Campo | Valor |
|---|---|
| Estado | **implementada** (falta revisión y la interpretación escrita en el documento técnico) |
| Responsable | Juan · Revisor: Daniel |
| Rúbrica | Experimentación, métricas e interpretación (10 %) + evidencia de los demás criterios |
| Depende de | 003, 004, 005, 006 |
| Fuente en el enunciado | "Casos mínimos para demostrar la solución" (pp. 8–9), "Resultados y métricas comparables" (p. 7), "Entregables" (p. 9) |

## 1. Contexto y porqué
"Cada equipo deberá preparar datos reproducibles, declarar el estado inicial y comparar los resultados **esperados** con los **obtenidos**." Cada caso mínimo es un JSON con su estado inicial, la prueba y lo que esperamos (campo extra `esperado`), y un comando que regenera la evidencia.

## 2. Casos mínimos (todos ≥ 20×20 salvo que se indique)

| # | Archivo `escenarios/casos/` | Qué demuestra | `esperado` (resumen) | Spec |
|---|---|---|---|---|
| 1 | `caso01_bfs_vs_dfs.json` | Ambos encuentran solución, recorren distinto | ambos `exito`; `orden_expansion` distinto; long(BFS) ≤ long(DFS) | 003 |
| 2 | `caso02_ruta_corta_vs_economica.json` | BFS y UCS dan caminos distintos por el costo | long(BFS) < long(UCS) y costo(UCS) < costo(BFS) | 003 |
| 3 | `caso03_obstaculo_heuristica.json` | El objetivo parece cerca pero un muro obliga a rodear | A\* H2 expande < A\* H1; ambos óptimos | 004 |
| 4 | `caso04_comparacion_heuristicas.json` | A\* con las dos heurísticas en el mismo escenario | tabla H1 vs H2 (+ UCS como referencia) | 004 |
| 5 | `caso05_beam.json` | Cambiar k modifica la exploración y la solución | k=1 falla o da costo mayor; k=8 encuentra el óptimo o cercano | 004 |
| 6 | `caso06_estado_compuesto.json` | Misma posición, estados distintos (lleva / no lleva recurso) | misión pasa 2 veces por una celda con distinto `lleva` | 002 |
| 7 | `caso07_decision_adversarial.json` | La mejor jugada Minimax ≠ avanzar directo al recurso | acción(Minimax) ≠ acción(VORAZ) | 005 |
| 8 | `caso08_minimax_vs_alfabeta.json` | Misma acción; αβ evalúa menos | acciones y valores iguales; evaluados(αβ) < evaluados(MM) | 005 |
| 9 | `caso09_orden_acciones.json` | El orden de sucesores cambia la poda | podados distintos con natural/inverso/heurístico | 005 |
| 10 | `caso10_profundidad.json` | Mismo estado con distintas profundidades | tabla prof 1…5: nodos, tiempo, acción | 005 |

Además:
- `escenarios/ejemplo_enunciado.json` — copia literal del PDF (prueba de contrato).
- `escenarios/sensibilidad/pantano_7.json` y `pantano_15.json` — el ejemplo que da el profesor: predecir y luego observar el efecto en UCS y A\*.
- `escenarios/invalidos/*.json` — spec 001.
- `escenarios/externos/` — carpeta vacía para los JSON que traiga el profesor (y para practicar con mapas que nos inventemos el uno al otro).

## 3. Experimentos (además de los casos)
| ID | Experimento | Variables | Salida |
|---|---|---|---|
| E1 | Comparación de los 5 algoritmos de búsqueda en todos los casos | algoritmo × heurística | `resultados/busqueda.csv` |
| E2 | Beam k ∈ {1, 2, 4, 8, 16} × criterio {h, f} | k, criterio | `resultados/beam.csv` + gráfica |
| E3 | Sensibilidad al costo (pantano 1 → 20) | costo | `resultados/sensibilidad.csv` + gráfica costo vs. camino |
| E4 | Minimax vs αβ por profundidad 1…5 | profundidad × algoritmo | `resultados/adversarial_profundidad.csv` + gráfica nodos (escala log) |
| E5 | Orden de acciones vs poda | orden × profundidad | `resultados/orden_poda.csv` |
| E6 | Torneo corto: αβ(d) vs VORAZ y αβ(d1) vs αβ(d2), alternando quién empieza | profundidades | `resultados/torneo.csv` (victorias/empates/turnos) |

## 4. Diseño

> **Implementado:** `tacticalgrid/experimentos/casos.py` (una función por caso: carga, ejecuta y compara con lo esperado; la usan los tests y el reporte) y `experimentos/reporte.py` (E1–E6 + `resultados/RESUMEN.md`). Comando: `python -m tacticalgrid experimentos` (≈ 5 s). Los escenarios incluyen `descripcion`, `esperado` y `mapa_ascii` (dibujo del mapa) como campos extra.
> Cambios frente al bosquejo: sin gráficas (matplotlib opcional, no instalado); tiempo de una sola corrida (no mediana de 5); E6 usa `escenarios/partida_simetrica.json` (21×21 simétrico por rotación) para que el resultado dependa del agente y no del mapa.
> **Hallazgos para el documento técnico:** caso 2 (BFS 17 pasos/costo 83 vs UCS 33/33); caso 3 (A\* H2 177 vs H1 282 expandidos); caso 5 (Beam k=1 falla); E3 (con pantano ≥ 3 UCS cambia al rodeo); E4/E5 (alfa‑beta prof. 4: 427 evaluados vs 20 478 de Minimax; con orden inverso 10 234); E6 (más profundidad gana; igual profundidad empata).
>
> Bosquejo original:
```
tacticalgrid/experimentos/
├── runner.py       # ejecutar_caso(ruta) -> dict con obtenidos + comparación contra `esperado`
├── experimentos.py # E1…E6, cada uno una función pura que devuelve filas
└── reporte.py      # escribe CSV/JSON y resultados/RESUMEN.md (tablas markdown + ✔/✘ esperado vs obtenido)
```
- `python -m tacticalgrid experimentos [--solo E2] [--salida resultados/]`.
- Cada archivo de salida incluye cabecera con: fecha, commit (`git rev-parse --short HEAD`), versión de Python, parámetros. ⇒ reproducibilidad.
- Tiempos: mediana de 5 repeticiones (el resto de métricas es determinista).
- Gráficas con matplotlib **opcionales** (si no está instalado, solo CSV).

## 5. Criterios de aceptación
- **CA-008-1** `pytest tests/test_casos.py` ejecuta los 10 casos y compara `esperado` vs obtenido. → verde.
- **CA-008-2** `python -m tacticalgrid experimentos` regenera `resultados/` sin intervención y `RESUMEN.md` muestra ✔ en los 10 casos.
- **CA-008-3** Ejecutar dos veces produce CSV idénticos salvo la columna de tiempo.
- **CA-008-4** Cada caso declara estado inicial (en el propio JSON) y una descripción en el campo extra `descripcion`.

## 6. Tareas
- [x] T1 Diseñar los mapas de los casos 1–6 — generados con Claude (ver `mapa_ascii` en cada JSON); **verificar a mano al revisar** — ambos
- [x] T2 Diseñar los estados de los casos 7–10 — implementado con Claude; revisan ambos
- [x] T3 `runner.py` + comparación con `esperado` — implementado con Claude; revisan ambos
- [x] T4 E1–E6 + `RESUMEN.md` — implementado con Claude; revisan ambos
- [ ] T5 Interpretación escrita de cada experimento en el documento técnico — Ambos
