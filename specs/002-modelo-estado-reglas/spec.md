# 002 — Modelo de estado, acciones y reglas del juego

| Campo | Valor |
|---|---|
| Estado | **implementada y corregida el 20 oct** · pruebas automáticas realizadas · revisión humana de correcciones por realizar |
| Responsable | Daniel · Revisor: Juan |
| Rúbrica | Modelado del problema y representación de estados (15 %) |
| Depende de | 001 |
| Fuente en el enunciado | "Bandos, unidades y turnos", "Objetivo de la partida", "Modelado del problema y del estado" (p. 3); caso mínimo 6 |

## 1. Contexto y porqué
"El modelado es parte central del proyecto." Antes de los algoritmos hay que fijar **qué información define completamente una situación** y **qué acciones** pasan de un estado a otro. Hay **dos familias de problemas** que comparten escenario pero no estado:

| Problema | Usado por | Estado |
|---|---|---|
| Navegación simple | BFS, DFS, UCS, A\*, Beam (`prueba.modo = busqueda`) | `(fila, columna)` |
| Misión del recurso (recoger y entregar) | Los mismos algoritmos; demuestra el **caso 6** | `(fila, columna, lleva_recurso)` |
| Partida adversarial | Minimax, alfa‑beta, modo `partida` | `EstadoJuego` (abajo) |

**Separación clave:** lo que **no cambia** durante la partida (terreno, costos, bases, identidad/bando/tipo de las unidades) vive en `Escenario`. Lo que **sí cambia** vive en el estado. Así el estado es pequeño, hashable y suficiente.

## 2. Requisitos
- **RF-002-1** Identificar inequívocamente: estado inicial, acciones válidas, estados sucesores, condición objetivo/terminal y costo de las acciones.
- **RF-002-2** Ambos bandos operan bajo **las mismas reglas** (MAX/MIN son roles, no capacidades distintas).
- **RF-002-3** Por turno, un bando elige **una** unidad y ejecuta **una** acción válida. Sin simultaneidad ni tiempo real.
- **RF-002-4** Reglas **deterministas** para: bloqueos, imposibilidad de continuar, ausencia de ruta, pérdida del portador.
- **RF-002-5** ≥ 3 unidades por bando en los escenarios propios (el validador no lo exige para no rechazar escenarios externos de prueba como el 4×4 del enunciado, que tiene 2).
- **RF-002-6** Las acciones generadas son legales y los estados sucesores válidos (lo comprueba spec 006).

## 3. Decisiones de diseño (detalle y alternativas en `docs/DECISIONES.md`)

### 3.1 Estado de la partida — `EstadoJuego`  (`Pos` = tupla `(fila, columna)`)
```python
@dataclass(frozen=True)
class EstadoJuego:
    posiciones: tuple[Pos, ...]   # alineado con escenario.unidades (mismo orden del JSON)
    portador: str | None               # id de la unidad que lleva el recurso, o None
    recurso: Pos | None           # posición del recurso si está libre; None si alguien lo porta
    turno: str                         # "A" o "B": bando que debe actuar
    turnos_jugados: int                # para la regla de empate por límite de turnos
```
**Por qué es suficiente:** con el escenario (estático) + estos 5 campos se pueden calcular las acciones legales, el sucesor de cada acción, si el estado es terminal y quién ganó. **Por qué cada campo es necesario:**
- `posiciones`: sin ellas no se sabe a dónde puede moverse cada unidad ni quién bloquea a quién.
- `portador` / `recurso`: *misma posición física, estado distinto* (caso 6) — una unidad en (5,5) con el recurso puede ganar al entrar a su base; sin él, no.
- `turno`: el mismo tablero con turno de A o de B tiene acciones legales (y valor Minimax) distintos.
- `turnos_jugados`: el mismo tablero en el turno 10 o en el turno `max_turnos` difiere en si es terminal (empate).

### 3.2 Acciones
```python
class Accion(NamedTuple):
    tipo: str                 # "MOVER" | "INTERCEPTAR" | "PASAR"
    unidad: str | None = None # id de la unidad que actúa (None en PASAR)
    destino: Pos | None = None  # solo MOVER
# INTERCEPTAR no necesita "objetivo": solo puede haber un portador enemigo.
```

