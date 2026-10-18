# 005 — Decisión adversarial: Minimax, alfa‑beta y función de utilidad

| Campo | Valor |
|---|---|
| Estado | **implementada** (falta revisión de Daniel y validación de estudiante en docstrings) |
| Responsable | Daniel · Revisor: Juan |
| Rúbrica | Minimax y poda alfa‑beta (20 %) |
| Depende de | 002 (reglas), 004 (distancias precalculadas reutilizan la infraestructura de búsqueda) |
| Fuente en el enunciado | "Decisión adversarial", "MAX, MIN y función de utilidad", "Profundidad y poda alfa‑beta" (pp. 4–5); casos 7–10 |
| Base del curso | `minimax_limitado`, `mejor_jugada_*` (Minimax.ipynb), `alfa_beta` y move ordering (Poda_Alfa_Beta.ipynb) |

## 1. Contexto y porqué
La pregunta cambia de "¿cuál es mi mejor camino?" a "¿cuál es mi mejor **acción** teniendo en cuenta las respuestas posibles del adversario?". El árbol tiene profundidad limitada ⇒ hace falta una **función de evaluación** propia para estados no terminales.

## 2. Requisitos
- **RF-005-1** Minimax con profundidad limitada; la profundidad máxima se cambia **sin tocar código** (`juego.profundidad_maxima_minimax`, `--profundidad`, control en la GUI).
- **RF-005-2** Minimax con poda alfa‑beta.
- **RF-005-3** Con igual profundidad, utilidad y orden de acciones, ambos eligen **la misma acción** y el mismo valor.
- **RF-005-4** Cambiar el orden de generación de acciones y medir su efecto en la poda.
- **RF-005-5** Métricas: nodos generados, nodos evaluados, nodos podados, profundidad alcanzada, tiempo, acción seleccionada, valor obtenido.
- **RF-005-6** Función de utilidad propia desde la perspectiva de un bando, explicable: por qué una acción vale más que otra y qué pasa si cambian los pesos.

## 3. MAX, MIN y perspectiva (decisión D‑08)
- **MAX = el bando que tiene el turno en el estado raíz** (el que pide la decisión). MIN = el otro.
- La evaluación es **de suma cero y simétrica**: `E(s, perspectiva=A) = −E(s, perspectiva=B)`. Ambos bandos usan las **mismas reglas** y la **misma** función; MIN minimizar `E_A` equivale exactamente a que B maximice `E_B`. Por eso **MIN no está en desventaja**: MAX/MIN son roles en el árbol, no inteligencias distintas.

## 4. Función de utilidad / evaluación (decisión D‑09)

Distancias precalculadas **una vez por escenario** (Dijkstra con costos del JSON, respetando R3 "no se entra a la base enemiga"):
- `Dbase_X(p)`: costo mínimo desde `p` hasta la base del bando X.
- `Drec_X(p)`: costo mínimo desde `p` hasta la posición libre del recurso para unidades del bando X.

**Estados terminales** (perspectiva MAX, `prof` = profundidad a la que se alcanzó):
- MAX gana: `+V_GANAR − prof` (prefiere ganar **antes**). MIN gana: `−V_GANAR + prof` (prefiere perder **después**). Empate: `0`.

**Estados no terminales:** `E(s) = Σ wᵢ · fᵢ(s)` *(versión implementada en `adversarial/utilidad.py`)*

Primero se define **`restante(X)`** = costo que le falta al bando X para ganar si nadie lo estorbara:
- si X lleva el recurso: `Dbase_X(portador)`;
- si el recurso está libre: `min_{u∈X} Drec_X(u) + Dbase_X(recurso)`;
- si lo lleva el rival: `min_{u∈X} manhattan(u, portador) + Dbase_X(portador)` (alcanzarlo para interceptar y volver).

| # | Componente fᵢ | Definición (positivo = bueno para MAX) | Peso por defecto |
|---|---|---|---|
| f1 | Posesión | +1 si MAX porta, −1 si MIN porta, 0 si está libre | `posesion = 50` |
| f2 | Carrera | `restante(MIN) − restante(MAX)`: quién está más cerca de ganar | `carrera = 3` |
| f3 | Movilidad (unidades disponibles / bloqueo) | `#acciones_legales(MAX) − #acciones_legales(MIN)` | `movilidad = 0.1` |

