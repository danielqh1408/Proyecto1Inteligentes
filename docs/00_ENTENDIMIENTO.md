# 00 — Entendimiento del proyecto

> Documento para **aprender y explicar**. Resume el enunciado (`Primer proyecto.pdf`), lo conecta con lo visto en clase (notebooks del primer corte) y traza cada requisito hasta la spec, el módulo y el criterio de la rúbrica.

## 1. La idea en 30 segundos

Un tablero de al menos 20×20 con terrenos de distinto costo (camino, pasto, bosque, pantano…) y obstáculos. Dos bandos, A y B, con ≥ 3 unidades cada uno, juegan **por turnos**: en cada turno un bando mueve **una** unidad. En el centro hay un **recurso**; gana quien lo lleve a **su** base.

Sobre ese mismo mundo hacemos cuatro preguntas cada vez más difíciles:

```
¿Hay una ruta?        →  BFS, DFS                  (búsqueda no informada)
¿Cuál es la más barata? →  UCS                      (costo acumulado g(n))
¿Puedo buscar menos?   →  A* (h1, h2), Beam (k)     (conocimiento heurístico h(n))
¿Y si el otro también piensa? → Minimax, alfa-beta  (decisión adversarial)
```

Eso es exactamente la **pregunta central**: *¿cómo cambia la forma de decidir de un sistema inteligente cuando pasa de encontrar una ruta, a optimizar su costo, a usar conocimiento heurístico y a actuar frente a un adversario?*

## 2. Qué ya sabemos (del primer corte) y qué es nuevo

| Visto en clase (notebooks) | En el proyecto cambia… |
|---|---|
| `bfs`/`dfs` sobre laberinto 0/1 con `deque`/pila y `visitados` | …el mapa viene de un **JSON**, las celdas tienen **costos**, y hay que medir **generados, expandidos, frontera máxima y tiempo** |
| `costo_uniforme` con `heapq`, `count()` y `mejor_g` | …los costos son del terreno y deben salir del JSON (pantano 7 → 15 en vivo) |
| `a_estrella` con Manhattan; heurística que sobreestima | …hay que **proponer y defender una segunda heurística** (admisibilidad, costo, dónde falla) |
| `beam_search_mapa` con k = 1, 2, 3, 5, 10 | …k = 1, 2, 4, 8 y **mostrar que el corte puede descartar un buen camino** |
| `minimax` en árboles fijos, piedras y Tres en Raya | …**profundidad limitada** + **función de evaluación propia** en un juego con varias unidades |
| `alfa_beta` y *move ordering* | …contar **nodos podados**, comprobar **misma decisión** y medir el efecto del **orden** |
| Estado = `(fila, columna)` o tupla del tablero | …el estado debe incluir **quién lleva el recurso, el turno**, etc. (dos estados con la unidad en la misma casilla pueden ser distintos) |

## 3. Lo que el profesor va a hacer en la sustentación (y cómo nos preparamos)

| El profesor podrá… | Nuestra respuesta de diseño |
|---|---|
| Traer un JSON **nunca visto** | Carga genérica + validación completa (spec 001); cero supuestos (constitución P1, P3) |
| Cambiar costos (pantano 7 → 15) y pedir **predicción** | Costos solo desde el JSON; escenario de sensibilidad ensayado (spec 008, E3) |
| Mover obstáculos, bases, unidades, recurso; cambiar el objetivo | Todo sale del JSON / clic en la GUI |
| Cambiar la profundidad de Minimax | `juego.profundidad_maxima_minimax`, `--profundidad`, control en la GUI |
| Cambiar el orden de generación de acciones | `juego.orden_acciones` / `prueba.orden_movimientos` / GUI |
| Pedir otro algoritmo sobre el mismo escenario | Tabla comparativa acumulada en la GUI |
| Escoger un método al azar y pedir una **modificación pequeña** | Código corto, documentado y que ambos entendemos (P10); ensayos en `GUIA_SUSTENTACION.md` |
| Preguntar individualmente cualquier parte | Revisión cruzada obligatoria + simulacros con el examinador |

## 4. Decisiones abiertas que el enunciado nos deja (y dónde las resolvimos)

| Decisión abierta | Resolución | Dónde |
|---|---|---|
| Estructura interna del software | 4 capas + verificación + experimentos | `ARQUITECTURA.md` |
| Representación interna del estado | `EstadoJuego` (5 campos) y estados de navegación | spec 002 |
| Reglas para bloqueos, sin ruta, pérdida del portador | R1–R10 | spec 002 §3.3 |
| Tipos de unidades | Todas `estandar` (MVP); tipos extensibles | `DECISIONES.md` D‑11 |
| Segunda heurística | `obstaculos`: BFS inverso escalado por c_min | spec 004 §3 |
| Función de utilidad | 3 componentes: posesión, carrera y movilidad + terminal | spec 005 §4 |
| Lenguaje e interfaz | Python 3.12 + tkinter | `DECISIONES.md` D‑10, D‑12 |

## 5. Matriz de trazabilidad (requisito → spec → módulo → prueba → rúbrica)

