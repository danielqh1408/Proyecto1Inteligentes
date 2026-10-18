# Arquitectura — TacticalGrid

## 1. Capas (exigencia del enunciado: separar lógica del juego, escenario, algoritmos e interfaz)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Capa 4 · INTERFAZ          tacticalgrid/interfaz/  (tkinter)   ·  cli.py   │
│   solo presenta y orquesta; NO contiene lógica de IA ni reglas            │
└───────────────┬───────────────────────────┬──────────────────────────────┘
                │                           │
┌───────────────▼─────────────┐ ┌───────────▼──────────────┐ ┌──────────────────────┐
│ Capa 3a · BÚSQUEDA          │ │ Capa 3b · ADVERSARIAL    │ │ VERIFICACIÓN         │
│ problema · bfs · dfs · ucs  │ │ distancias · utilidad    │ │ verificador (oráculo │
│ a_estrella · beam ·         │ │ minimax · alfa_beta ·    │ │ independiente)       │
│ heuristicas · metricas      │ │ orden · partida          │ │                      │
└───────────────┬─────────────┘ └───────────┬──────────────┘ └──────────┬───────────┘
                │                           │                           │
┌───────────────▼───────────────────────────▼───────────────────────────▼───────────┐
│ Capa 2 · JUEGO     estado (EstadoJuego) · acciones (Accion) · reglas (R1–R10)     │
└───────────────────────────────────────┬────────────────────────────────────────────┘
┌───────────────────────────────────────▼────────────────────────────────────────────┐
│ Capa 1 · ESCENARIO  modelo (Escenario inmutable) · cargador (atómico) · validador  │
└────────────────────────────────────────────────────────────────────────────────────┘
                 ▲ JSON común (contrato con el profesor)

EXPERIMENTOS (runner, E1–E6, reporte) usa capas 1–3 + verificación, escribe resultados/
config.py: ÚNICO lugar con valores por defecto (orden de movimientos, pesos, max_turnos, profundidad)
```

**Regla de dependencias:** una capa solo importa capas inferiores. `tests/test_arquitectura.py` lo comprueba recorriendo los `import` de cada módulo.

## 2. Módulos y responsabilidades

| Módulo | Responsabilidad | Spec |
|---|---|---|
| `escenario/modelo.py` | `Posicion`, `TipoTerreno`, `UnidadDef`, `ConfigPrueba`, `Escenario` (consultas: `dentro`, `transitable`, `costo`, `costo_minimo`, `vecinos`) | 001 |
| `escenario/validador.py` | 9 reglas del enunciado + advertencias; reporta **todos** los errores | 001 |
| `escenario/cargador.py` | `cargar_escenario(ruta|dict)`: valida → construye → devuelve (o lanza `EscenarioInvalido`) | 001 |
| `juego/estado.py` | `EstadoJuego` (inmutable, hashable) | 002 |
| `juego/acciones.py` | `Accion` (MOVER, INTERCEPTAR, PASAR) | 002 |
| `juego/reglas.py` | `estado_inicial`, `acciones_legales`, `aplicar`, `es_terminal`, `ganador`, `validar_estado` | 002 |
| `busqueda/problema.py` | `ProblemaBusqueda` (protocolo), `ProblemaNavegacion`, `ProblemaMision` | 002/003 |
| `busqueda/resultado.py`, `metricas.py` | `ResultadoBusqueda` y contador de métricas con definición única | 003 |
| `busqueda/no_informada.py` | `bfs`, `dfs` | 003 |
| `busqueda/costo_uniforme.py` | `costo_uniforme` | 003 |
| `busqueda/heuristicas.py` | `cero`, `manhattan`, `obstaculos`, `manhattan_promedio`, `crear_heuristica` | 004 |
| `busqueda/a_estrella.py`, `beam.py` | `a_estrella`, `beam_search` | 004 |
| `adversarial/distancias.py` | Dijkstra inverso precalculado por escenario (`Dbase_X`, `Drec_X`) | 005 |
| `adversarial/utilidad.py` | `utilidad_terminal`, `evaluar` (con desglose) | 005 |
| `adversarial/orden.py` | `ordenar_acciones(natural|inverso|heuristico)` | 005 |
| `adversarial/minimax.py`, `alfa_beta.py` | decisión con métricas y variación principal | 005 |
| `adversarial/partida.py` | bucle por turnos, agentes HUMANO/MINIMAX/ALFA_BETA/VORAZ | 005 |
| `verificacion/verificador.py` | `verificar_camino`, `verificar_estado`, `verificar_decision`, `verificar_minimax_vs_alfabeta` | 006 |
| `experimentos/` | `runner`, `experimentos` (E1–E6), `reporte` | 008 |
| `interfaz/` | `app`, `lienzo`, paneles, `paleta` | 007 |
| `cli.py`, `__main__.py` | `validar`, `ejecutar`, `buscar`, `decidir`, `experimentos`, `gui` | 001/007/008 |
| `config.py` | valores por defecto (nunca costos) | 000 P3 |

## 3. Flujo de datos típico

**Modo búsqueda** (`python -m tacticalgrid ejecutar caso02.json`)
```
JSON ──cargar_escenario──► Escenario ──► ProblemaNavegacion(inicio=unidad_inicio, objetivo)
     ──► algoritmo(problema[, heurística, k]) ──► ResultadoBusqueda
     ──► verificar_camino ──► CLI imprime to_dict() / GUI dibuja camino + explorados + métricas
```

**Modo adversarial** (`python -m tacticalgrid decidir caso07.json --algoritmo ALFA_BETA`)
```
JSON ──► Escenario ──► estado_inicial ──► distancias.precalcular(escenario)
     ──► alfa_beta(escenario, estado, profundidad, orden, pesos) ──► ResultadoDecision
     ──► verificar_decision ──► acción + valor + valores_raiz + desglose
```

## 4. Interfaz de algoritmos (contrato interno)

```python
# Búsqueda: todos reciben un ProblemaBusqueda y devuelven ResultadoBusqueda
bfs(problema) / dfs(problema) / costo_uniforme(problema)
a_estrella(problema, heuristica)
beam_search(problema, heuristica, k, criterio="h")

# Adversarial
minimax(escenario, estado, profundidad, orden="natural", pesos=None, auditar=False) -> ResultadoDecision
alfa_beta(escenario, estado, profundidad, orden="natural", pesos=None, auditar=False) -> ResultadoDecision
```
Los algoritmos de búsqueda **no saben** que existe un juego: solo ven `estado_inicial`, `es_objetivo`, `sucesores`. Por eso el mismo `bfs` resuelve navegación simple y la misión con recurso (estado compuesto).

## 5. Configuración: precedencia
`CLI/GUI` > `JSON (prueba.* / juego.*)` > `config.py`. Lo que se usó realmente queda registrado en cada resultado (para reproducir).

## 6. Escenarios y resultados
```
escenarios/
├── ejemplo_enunciado.json         # copia literal del PDF (contrato)
├── casos/caso01…caso10_*.json     # casos mínimos con campos extra `descripcion` y `esperado`
├── sensibilidad/                  # pantano_7.json, pantano_15.json …
├── invalidos/                     # uno por regla de validación + múltiples errores
└── externos/                      # JSON del profesor / de práctica
resultados/
├── RESUMEN.md                     # esperado vs obtenido (✔/✘) de los 10 casos
└── *.csv, *.json, graficas/*.png  # E1–E6 con cabecera de reproducibilidad
```
