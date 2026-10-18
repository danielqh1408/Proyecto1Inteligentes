# Arquitectura — TacticalGrid

## 1. Capas (exigencia del enunciado: separar lógica del juego, escenario, algoritmos e interfaz)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Capa 4 · INTERFAZ          tacticalgrid/interfaz/  (tkinter) · __main__.py│
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
| `escenario/modelo.py` | `Unidad`, `Escenario` (consultas: `dentro`, `transitable`, `costo`, `costo_minimo`, `vecinos`) | 001 |
| `escenario/validador.py` | `validar(datos) -> list[str]`: 9 reglas del enunciado + R10 | 001 |
| `escenario/cargador.py` | `cargar_escenario(ruta|dict)`: valida → construye → devuelve (o lanza `EscenarioInvalido`) | 001 |
| `juego/estado.py` | `EstadoJuego` (inmutable, hashable), `Accion`, `estado_inicial` | 002 |
| `juego/reglas.py` | `acciones_legales`, `aplicar`, `costo_accion`, `es_terminal`, `ganador`, `validar_estado` | 002 |
| `busqueda/problema.py` | `ProblemaNavegacion`, `ProblemaMision` (interfaz: `inicio`, `es_objetivo`, `sucesores`) | 002/003 |
| `busqueda/resultado.py` | `Resultado` (métricas + formato del enunciado), `reconstruir`, `posicion` | 003 |
| `busqueda/algoritmos.py` | `bfs`, `dfs` (comparten `_busqueda_ciega`), `a_estrella`, `costo_uniforme` (= A* con h=0), `beam_search` | 003/004 |
| `busqueda/heuristicas.py` | `manhattan`, `obstaculos`, `manhattan_promedio`, `crear_heuristica` | 004 |
| `busqueda/ejecutar.py` | `crear_problema` y `ejecutar_busqueda`: corre la prueba del JSON con cualquier algoritmo | 003/004 |
| `adversarial/utilidad.py` | `distancias` (4 Dijkstra con caché), `restante`, `evaluar` (con desglose), `utilidad_terminal` | 005 |
| `adversarial/minimax.py` | `decidir(poda=...)` (una sola recursión), `minimax`, `alfa_beta`, `voraz`, `ordenar_acciones`, `Decision` | 005 |
| `adversarial/partida.py` | `jugar` (bucle por turnos), `decidir_con`, `resumen_final` | 005 |
| `verificacion/verificador.py` | `verificar_camino`, `verificar_estado`, `verificar_decision`, `verificar_minimax_vs_alfabeta` | 006 |
| `experimentos/` | `runner`, `experimentos` (E1–E6), `reporte` | 008 |
| `interfaz/` | `app`, `lienzo`, paneles, `paleta` | 007 |
| `__main__.py` | `validar`, `ejecutar`, `buscar`, `decidir`, `experimentos`, `gui` | 001/007/008 |
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
