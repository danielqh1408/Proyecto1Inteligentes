# Registro de decisiones (ADR ligero)

> Cada decisión abierta del enunciado se resuelve aquí con **contexto → decisión → alternativas → consecuencias**. Estado: `propuesta` (falta acordar en equipo) · `aceptada` · `reemplazada`.
> Cambiar una decisión `aceptada` requiere actualizar las specs afectadas en el mismo commit.

| ID | Decisión | Estado |
|---|---|---|
| D‑01 | Bandos `a/b` se normalizan a `A/B` | **aceptada** (18 oct) |
| D‑02 | Solo las 9 validaciones del PDF + unidades superpuestas (sin advertencias extra) | **aceptada** (18 oct) |
| D‑03 | Si hay portador, el recurso está donde está el portador | **aceptada** (18 oct) |
| D‑04 | Campos opcionales con valores por defecto en `config.py` | **aceptada** (18 oct) |
| D‑05 | En modo búsqueda las otras unidades se ignoran (opción para bloquear) | **aceptada** (18 oct) |
| D‑06 | Heurísticas: `manhattan`·c_min y `obstaculos` (BFS inverso)·c_min | **aceptada** (18 oct) |
| D‑07 | Beam por niveles, criterio h, visitados global (como en clase) | **aceptada** (18 oct) |
| D‑08 | MAX = bando en turno en la raíz; evaluación de suma cero simétrica | **aceptada** (18 oct) |
| D‑09 | Utilidad: 20·posesión + 3·carrera + 0.1·movilidad, con pesos configurables | **aceptada** (Daniel, 20 oct; posesión bajó de 50 a 20) |
| D‑10 | GUI con tkinter | **aceptada** (18 oct) |
| D‑11 | Unidades idénticas (`estandar`) en el MVP | **aceptada** (18 oct) |
| D‑12 | Python 3.12, núcleo solo stdlib, pytest | **aceptada** (18 oct) |
| D‑13 | Prueba de objetivo al extraer de la frontera en todos los algoritmos | **aceptada** (18 oct) |
| D‑14 | Interceptar devuelve el recurso y al antiguo portador a sus posiciones iniciales; no se entra a la base enemiga | **aceptada** (propuesta de Daniel, 20 oct) |

---

### D‑01 · Normalización de bandos
**Contexto:** la sección de validación dice "a o b"; el ejemplo usa `"A"`. **Decisión:** aceptar ambas y normalizar a mayúscula. **Consecuencia:** un JSON con minúsculas del profesor no se rechaza.

### D‑02 · Qué se valida
**Contexto:** el enunciado lista 9 validaciones; hay otras situaciones raras (base sobre muro, recurso sobre base, mapa < 20×20). **Decisión:** se validan solo las 9 del enunciado, los tipos de dato y que dos unidades no compartan celda (rompería el modelo de estado). Lo demás no se revisa. **Alternativas:** advertencias extra (descartado por la regla de simplicidad: más código sin valor en la nota) o ser más estrictos (riesgo de rechazar un JSON válido del profesor).

### D‑03 · Recurso con portador
**Decisión:** si `juego.portador_recurso` ≠ null, el recurso está en la posición de esa unidad; `recurso` se conserva como dato original. **Consecuencia:** el estado nunca tiene recurso "en dos lugares".

### D‑04 · Valores por defecto
`profundidad_maxima_minimax = 3`, `max_turnos = 200`, `orden_movimientos = [abajo, arriba, derecha, izquierda]` (orden de los notebooks), `orden_acciones = natural`, pesos de utilidad de spec 005. Todos sobreescribibles por JSON/CLI/GUI. Viven solo en `config.py`.

### D‑05 · Otras unidades en modo búsqueda
**Contexto:** "En una primera etapa se ignorará temporalmente el comportamiento del adversario." **Decisión:** las otras unidades no bloquean por defecto; `prueba.unidades_bloquean: true` las convierte en obstáculos. **Consecuencia:** el objetivo puede coincidir con una celda ocupada sin que la búsqueda falle.

