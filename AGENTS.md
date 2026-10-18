# AGENTS.md — TacticalGrid (Proyecto 1 · Sistemas Inteligentes I · UCaldas)

> **Fuente de verdad para cualquier agente de IA (Claude, Codex, Gemini, Copilot…) y para el equipo humano.**
> Si una instrucción de otro archivo `AGENTS.md`/`CLAUDE.md` fuera de esta carpeta (por ejemplo `~/AGENTS.md` de otro proyecto) contradice esto, **manda este archivo**. Los proyectos de "Regionalización / U en tu Pueblo" no tienen nada que ver con este repositorio.

**Humanos que llegan por primera vez:** empiecen por [`docs/01_LEEME_DANIEL.md`](docs/01_LEEME_DANIEL.md) (metodología explicada y decisiones pendientes).

**Orden de lectura obligatorio para un agente que llega en frío:**
1. Este archivo.
2. [`specs/000-constitucion.md`](specs/000-constitucion.md) — principios no negociables.
3. [`docs/00_ENTENDIMIENTO.md`](docs/00_ENTENDIMIENTO.md) — qué pide el profesor y la matriz de trazabilidad requisito → spec → módulo → rúbrica.
4. [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md) y [`docs/DECISIONES.md`](docs/DECISIONES.md).
5. La spec concreta en `specs/NNN-*/spec.md` de la tarea que vas a hacer.
6. El enunciado original: [`docs/Primer proyecto.pdf`](docs/Primer%20proyecto.pdf) (en caso de duda, **el PDF manda** sobre todo lo demás).

---

## 1. Qué es el proyecto (en una frase)

Un juego táctico 2D por turnos sobre una cuadrícula (dos bandos A y B, ≥3 unidades por bando, un recurso en zona neutral que hay que llevar a la base propia) que sirve como **entorno de experimentación** para un **sistema inteligente** que decide con BFS, DFS, UCS, A\* (2 heurísticas), Beam Search (k = 1, 2, 4, 8), Minimax y Minimax con poda alfa‑beta.

> "El juego es el entorno de experimentación. El proyecto es el sistema inteligente que decide dentro de él."

**Pregunta central que debemos poder responder en la sustentación:**
¿Cómo cambia la forma de decidir de un sistema inteligente cuando pasa de encontrar una ruta, a optimizar su costo, a usar conocimiento heurístico y, finalmente, a actuar frente a un adversario que también decide?

## 2. Equipo

