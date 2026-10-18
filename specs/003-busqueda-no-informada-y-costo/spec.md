# 003 — BFS, DFS y Costo Uniforme (UCS) + definición única de métricas

| Campo | Valor |
|---|---|
| Estado | borrador |
| Responsable | Juan · Revisor: Daniel |
| Rúbrica | BFS, DFS y Costo Uniforme (15 %) |
| Depende de | 001, 002 (§3.4 problemas de búsqueda) |
| Fuente en el enunciado | "Búsqueda no informada", "Búsqueda basada en costos", "Resultados y métricas comparables" (pp. 3–4, 7); casos 1 y 2 |
| Base del curso | `Resolucion_Problemas_Busqueda_NoInformada.ipynb` (bfs/dfs con `deque` y pila), `Resolucion_Problemas_Busqueda_Informada.ipynb` (`costo_uniforme` con `heapq`, `count()` y `mejor_g`) |

## 1. Contexto y porqué
Primera pregunta del proyecto: *¿existe una ruta?* (BFS/DFS) y luego *¿cuál es la más barata?* (UCS). Las implementaciones siguen **el mismo estilo que en clase** para que la sustentación sea natural, pero operan sobre un `ProblemaBusqueda` genérico (no sobre una matriz de 0/1) y reportan métricas completas.

## 2. Requisitos
- **RF-003-1** BFS (cola FIFO) y DFS (pila LIFO) sobre el mismo modelo de escenario.
- **RF-003-2** UCS: minimiza costo acumulado g(n) con costos tomados del escenario.
- **RF-003-3** Los tres funcionan con `ProblemaNavegacion` y `ProblemaMision` sin cambios.
- **RF-003-4** Métricas mínimas: solución sí/no, longitud, costo, estados generados, estados expandidos, máximo de frontera, tiempo.
- **RF-003-5** Salida equivalente a la estructura del enunciado: `{"algoritmo", "exito", "camino", "costo", "estados_generados", "estados_expandidos", "maximo_frontera"}` (+ extras).
- **RF-003-6** Al menos un escenario donde BFS y UCS den caminos distintos (caso 2) y uno donde BFS y DFS recorran distinto (caso 1).

## 3. Definición ÚNICA de métricas (aplica a 003 y 004)

| Métrica | Definición operativa (exacta) |
|---|---|
| `exito` | `True` si se extrajo de la frontera un estado objetivo. |
| `camino` | Lista de posiciones `[[f, c], …]` desde el inicio hasta el objetivo (incluye ambos extremos). Vacía si no hay éxito. |
| `longitud` | `len(camino) - 1` = número de movimientos. |
| `costo` | Σ `costo(celda)` de cada celda del camino **excepto la inicial**. |
| `estados_generados` | Número de **inserciones** en la frontera, incluida la del estado inicial. En UCS/A\*, una re‑inserción por mejora de g cuenta como generación nueva. |
| `estados_expandidos` | Número de estados **extraídos de la frontera cuyos sucesores se calcularon**. El objetivo extraído **no** cuenta (no se expande). En UCS/A\*, las entradas obsoletas (g ≠ mejor_g) **no** cuentan. |
| `maximo_frontera` | Máximo de `len(frontera)` observado tras cada inserción (incluye entradas obsoletas del heap — se documenta). |
| `tiempo_ms` | `time.perf_counter()` alrededor del algoritmo, sin incluir carga ni dibujo. |
| `orden_expansion` | (extra, para la GUI) lista de posiciones en el orden en que se expandieron. |
| `frontera_final` | (extra, para la GUI) posiciones que quedaron en la frontera al terminar. |

**Prueba de objetivo:** en los cinco algoritmos se hace **al extraer** de la frontera (no al generar). Es lo que hacen los notebooks de clase para UCS/A\* y es necesario para la optimalidad de UCS/A\*; usarlo también en BFS/DFS hace las métricas comparables. *Consecuencia a explicar:* BFS genera algunos nodos más que si probara al generar.

## 4. Diseño

```
tacticalgrid/busqueda/
├── resultado.py         # ResultadoBusqueda (dataclass) + to_dict() con las claves del enunciado
├── metricas.py          # ContadorMetricas: generar(), expandir(), observar_frontera(n)
├── no_informada.py      # bfs(problema), dfs(problema)
└── costo_uniforme.py    # costo_uniforme(problema)
```

Pseudocódigo (búsqueda en grafo, misma forma que en clase):