### D‑06 · Heurísticas
**Decisión:** H1 = c_min·Manhattan; H2 = c_min·(pasos BFS desde el objetivo respetando obstáculos). **Por qué H2:** es admisible y consistente (problema relajado), domina a H1, es barata (un BFS de precálculo), y responde directo al caso 3 (muro entre la unidad y el objetivo). **Alternativas descartadas:** Euclidiana (dominada por Manhattan en 4‑vecindad); Dijkstra exacto (heurística perfecta pero cuesta lo mismo que resolver); "costo promedio·Manhattan" (no admisible — se conserva solo como H3 experimental). **Consecuencia:** hay que explicar por qué se multiplica por c_min.

### D‑07 · Beam Search
**Decisión:** igual al notebook (niveles, `visitados` global, ordena por h) con opción `criterio=f`. **Por qué:** coherencia con clase y deja visible el efecto pedido (descartar caminos buenos). **Consecuencia:** Beam puede fallar aunque exista ruta; se reporta `descartados`.

### D‑08 · MAX/MIN
**Decisión:** MAX = bando en turno en la raíz. Evaluación simétrica `E_A = −E_B`. **Consecuencia:** el mismo código decide por A o por B; argumento directo de que MIN no está en desventaja.

### D‑09 · Función de utilidad
**Decisión:** terminal ±(10 000 − profundidad), 0 empate; no terminal = 20·posesión + 3·carrera + 0.1·movilidad, donde carrera = restante(MIN) − restante(MAX) y `restante` es el costo real (Dijkstra) que le falta a cada bando para ganar (spec 005 §4). **Por qué:** cubre los factores que sugiere el enunciado (posesión, distancias, proximidad del adversario, unidades disponibles) y es **monótona**: recoger el recurso nunca empeora el valor. **Historia:** la propuesta inicial de 5 componentes se descartó al implementar porque una unidad junto al recurso prefería no recogerlo. **Ajuste (20 oct):** Daniel consideró alto el peso de posesión (50). Se probó 10, 20 y 50: los 10 casos y el torneo E6 dan el mismo resultado, porque `carrera` ya premia tener el recurso; se dejó en 20. **Consecuencia:** pesos ajustables en vivo desde `juego.pesos_utilidad`.

### D‑10 · Interfaz: tkinter
**Contexto:** se necesita cargar archivos, controles (combos, spinbox), tablas y una cuadrícula; la estética no se evalúa. **Decisión:** `tkinter` + `ttk`. **Alternativas:** Pygame (hay que construir botones, tablas y diálogo de archivos a mano), Streamlit (modelo de recarga incómodo para turnos), web React (otro stack y otra capa de API). **Riesgo:** en macOS con Python de Homebrew falta Tk ⇒ `brew install python-tk@3.12`. **Pendiente:** confirmar que funciona en el equipo de Daniel y en el PC de la sustentación.

### D‑11 · Tipos de unidad
**Decisión:** todas `estandar` (mismo movimiento y reglas). El campo `tipo` se lee y se muestra; un tipo desconocido se trata como `estandar` con advertencia. **Por qué:** el enunciado permite unidades idénticas y pide no complicar con combate. **Extensión posible:** `explorador` con costo de bosque reducido.

### D‑12 · Lenguaje y dependencias
Python 3.12 (igual que el curso), núcleo con stdlib, `pytest` para pruebas, `matplotlib` opcional para gráficas.

### D‑13 · Prueba de objetivo al extraer
Ver spec 003 §3. Necesaria para la optimalidad de UCS/A\* y hace comparables las métricas de los 5 algoritmos.

### D‑14 · Intercepción y base enemiga
**Decisión (aceptada, propuesta de Daniel):** INTERCEPTAR (adyacente al portador enemigo) le hace perder el recurso: el recurso vuelve libre a su posición inicial del JSON y el antiguo portador vuelve a su posición inicial (si está ocupada, se queda). Nadie puede entrar a la base enemiga. **Historia:** (1) la primera versión pasaba el recurso al interceptor: dos unidades vecinas se lo quitaban en cada turno (166 intercepciones en 200 turnos) y todo era empate; (2) se agregó que el portador vuelve a su inicio; (3) Daniel propuso que el recurso también vuelva a su sitio, así interceptar es una jugada defensiva que reinicia la carrera. Con (3) los 10 casos se cumplen, no hay ciclos y en el mapa simétrico el agente con más profundidad gana. **Alternativas:** el recurso cae al suelo donde estaba (añade posiciones posibles del recurso), un turno de inmunidad (añade un campo al estado). **Consecuencia:** el recurso libre SIEMPRE está en su posición inicial ⇒ las distancias al recurso se precalculan una sola vez.