`V_GANAR = 10 000` (en `config.VALOR_VICTORIA`).

> **Lección aprendida (para la sustentación):** la primera versión tenía 5 componentes separados (posesión, carrera al recurso, progreso de entrega, presión, movilidad). Al jugar partidas se vio que **una unidad al lado del recurso prefería no recogerlo**: al recogerlo desaparecía el término "carrera al recurso" (grande) y aparecía "entrega" (negativo). La evaluación no era **monótona**. Unificar todo en `restante` corrige eso: recoger el recurso nunca empeora el valor (`test_recoger_siempre_mejora`). La proximidad del adversario sigue presente dentro de `restante` del bando que persigue.

- Pesos configurables en `config.py` y sobreescribibles con `juego.pesos_utilidad` en el JSON (sin tocar código).
- `evaluar(...)` devuelve también el **desglose** `{posesion, carrera, movilidad}` para explicar por qué una acción vale más que otra.
- **Complejidad:** precálculo de 4 Dijkstra O(V log V) (con caché por escenario); cada evaluación O(U) por la movilidad.
- *Alternativas descartadas:* utilidad solo terminal (con profundidad limitada casi todas las hojas valdrían 0); Manhattan en lugar de Dijkstra (ignoraría costos y muros).

## 5. Algoritmos

> **Implementado:** `adversarial/minimax.py` — `decidir(..., poda)` es UNA sola función recursiva; `minimax` y `alfa_beta` la llaman con `poda=False/True`. La única diferencia es `if poda and alfa >= beta: break`. `voraz` = `decidir` con profundidad 1. `adversarial/partida.py` tiene el bucle por turnos. CLI: `decidir`, `partida`, `ejecutar`.

```python
minimax(escenario, estado, profundidad, orden="natural", pesos=None) -> ResultadoDecision
alfa_beta(escenario, estado, profundidad, orden="natural", pesos=None) -> ResultadoDecision
```
- Recursión con `es_max`, igual a `minimax_limitado` de clase: terminal ⇒ utilidad; profundidad 0 ⇒ evaluación; si no, max/min de los hijos.
- **Desempate (invariante RF‑005‑3):** en la raíz se elige la **primera** acción cuyo valor sea **estrictamente** mejor (`>` para MAX). En alfa‑beta, un hijo podado devuelve una cota ≤ α y nunca reemplaza a la mejor ⇒ misma acción que Minimax.
- **Orden de acciones** (`orden`): `natural` (R10 de spec 002), `inverso`, `heuristico` (hijos ordenados por evaluación estática: descendente para MAX, ascendente para MIN). Las evaluaciones usadas solo para ordenar se cuentan aparte (`evaluaciones_ordenamiento`) para no contaminar la comparación.

### Métricas (definición única)
| Métrica | Definición |
|---|---|
| `nodos_generados` | Estados creados con `aplicar` durante la búsqueda **+ 1** (la raíz). |
| `nodos_evaluados` | Llamadas a utilidad terminal o a la evaluación por límite de profundidad. |
| `nodos_podados` | Suma, en cada corte α ≥ β, del número de acciones hermanas **no exploradas** en ese nodo (ramas evitadas; no se estima el tamaño del subárbol). 0 en Minimax. |
| `profundidad_alcanzada` | Máxima profundidad efectivamente visitada (puede ser < límite si hay terminales). |
| `tiempo_ms` | `perf_counter` alrededor de la decisión. |
| `accion` | Acción recomendada (texto legible, p. ej. `A2 → derecha (5,6)`). |
| `valor` | Valor Minimax del estado raíz. |
| `valores_raiz` | (extra) `[(accion, valor, es_cota)]` por cada acción de la raíz — en alfa‑beta las no elegidas pueden ser cotas. |
| `variacion_principal` | (extra) secuencia de acciones esperada y `desglose` de la evaluación en la hoja. |

## 6. Modo partida (`prueba.modo = partida`)
Bucle por turnos donde cada bando se controla como `MINIMAX`, `ALFA_BETA` o `VORAZ` (= `decidir` con profundidad 1: no mira la respuesta del rival; contraste del caso 7). El control `HUMANO` se hace desde la GUI (spec 007). Cada jugada se valida con `reglas.aplicar` y se registra en un historial exportable.