```text
BFS:  frontera = deque([inicio]); padres = {inicio: None}            # padres hace de 'visitados'
      while frontera:
          s = frontera.popleft()
          if objetivo(s): return reconstruir(padres, s)
          expandidos += 1
          for (a, s2, c) in sucesores(s):
              if s2 not in padres: padres[s2] = s; frontera.append(s2); generados += 1

DFS:  idéntico con pila (pop() del final). Visitados se marcan al apilar (como en clase).

UCS:  frontera = [(0, tie, inicio)]; mejor_g = {inicio: 0}
      while frontera:
          g, _, s = heappop(frontera)
          if g != mejor_g[s]: continue                     # entrada obsoleta (eliminación perezosa)
          if objetivo(s): return reconstruir(...)
          expandidos += 1
          for (a, s2, c) in sucesores(s):
              ng = g + c
              if ng < mejor_g.get(s2, inf): mejor_g[s2] = ng; padres[s2] = s; heappush(frontera, (ng, next(tie), s2))
```

- Reconstrucción por diccionario de padres (O(L)), no copiando listas `camino + [x]` en cada nodo (más eficiente en 20×20+; explicar la diferencia con el notebook).
- Desempate en el heap con `itertools.count()` ⇒ determinismo (P5).
- DFS **no** garantiza camino mínimo y depende del orden de movimientos (taller 1 del notebook).

## 5. Complejidad (para el documento técnico)
| Algoritmo | Tiempo | Espacio | Completo | Óptimo |
|---|---|---|---|---|
| BFS | O(V + E) | O(V) | Sí (finito) | En número de movimientos, no en costo |
| DFS (grafo) | O(V + E) | O(V) | Sí (finito, con visitados) | No |
| UCS | O((V + E) log V) | O(V) | Sí (costos > 0) | Sí en costo |
V = celdas transitables (× 2 en `ProblemaMision`), E ≤ 4V. En términos de árbol: BFS O(b^d), UCS O(b^(1+⌊C*/ε⌋)).

## 6. Criterios de aceptación
- **CA-003-1** En el ejemplo del enunciado, BFS desde A1 (0,1) a (3,2) encuentra camino válido de longitud mínima (verificado por spec 006). → `test_busqueda_no_informada.py::test_bfs_ejemplo`
- **CA-003-2** **Caso 1:** en `caso01_bfs_vs_dfs.json` ambos encuentran solución con `orden_expansion` distinto. → `test_casos.py::test_caso01`
- **CA-003-3** **Caso 2:** en `caso02_ruta_corta_vs_economica.json`, `len(BFS) < len(UCS)` y `costo(UCS) < costo(BFS)`. → `test_casos.py::test_caso02`
- **CA-003-4** UCS coincide en costo con un Dijkstra de referencia en 20 mapas pseudoaleatorios con semilla fija. → `test_busqueda_costo.py::test_ucs_optimo`
- **CA-003-5** Objetivo inalcanzable ⇒ `exito=False`, `camino=[]`, métricas presentes. → `test_busqueda_no_informada.py::test_sin_ruta`
- **CA-003-6** Inicio == objetivo ⇒ `exito=True`, `longitud=0`, `costo=0`, `expandidos=0`. → `test_..._trivial`
- **CA-003-7** Cambiar `orden_movimientos` cambia el camino de DFS en el caso 1 y no cambia la longitud de BFS. → `test_..._orden_movimientos`
- **CA-003-8** `to_dict()` contiene exactamente las claves del enunciado (+ extras documentados). → `test_resultado.py::test_formato`
- **CA-003-9** Los tres algoritmos funcionan sobre `ProblemaMision` (la unidad recoge y entrega). → `test_..._mision`

## 7. Tareas
- [ ] T1 `ResultadoBusqueda` + `ContadorMetricas` — Juan
- [ ] T2 `bfs`, `dfs` con docstrings completos — Juan
- [ ] T3 `costo_uniforme` con eliminación perezosa — Juan
- [ ] T4 Escenarios `caso01` y `caso02` (≥ 20×20) con su `esperado` — Juan
- [ ] T5 Tests CA‑003‑1…9 — Juan
- [ ] T6 Revisión y simulacro — Daniel

## 8. Para sustentar
- *¿Por qué BFS encuentra el camino más corto en movimientos pero no el más barato?* → Explora por niveles (número de aristas), ignora costos.
- *¿Por qué UCS revisa `g != mejor_g[s]`?* → `heapq` no permite disminuir prioridad; se re‑inserta y se descartan entradas viejas (eliminación perezosa).
- *¿Qué cambia si el pantano pasa de 7 a 15?* → BFS: nada (no usa costos). UCS: puede desviarse más para evitar el pantano; su costo óptimo nunca baja.
- *¿Por qué DFS cambia con el orden de movimientos?* → La pila hace que el último sucesor insertado se explore primero.