| Requisito del enunciado | Spec | Módulo | Prueba / evidencia | Rúbrica |
|---|---|---|---|---|
| Cargar formato JSON común sin cambiar código | 001 | `escenario/cargador.py` | `test_escenario.py` | Validación 5 % |
| Validar (9 reglas) y rechazar sin estado parcial | 001 | `escenario/validador.py` | `test_validador.py`, `escenarios/invalidos/` | Validación 5 % |
| Mapas ≥ 20×20 y otras dimensiones | 001 / 008 | `escenario/modelo.py` | casos 1–10 (≥ 20×20), ejemplo 4×4 | Modelado 15 % |
| Costos del JSON, no constantes | 001 / 003 | `Escenario.costo` | `test_costos_desde_json`, E3 | BFS/DFS/UCS 15 % |
| Estado inicial, acciones, sucesores, objetivo, costo | 002 | `juego/`, `busqueda/problema.py` | `test_reglas.py` | Modelado 15 % |
| Mismas reglas para ambos bandos | 002 / 005 | `juego/reglas.py`, `adversarial/utilidad.py` | `test_simetria_bandos`, `test_suma_cero` | Modelado / Minimax |
| Reglas deterministas (bloqueo, sin ruta, pérdida del portador) | 002 | `juego/reglas.py` | `test_bloqueo_y_empate`, `test_interceptar` | Modelado 15 % |
| BFS y DFS con métricas | 003 | `busqueda/algoritmos.py` | caso 1 | BFS/DFS/UCS 15 % |
| UCS; BFS ≠ UCS en un escenario | 003 | `busqueda/algoritmos.py` | caso 2 | BFS/DFS/UCS 15 % |
| A\* con 2 heurísticas justificadas | 004 | `busqueda/algoritmos.py`, `heuristicas.py` | casos 3, 4; `test_busqueda.py` | A\*/Beam 20 % |
| Beam k = 1, 2, 4, 8 + análisis | 004 / 008 | `busqueda/algoritmos.py` | caso 5, E2 | A\*/Beam 20 % |
| Minimax y αβ con profundidad configurable | 005 | `adversarial/minimax.py` | casos 8, 10 | Minimax 20 % |
| Utilidad propia explicable | 005 | `adversarial/utilidad.py` | caso 7, `test_adversarial.py` | Minimax 20 % |
| Misma decisión MM vs αβ; efecto del orden | 005 | `adversarial/minimax.py` | casos 8, 9 | Minimax 20 % |
| Métricas comparables en la interfaz | 003 / 005 / 007 | `resultado.py`, `interfaz/` | tabla de métricas | Experimentación 10 % |
| Visualización mínima y explorados (sin dibujo de frontera) | 007 | `interfaz/app.py` | capturas en manual | Interfaz 5 % |
| Verificación de soluciones | 006 | `verificacion/verificador.py` | `test_verificador.py` | Validación 5 % |
| 10 casos mínimos reproducibles | 008 | `experimentos/` | `test_casos.py`, `resultados/RESUMEN.md` | Experimentación 10 % |
| Documentación de métodos (7 campos) | 009 | todo el paquete | `test_documentacion.py` | Calidad/doc 10 % |
| Declaración del uso de IA | 009 | docstrings + `docs/USO_IA.md` | auditoría | Calidad/doc 10 % |
| Entregables (README, manual, doc técnico, evidencia) | 009 | `docs/`, `resultados/` | checklist spec 009 | Grupal |

## 6. Evaluación (para priorizar)

50 % grupal (producto) + 50 % **individual** (sustentación). La nota individual puede bajar la final si hay diferencia entre lo que hace el producto y lo que el estudiante domina.

| Componente grupal | % | Specs |
|---|---|---|
| Modelado y representación de estados | 15 | 002 (+001) |
| BFS, DFS y UCS | 15 | 003 |
| A\*, heurísticas y Beam | 20 | 004 |
| Minimax y alfa‑beta | 20 | 005 |
| Experimentación, métricas e interpretación | 10 | 008 |
| Interfaz y visualización | 5 | 007 |
| Validación de escenarios y soluciones | 5 | 001, 006 |
| Calidad y documentación técnica | 10 | 009 |

**Lectura estratégica:** el 55 % grupal está en *modelado + A\*/Beam + Minimax*. La GUI vale 5 %: debe ser **funcional y clara**, no bonita.

## 7. Glosario rápido (para explicar con nuestras palabras)

- **Estado:** toda la información que cambia y que hace falta para decidir.
- **Frontera:** estados generados que aún no se han expandido.
- **Generar / expandir:** generar = meter en la frontera; expandir = sacar y calcular sus sucesores.
- **g(n):** costo real acumulado. **h(n):** estimación del costo restante. **f(n) = g + h.**
- **Admisible:** h(n) ≤ h\*(n) siempre. **Consistente:** h(n) ≤ c(n, n') + h(n').
- **Dominancia:** h₂ ≥ h₁ con ambas admisibles: h₂ informa más; las expansiones totales también dependen de los empates en f = C*.
- **Beam width k:** cuántos estados se conservan por nivel.
- **Utilidad / evaluación:** número que dice qué tan bueno es un estado para MAX.
- **Poda α‑β:** dejar de explorar una rama cuando ya no puede cambiar la decisión de la raíz (α ≥ β).
- **Horizonte:** lo que queda más allá de la profundidad máxima; la evaluación lo estima.
