# 004 — A\*, heurísticas y Beam Search

| Campo | Valor |
|---|---|
| Estado | **implementada** (falta revisión de Daniel y validación de estudiante en docstrings) |
| Responsable | Juan · Revisor: Daniel |
| Rúbrica | A\*, heurísticas y Beam Search (20 %) |
| Depende de | 003 (métricas, resultado, problemas) |
| Fuente en el enunciado | "Búsqueda informada", "Búsqueda con memoria limitada" (p. 4); casos 3, 4 y 5 |
| Base del curso | `a_estrella`, `astar_mapa`, `manhattan`, `beam_search_mapa` del notebook de búsqueda informada |

## 1. Contexto y porqué
Tercera pregunta: *¿puedo usar conocimiento del entorno para explorar menos sin perder la mejor ruta?* (A\*) y *¿qué pierdo si limito la memoria?* (Beam). Se exige **dos heurísticas**: Manhattan y una **propia, justificada**.

## 2. Requisitos
- **RF-004-1** A\* con f(n) = g(n) + h(n), costos del escenario.
- **RF-004-2** Heurística 1: Manhattan. Heurística 2: propuesta por el equipo con: qué estima, qué información usa, costo computacional, admisibilidad (y por qué), dónde orienta bien y dónde pierde discriminación.
- **RF-004-3** Beam Search con k configurable; experimentos con **k = 1, 2, 4, 8** como mínimo.
- **RF-004-4** Analizar si restringir el haz descarta un camino que después habría sido conveniente.
- **RF-004-5** Mismas métricas de la spec 003 §3 (+ extras de Beam).

## 3. Heurísticas (decisión D‑06)

Sea **c_min** = menor costo entre los terrenos transitables **del escenario cargado** (se lee del JSON, no es constante).

### H1 — `manhattan`: h₁(n) = c_min · (|f − f_g| + |c − c_g|)
- **Estima:** costo mínimo restante si no hubiera obstáculos y todo el terreno fuera del tipo más barato.
- **Usa:** posición actual, posición objetivo y c_min.
- **Costo:** O(1) por evaluación.
- **Admisible:** cualquier camino de 4‑vecindad necesita ≥ Manhattan movimientos y cada uno cuesta ≥ c_min. **Consistente:** al moverse a un vecino, h cambia como máximo c_min ≤ costo del paso.
- *Por qué multiplicamos por c_min:* la Manhattan "pura" solo es admisible si c_min ≥ 1. Si el profesor pone `camino: 0.5`, la Manhattan pura **sobreestimaría** y A\* podría perder la optimalidad. Con c_min = 1 (como en el ejemplo) es idéntica a la Manhattan de clase.
- **Pierde discriminación:** cuando hay barreras entre el estado y el objetivo (los estados "pegados" al muro por el lado equivocado parecen muy buenos).

### H2 — `obstaculos` (propia): h₂(n) = c_min · pasos_BFS(n → objetivo) respetando obstáculos
- **Estima:** costo mínimo restante en un **problema relajado** donde se conservan los obstáculos pero todo terreno transitable cuesta c_min.
- **Usa:** el mapa de transitabilidad del escenario, la posición objetivo y c_min. Se precalcula **una vez por objetivo** con un BFS inverso desde el objetivo; luego cada consulta es un acceso a diccionario.
- **Costo:** O(F·C) de precálculo (una sola vez) + O(1) por evaluación. Memoria O(F·C).
- **Admisible:** el costo real de cualquier camino ≥ (número de pasos del camino) · c_min ≥ pasos_BFS · c_min. **Consistente:** pasos_BFS de dos vecinos difieren en ≤ 1.
- **Domina a H1:** pasos_BFS ≥ Manhattan siempre ⇒ h₂ ≥ h₁ ⇒ A\* con H2 expande **≤** estados que con H1 (con desempates iguales) — dominancia vista en clase.
- **Orienta bien:** mapas con muros, laberintos, "trampas" donde el objetivo parece cerca pero hay que rodear (caso 3). Detecta además celdas **sin salida**: si pasos_BFS = ∞, el estado no puede llegar y no se inserta.
- **Pierde discriminación:** mapas abiertos sin obstáculos (h₂ = h₁) y mapas donde la diferencia la hace el **costo del terreno** (pantanos, bosques), porque supone todo a c_min.
- *Por qué no usar Dijkstra exacto como heurística:* sería la heurística perfecta, pero calcularla cuesta lo mismo que resolver el problema con UCS; no aporta como "conocimiento barato".

### Heurísticas para `ProblemaMision` (estado con `lleva_recurso`)
- Si no lleva: h = h(pos → recurso) + h(recurso → base) (el segundo término es constante y se precalcula).
- Si lleva: h = h(pos → base).
Ambas siguen siendo admisibles y consistentes (se explica en el documento técnico).

### H3 opcional — `manhattan_promedio` (NO admisible, solo para experimentar)
c_promedio · Manhattan. Sirve para mostrar, como en el notebook ("Caso 3 — Heurística que sobreestima"), que A\* puede devolver un camino **no óptimo** expandiendo menos.