## 7. Criterios de aceptación
- **CA-005-1** **Caso 8:** Minimax y alfa‑beta devuelven la misma acción y el mismo valor en todos los estados de `escenarios/casos/` y en 50 estados alcanzables aleatorios (semilla fija), para profundidades 1–4 y los 3 órdenes; `nodos_evaluados(αβ) ≤ nodos_evaluados(minimax)` y es estrictamente menor en el caso 8. → `test_adversarial.py::test_minimax_igual_alfabeta`
- **CA-005-2** **Caso 7:** en `caso07_decision_adversarial.json` la acción de Minimax (prof ≥ 3) **no** es la del agente VORAZ (no avanza directo al recurso: bloquea o se posiciona para interceptar). → `test_casos.py::test_caso07`
- **CA-005-3** **Caso 9:** en `caso09_orden_acciones.json`, `nodos_podados` difiere entre `natural`, `inverso` y `heuristico`, con el mismo **valor** (la acción puede cambiar solo si hay empates de valor, porque se elige la primera en el orden). → `test_casos.py::test_caso09`
- **CA-005-4** **Caso 10:** el mismo estado evaluado con profundidad 1…5 reporta nodos y tiempo crecientes; se registra si cambia la acción. → `test_casos.py::test_caso10`
- **CA-005-5** Simetría: `evaluar(s, "A") == -evaluar(s, "B")` para estados no terminales. → `test_utilidad.py::test_suma_cero`
- **CA-005-6** Ganar en 1 jugada vale más que ganar en 3 (preferencia por victorias rápidas). → `test_utilidad.py::test_preferencia_victoria_rapida`
- **CA-005-7** Cambiar `juego.pesos_utilidad` en el JSON cambia el valor. → `test_utilidad.py::test_pesos_desde_json`
- **CA-005-8** Toda acción considerada en el árbol es legal (verificador en modo auditoría, spec 006). → `test_adversarial.py::test_acciones_legales_en_arbol`
- **CA-005-9** La profundidad del JSON se usa si no se pasa otra; la CLI la sobreescribe. → `test_cli.py::test_profundidad`

## 8. Tareas
- [x] T1 Distancias precalculadas (Dijkstra multi‑fuente inversa) — implementado con Claude; revisa Daniel
- [x] T2 `evaluar` con desglose + utilidad terminal — implementado con Claude; revisa Daniel
- [x] T3 `minimax` con métricas, valores de la raíz y desglose — implementado con Claude; revisa Daniel
- [x] T4 `alfa_beta` con conteo de podas — implementado con Claude; revisa Daniel
- [x] T5 Ordenamiento de acciones (natural / inverso / heurístico) — implementado con Claude; revisa Daniel
- [x] T6 Modo partida + agente VORAZ — implementado con Claude; revisa Daniel
- [x] T7 Escenarios `caso07`…`caso10` — implementado con Claude; revisa Daniel
- [x] T8 Tests CA‑005‑1…9 — implementado con Claude; revisa Daniel
- [ ] T9 Sección "Función de utilidad" y "Adversarial" del documento técnico — Daniel
- [ ] T10 Revisión y simulacro — Juan

## 9. Para sustentar
- *¿Por qué esta acción vale más que esta otra?* → `python -m tacticalgrid decidir <json>` muestra el valor de cada acción de la raíz y el `desglose` del estado elegido.
- *¿Por qué MIN no está en desventaja?* → §3: mismas reglas, misma función negada; minimizar E_A = maximizar E_B.
- *¿Por qué alfa‑beta da la misma decisión?* → Solo descarta ramas que no pueden cambiar el valor de la raíz; desempate por primera acción estrictamente mejor.
- *¿Qué pasa si invierto el orden de acciones?* → Mismo valor y acción; cambia cuántas ramas se podan. Mejor orden ≈ O(b^(m/2)); peor ≈ O(b^m).
- *¿Qué pasa si sube la profundidad de 2 a 4?* → Nodos crecen ~b² veces (b ≈ 10–15); la acción puede cambiar al "ver" una intercepción que antes estaba fuera del horizonte.
- *Si posesion = 0, ¿qué hace la IA?* → Sigue queriendo el recurso por la carrera (recogerlo reduce lo que le falta), pero deja de "proteger" la posesión con fuerza: puede preferir otra jugada si acerca más la victoria.
- *¿Por qué cambiaron de 5 a 3 componentes?* → Ver la lección aprendida en §4: la evaluación debe ser monótona respecto al objetivo.