### 3.3 Reglas (deterministas)
| # | Regla |
|---|---|
| R1 | **Turno:** actúa el bando `estado.turno`; elige una unidad propia y una acción. Después, `turno` alterna y `turnos_jugados += 1`. |
| R2 | **MOVER:** la unidad pasa a una celda 4‑vecina que esté dentro del mapa, sea transitable y **no esté ocupada** por otra unidad (de cualquier bando). Costo = `costo(destino)`. |
| R3 | **Base enemiga:** ninguna unidad puede **entrar** a la base del bando contrario (evita la estrategia degenerada de "estacionarse" en la base rival y bloquear el juego para siempre). |
| R4 | **Recoger:** si una unidad entra a la celda del recurso libre, lo recoge automáticamente (`portador = id`, `recurso = None`). |
| R5 | **INTERCEPTAR:** una unidad **adyacente** (4‑vecindad) al portador **enemigo** le hace **perder** el recurso: el recurso vuelve **libre a su posición inicial** del JSON y el antiguo portador **vuelve a su posición inicial** (si está ocupada, se queda donde está). Nadie se queda con el recurso. Costo 0. Esta es la regla de *pérdida del portador*. *(Historia: la versión del 17 oct pasaba el recurso al interceptor y producía un ciclo infinito — 166 intercepciones en 200 turnos; el 18 oct se agregó el regreso del portador; el 20 oct, por propuesta de Daniel, también el recurso vuelve a su sitio.)* |
| R6 | **Entrega / victoria:** tras aplicar cualquier acción, si el portador está en la base de **su** bando, ese bando gana (estado terminal). |
| R7 | **Bloqueo total:** si el bando en turno no tiene ninguna acción MOVER ni INTERCEPTAR legal, su única acción es **PASAR** (costo 0). |
| R8 | **Empate:** si `turnos_jugados ≥ max_turnos` (por defecto 200; configurable en `juego.max_turnos`), el estado es terminal con empate. (Si nadie puede moverse, ambos bandos pasan hasta llegar al límite: no hace falta otra regla ni otro campo en el estado.) |
| R9 | **Sin ruta** (modo búsqueda): el algoritmo termina con `exito = false`, camino vacío y métricas completas; no es un error. |
| R10 | **Orden de generación:** unidades del bando en el orden del JSON; para cada unidad, primero INTERCEPTAR (si aplica) y luego MOVER en `orden_movimientos` (por defecto `abajo, arriba, derecha, izquierda`, el mismo de los notebooks de clase). El orden global se puede alterar con `juego.orden_acciones ∈ {natural, inverso, heuristico}` (spec 005). |

*Alternativas consideradas:* soltar el recurso al ser interceptado (queda en la celda del portador); acción ESPERAR siempre disponible (aumenta la ramificación en +1 por turno); unidades con tipos distintos (explorador más rápido). Se descartan para el MVP por complejidad; se documentan como posibles extensiones.

### 3.4 Problemas de búsqueda (modo `busqueda`)
```python
# Interfaz que usan todos los algoritmos (tacticalgrid/busqueda/problema.py)
problema.inicio            # estado inicial
problema.es_objetivo(s)    # prueba de objetivo
problema.sucesores(s)      # [(estado_siguiente, costo), ...] en orden determinista
```
- `ProblemaNavegacion(escenario, inicio, objetivo, orden=ORDEN_MOVIMIENTOS, bloqueadas=())` — estado `Pos`.
- `ProblemaMision(escenario, id_unidad, orden=ORDEN_MOVIMIENTOS, bloqueadas=())` — estado `(Pos, lleva: bool)`; objetivo `(base_propia, True)`; al entrar a la celda del recurso `lleva` pasa a `True`.
- **D-05:** en modo búsqueda las demás unidades se **ignoran** ("se ignorará temporalmente el comportamiento del adversario"). Con `prueba.unidades_bloquean: true` sus celdas se tratan como obstáculos.
- Costo de un camino = Σ costo de **entrar** a cada celda después de la inicial.