## 4. Beam Search (decisión D‑07)
Como en clase: búsqueda **por niveles**. En cada nivel se expanden todos los estados del haz, se juntan los sucesores nuevos y se conservan los **k mejores** según h(n) (criterio por defecto `h`, "beam voraz"); opción `criterio="f"` usa g + h.
- Prueba de objetivo al sacar del haz (igual que los demás).
- `visitados` **global** (como en clase): un estado descartado por el corte queda marcado y no se vuelve a generar ⇒ Beam **no es completo ni óptimo**. Es exactamente lo que el enunciado pide analizar.
- Desempate determinista: (valor, contador de generación).
- Extras en el resultado: `k`, `criterio`, `descartados` (candidatos eliminados por el corte), `maximo_haz`.
- `maximo_frontera` en Beam = máximo de candidatos simultáneos **antes** del corte (memoria realmente usada en el nivel).

## 5. Diseño

> **Implementado:** `a_estrella` y `beam_search` en `busqueda/algoritmos.py`; `manhattan`, `obstaculos`, `manhattan_promedio` y `crear_heuristica` en `busqueda/heuristicas.py`. Evidencia: caso 3 (H2 expande 177 vs 282 de H1, mismo costo 32), caso 5 (Beam k=1 falla, k≥2 encuentra), caso 2 (H3 da costo 83 vs óptimo 33 → no admisible).
```
tacticalgrid/busqueda/
├── heuristicas.py   # crear_heuristica(nombre, escenario, problema) -> Callable[[estado], float]
│                    # registro: {"cero", "manhattan", "obstaculos", "manhattan_promedio"}
├── a_estrella.py    # a_estrella(problema, heuristica) -> ResultadoBusqueda
└── beam.py          # beam_search(problema, heuristica, k, criterio="h") -> ResultadoBusqueda
```
A\* = UCS con prioridad (f, g, tie). Con `heuristica="cero"`, A\* debe dar **exactamente** el mismo costo que UCS (prueba de cordura).

## 6. Criterios de aceptación
- **CA-004-1** A\* con H1 y con H2 obtiene el **mismo costo** que UCS en todos los casos y en 20 mapas aleatorios con semilla. → `test_a_estrella.py::test_optimo_igual_ucs`
- **CA-004-2** A\* con `cero` ≡ UCS (mismo costo; expandidos iguales salvo desempates). → `test_a_estrella.py::test_h_cero`
- **CA-004-3** Admisibilidad empírica: para todo estado de los mapas de prueba, h₁ ≤ h₂ ≤ h\* (h\* por Dijkstra inverso). → `test_heuristicas.py::test_admisible_y_dominancia`
- **CA-004-4** Consistencia: h(n) ≤ c(n,n') + h(n') para todo par vecino. → `test_heuristicas.py::test_consistente`
- **CA-004-5** **Caso 3:** en `caso03_obstaculo_heuristica.json`, `expandidos(H2) < expandidos(H1)`. → `test_casos.py::test_caso03`
- **CA-004-6** **Caso 4:** ambas heurísticas sobre el mismo escenario quedan en la tabla comparativa. → `test_casos.py::test_caso04`
- **CA-004-7** **Caso 5:** en `caso05_beam.json`, al variar k ∈ {1,2,4,8} cambian `estados_expandidos` y, al menos para un k, cambia el camino o `exito`. → `test_casos.py::test_caso05`
- **CA-004-8** Con `c_min = 0.5` en el JSON, H1 sigue siendo admisible. → `test_heuristicas.py::test_cmin_fraccionario`
- **CA-004-9** H3 (`manhattan_promedio`) produce al menos un caso con costo > óptimo (evidencia de no admisibilidad). → `test_heuristicas.py::test_h3_no_admisible`

## 7. Tareas
- [x] T1 `heuristicas.py` (cero, manhattan, obstaculos, manhattan_promedio) + versiones para misión — implementado con Claude; revisa el otro integrante
- [x] T2 `a_estrella` — implementado con Claude; revisa el otro integrante
- [x] T3 `beam_search` con extras — implementado con Claude; revisa el otro integrante
- [x] T4 Escenarios `caso03`, `caso04`, `caso05` — implementado con Claude; revisa el otro integrante
- [x] T5 Tests CA‑004‑1…9 — implementado con Claude; revisa el otro integrante
- [ ] T6 Sección "Heurísticas" del documento técnico (las 5 preguntas del enunciado por heurística) — Juan
- [ ] T7 Revisión y simulacro — Daniel

## 8. Para sustentar
- *¿Su heurística es admisible? Demuéstrelo.* → Relajación del problema (§3, H2).
- *¿Qué pasa con su heurística si el pantano cuesta 15?* → No cambia (usa c_min); sigue admisible pero discrimina menos; A\* expandirá más en zonas de pantano.
- *¿Y si el camino cuesta 0.5?* → c_min = 0.5, ambas heurísticas se escalan y siguen admisibles.
- *¿Por qué Beam con k=1 falla aquí?* → El corte descartó el único sucesor que llevaba al pasillo; con visitados global ya no se recupera.
- *Prediga: ¿A\* con H2 expande más o menos que con H1 en un mapa sin muros?* → Igual (h₂ = h₁).