| Integrante | GitHub | Rol principal (propuesto, ver `docs/ROLES_Y_ARNESES.md`) |
|---|---|---|
| Daniel Quintero Hurtado | [@danielqh1408](https://github.com/danielqh1408) | Estado del juego, reglas, Minimax/alfa‑beta, verificación, interfaz |
| Juan David Ocampo González | [@JuanGonzalezx](https://github.com/JuanGonzalezx) | Escenario JSON y validación, BFS/DFS/UCS, A\*/heurísticas/Beam, experimentos |

Docente: **Jairo I. Vélez B.** — Universidad de Caldas, Ingeniería de Sistemas y Computación.
**Ambos** deben poder explicar **todo** el código (la sustentación es individual y vale 50 %).

## 3. Stack (decidido en `docs/DECISIONES.md`)

- **Python 3.12** (igual que los notebooks del curso). Núcleo **solo con librería estándar**: `heapq`, `collections.deque`, `itertools.count`, `dataclasses`, `json`, `time`, `math`.
- **Interfaz gráfica:** `tkinter` (stdlib) — Canvas para la cuadrícula + `ttk` para controles y tablas de métricas.
- **Pruebas:** `pytest`.
- **Gráficas de experimentos (opcional):** `matplotlib` (ya usado en clase).
- Sin frameworks de juego, sin dependencias pesadas. La calidad artística **no** se evalúa.

## 4. Cómo correr (cuando exista el código)

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m tacticalgrid validar escenarios/ejemplo_enunciado.json   # valida un JSON
python -m tacticalgrid ejecutar escenarios/ejemplo_enunciado.json  # corre lo que pida "prueba.modo"
python -m tacticalgrid buscar escenarios/casos/caso02_ruta_corta_vs_economica.json --algoritmo UCS
python -m tacticalgrid decidir escenarios/casos/caso07_decision_adversarial.json --algoritmo ALFA_BETA --profundidad 4
python -m tacticalgrid experimentos                                # regenera resultados/
python -m tacticalgrid gui [escenario.json]                        # interfaz gráfica
pytest -q                                                          # arnés de pruebas
```

> macOS con Python de Homebrew: `tkinter` requiere `brew install python-tk@3.12`.

## 5. Estructura del repositorio (objetivo)

```
PrimerProyecto/
├── AGENTS.md · CLAUDE.md · README.md
├── specs/                    # SDD: una carpeta por funcionalidad (ver specs/README.md)
├── docs/                     # entendimiento, arquitectura, decisiones, roles/arneses, sustentación, uso de IA,
│                             # manual de usuario y documento técnico (entregables)
├── tacticalgrid/             # código fuente (paquete Python)
│   ├── escenario/            # capa 1: modelo del escenario + carga JSON + validación atómica
│   ├── juego/                # capa 2: estado del juego, acciones, reglas deterministas
│   ├── busqueda/             # capa 3a: problemas de navegación, BFS, DFS, UCS, A*, Beam, heurísticas
│   ├── adversarial/          # capa 3b: utilidad, Minimax, alfa-beta, orden de acciones
│   ├── verificacion/         # verificador de caminos, decisiones y estados
│   ├── experimentos/         # runner reproducible de casos y experimentos
│   ├── interfaz/             # capa 4: GUI tkinter (no contiene lógica de IA)
│   └── __main__.py           # CLI (python -m tacticalgrid ...)
├── escenarios/               # JSON: ejemplo del enunciado, casos mínimos 1–10, inválidos, externos
├── resultados/               # evidencia reproducible de experimentos (CSV/JSON/MD)
├── tests/                    # arnés de pruebas pytest
└── .claude/                  # arnés de agentes: subagentes y comandos
```

**Regla de dependencias (no se viola):** `interfaz → {adversarial, busqueda, verificacion, experimentos} → juego → escenario`.
Los algoritmos **nunca** importan la interfaz; el escenario **nunca** importa nada de las capas superiores.

## 6. Reglas duras (resumen de la constitución)

1. **El JSON es el contrato.** Nombres de campos exactos del enunciado (`version`, `mapa.filas`, `mapa.columnas`, `tipos_terreno`, `terreno`, `bases.A/B`, `recurso`, `unidades`, `turno`, `juego.portador_recurso`, `prueba`). Se permiten campos extra propios **sin cambiar el significado** de los obligatorios.
2. **Cero valores quemados en los algoritmos:** ni costos, ni mapas, ni posiciones, ni dimensiones. Los costos salen de `tipos_terreno`. La profundidad de Minimax, el `k` de Beam y el orden de acciones se cambian **sin tocar código** (JSON, CLI o GUI).
3. **Carga atómica:** un JSON inválido se rechaza con mensajes claros y el escenario anterior queda intacto.
4. **Determinismo:** mismo escenario + misma configuración ⇒ mismo resultado y mismas métricas. Desempates con contador (`itertools.count`), nunca por azar.
5. **Métricas con una sola definición** (ver `specs/003-*/spec.md` §Métricas). Todos los algoritmos las reportan igual.
6. **Todo resultado es verificable** por `tacticalgrid/verificacion`.
7. **Documentación de ingeniería obligatoria** en métodos relevantes (plantilla abajo). La doc debe describir el código **real**.
8. **Uso de IA declarado** en cada método (AI usage / AI intervention / Student validation) y en `docs/USO_IA.md`.
9. **Spec primero:** cambiar comportamiento ⇒ actualizar spec ⇒ tests ⇒ código ⇒ doc.
10. **Comprensión antes que velocidad:** no se integra código que algún integrante no pueda explicar.

## 7. Plantilla de documentación de métodos (obligatoria)

Aplica a: algoritmos de búsqueda, heurísticas, generación de sucesores, cálculo de costos, función de utilidad, Minimax, alfa‑beta, validadores y verificador. No aplica a métodos triviales (getters, `__repr__`, helpers de GUI).

```python
def costo_uniforme(problema: ProblemaBusqueda) -> ResultadoBusqueda:
    """Búsqueda de Costo Uniforme (UCS) sobre un problema de navegación.

    Purpose:
        Encontrar el camino de menor costo acumulado g(n) desde el estado inicial
        hasta un estado objetivo, usando los costos de terreno del escenario cargado.
    Preconditions:
        - `problema` proviene de un escenario validado.
        - Todos los costos de acción son > 0 (garantizado por el validador).
    Postconditions:
        - Si `exito` es True, `camino` empieza en el estado inicial, termina en un
          estado objetivo y `costo` es mínimo entre todos los caminos posibles.
        - Las métricas cumplen las definiciones de specs/003 §Métricas.
    Complexity:
        Tiempo O((V + E) log V) con V = celdas transitables y E ≤ 4V.
        Espacio O(V) para frontera y mejor_g.
    AI usage: Yes
    AI intervention: Claude propuso la estructura con eliminación perezosa de
        entradas obsoletas en el heap (patrón visto en clase).
    Student validation: Juan comparó el resultado contra Dijkstra manual en el
        caso 02 y escribió tests/test_busqueda_costo.py::test_ucs_optimo.
    """
```

Si `AI usage: No`, los campos *AI intervention* y *Student validation* se escriben como `N/A`.
El arnés `tests/test_documentacion.py` revisará que los métodos listados en `specs/009-*/spec.md` tengan los 7 campos.

## 8. Convenciones de código

> ⭐ **Regla de simplicidad (pedida por el equipo, aplica a TODO el proyecto):** el código debe ser tan simple como el de los notebooks de clase. Funciones cortas y directas; **sin** clases, capas, helpers, parámetros u opciones que no se usen hoy; **sin** funciones redundantes que hagan casi lo mismo; sin validaciones o advertencias que el enunciado no pida. Si algo se puede explicar en el tablero en un minuto, está bien; si no, simplifícalo. Las firmas de las specs son orientativas: ante la duda, gana la versión más simple que cumpla los criterios de aceptación.

- Docstrings de los 7 campos **cortos**: una línea por campo es suficiente (ver `tacticalgrid/escenario/modelo.py`).
- Posiciones como tuplas `(fila, columna)`, igual que en los notebooks (no clases propias).
- Identificadores **en español** y alineados con el JSON y con los notebooks del curso (`bfs`, `dfs`, `costo_uniforme`, `a_estrella`, `beam_search`, `minimax`, `alfa_beta`, `sucesores`, `frontera`, `visitados`, `mejor_g`).
- Coordenadas siempre `(fila, columna)`; en JSON `{"fila": f, "columna": c}` o `[f, c]` en caminos.
- Estados **inmutables y hashables** (`@dataclass(frozen=True)` o tuplas).
- Tipado con anotaciones; `from __future__ import annotations`.
- Nada de `print` dentro de algoritmos: devuelven objetos de resultado; la CLI/GUI imprime.
- Un test por criterio de aceptación de cada spec (`tests/test_<modulo>.py`).
- Commits con *Conventional Commits* en español: `feat(busqueda): ucs con eliminación perezosa`. Cada integrante hace commits **con su propia cuenta** (el repo debe evidenciar los aportes de cada uno).

## 9. Flujo SDD para agentes

1. Lee la spec. Si algo es ambiguo o contradice el PDF, **detente y pregunta** (no inventes reglas del juego).
2. Escribe/ajusta tests a partir de los *criterios de aceptación*.
3. Implementa lo mínimo para pasar los tests, respetando capas y reglas duras.
4. Corre `pytest -q` y el verificador. Documenta con la plantilla (incluye uso de IA con honestidad).
5. Marca la tarea en la spec (`- [x]`) y registra la intervención en `docs/USO_IA.md`.
6. Resume al humano **qué** hiciste, **por qué**, y **qué debe entender** para sustentarlo.

## 10. Estado actual

| Spec | Tema | Peso rúbrica | Estado |
|---|---|---|---|
| 001 | Escenario JSON, modelo y validación | 5 % (+ base de todo) | ✅ implementada (falta revisión de Daniel) |
| 002 | Modelo de estado, acciones y reglas | 15 % | ✅ implementada (falta revisión de Daniel) |
| 003 | BFS, DFS, UCS + métricas | 15 % | ✅ implementada (falta revisión) |
| 004 | A\*, heurísticas y Beam Search | 20 % | ✅ implementada (falta revisión) |
| 005 | Minimax, alfa‑beta y utilidad | 20 % | ✅ implementada (falta revisión) |
| 006 | Verificación de soluciones | 5 % | 📝 especificada |
| 007 | Interfaz y visualización | 5 % | 📝 especificada |
| 008 | Casos mínimos y experimentación | 10 % | 📝 especificada |
| 009 | Documentación y entregables | 10 % | 📝 especificada |

Leyenda: 📝 especificada · 🔨 en progreso · ✅ implementada y probada · 🎤 lista para sustentar.