### 3.5 Funciones (`tacticalgrid/juego/estado.py` y `tacticalgrid/juego/reglas.py`)
```python
estado_inicial(escenario) -> EstadoJuego                 # estado.py
acciones_legales(escenario, estado, orden=...) -> list[Accion]
aplicar(escenario, estado, accion) -> EstadoJuego        # lanza ValueError si no es legal
costo_accion(escenario, accion) -> float                 # costo(destino) al MOVER; 0 en otro caso
es_terminal(escenario, estado) -> bool
ganador(escenario, estado) -> str | None                 # "A", "B" o None (empate / no terminal)
validar_estado(escenario, estado) -> list[str]           # invariantes (usado por spec 006)
```
**Invariantes de un `EstadoJuego` válido:** todas las unidades dentro del mapa y en celdas transitables; no hay dos unidades en la misma celda; `(portador is None) == (recurso is not None)`; si hay portador, existe; `turno ∈ {A, B}`; `turnos_jugados ≥ 0`.

## 4. Criterios de aceptación
- **CA-002-1** El estado inicial del ejemplo del enunciado tiene turno A, sin portador, recurso en (2,2). → `tests/test_reglas.py::test_estado_inicial`
- **CA-002-2** **Caso 6:** `((2, 2), False)` y `((2, 2), True)` son estados distintos (distinto hash, distinto conjunto de objetivo) y `EstadoJuego` con la misma unidad en la misma celda, con y sin recurso, tiene acciones o valor distintos. → `tests/test_reglas.py::test_estado_compuesto`
- **CA-002-3** MOVER nunca lleva a obstáculo, fuera del mapa, celda ocupada ni base enemiga. → `tests/test_reglas.py::test_mover_restricciones`
- **CA-002-4** Entrar al recurso lo recoge; entrar a la base propia con él gana. → `tests/test_reglas.py::test_recoger_y_entregar`
- **CA-002-5** INTERCEPTAR solo es legal si hay adyacencia con el portador enemigo y deja el recurso libre en su posición inicial. → `tests/test_reglas.py::test_interceptar`
- **CA-002-6** Bando sin movimientos ⇒ única acción PASAR; límite de turnos ⇒ empate. → `tests/test_reglas.py::test_bloqueo_y_empate`
- **CA-002-7** `acciones_legales` es determinista y respeta el orden configurado. → `tests/test_reglas.py::test_orden_determinista`
- **CA-002-8** Para todo estado alcanzado en 300 partidas aleatorias de 30 jugadas (semilla 0), `validar_estado` no reporta errores (prueba de propiedad). → `tests/test_reglas.py::test_invariantes_alcanzables`
- **CA-002-9** Las reglas son simétricas: intercambiar los bandos de un escenario produce acciones espejo. → `tests/test_reglas.py::test_simetria_bandos`

## 5. Tareas
- [x] T1 `EstadoJuego`, `Accion` y `estado_inicial` — implementado con Claude; revisa Daniel
- [x] T2 `acciones_legales` + `aplicar` (R1–R7, R10) — implementado con Claude; revisa Daniel
- [x] T3 `es_terminal`, `ganador`, empate (R8) — implementado con Claude; revisa Daniel
- [x] T4 `ProblemaNavegacion` y `ProblemaMision` — implementado con Claude; revisa Daniel
- [x] T5 `validar_estado` (invariantes) — implementado con Claude; revisa Daniel
- [x] T6 Tests CA‑002‑1…9 — implementado con Claude; revisa Daniel
- [x] T7 Sección "Modelado" del documento técnico — en docs/DOCUMENTO_TECNICO.md (20 oct)

## Correcciones de auditoría (20 oct 2026)

Los estados verifican recurso dentro del mapa y en su posición libre original, y turnos enteros no negativos. Un estado terminal no tiene acciones. La misión de una unidad solo se admite si el recurso está libre o lo lleva esa unidad; no crea un segundo recurso. La navegación sigue siendo una abstracción que ignora al adversario. La regla de intercepción no garantiza ausencia de repeticiones físicas; el límite de turnos garantiza terminación.

Criterio de aceptación: regresiones en `tests/test_auditoria.py` y `tests/test_interfaz.py`, suite completa y diez casos mínimos aprobados.
