# 001 — Escenario JSON: modelo, carga y validación atómica

| Campo | Valor |
|---|---|
| Estado | **implementada y corregida el 20 oct** · pruebas automáticas realizadas · revisión humana de correcciones por realizar |
| Responsable | Juan · Revisor: Daniel |
| Rúbrica | Validación de escenarios y soluciones (5 %) — y es la base de todo lo demás |
| Depende de | — |
| Fuente en el enunciado | "Escenario de juego", "Formato común de escenarios JSON", "Modos de prueba", "Validación del escenario", "Compatibilidad con escenarios externos" (pp. 2, 5–7) |

## 1. Contexto y porqué
El profesor llevará **al menos un JSON nunca visto** y podrá cambiar costos, obstáculos, bases, unidades y recurso. Si la carga falla o algo está quemado en el código, se cae todo lo demás. Esta capa traduce el JSON a un objeto `Escenario` que el resto del sistema consulta.

## 2. Requisitos
- **RF-001-1** Cargar un archivo con los campos obligatorios: `version`, `mapa.filas`, `mapa.columnas`, `tipos_terreno`, `terreno`, `bases.A`, `bases.B`, `recurso`, `unidades`, `turno`, `juego.portador_recurso`; y el opcional `prueba`.
- **RF-001-2** Aceptar cualquier dimensión válida (mínimo de desarrollo 20×20, pero la app admite otras; p. ej. el 4×4 del enunciado).
- **RF-001-3** Los costos se leen de `tipos_terreno[nombre].costo`; un terreno con `transitable: false` puede omitir `costo`.
- **RF-001-4** Aceptar campos extra propios (p. ej. `juego.profundidad_maxima_minimax`, `juego.max_turnos`, `prueba.algoritmo`, `descripcion`) sin romper la carga.
- **RF-001-5** **Validación completa antes de aplicar** (lista del enunciado):
  1. `filas` y `columnas` enteros positivos y consistentes con la matriz `terreno`.
  2. Todo terreno usado en la matriz existe en `tipos_terreno`.
  3. Todo terreno transitable tiene `costo` numérico **> 0**.
  4. Bases, recurso y unidades dentro del mapa.
  5. Ninguna unidad sobre celda no transitable.
  6. Identificadores de unidad únicos.
  7. Cada unidad pertenece a `A` o `B`.
  8. `turno` es `A` o `B`.
  9. Si `portador_recurso` no es `null`, identifica una unidad existente.
- **RF-001-6** Un escenario inválido se rechaza **sin modificar** el escenario actual, y se informan los errores con el campo y la explicación.
- **RF-001-7** Modos de `prueba.modo`: `busqueda`, `partida`, `adversarial` (se interpretan en las specs 003–005).

## 3. Decisiones de diseño
- **D-01 (bando en minúsculas):** se aceptan `A/B` y `a/b` y se **normalizan a mayúsculas**.
- **D-02 (solo lo que pide el PDF):** se validan exactamente las 9 reglas del enunciado, más tipos de dato (E00) y **R10: dos unidades no pueden estar en la misma celda** (rompería el modelo de estado de la spec 002). No se agregan advertencias extra: más reglas = más código que explicar y más riesgo de rechazar un JSON válido del profesor.
- **Parada temprana:** si faltan campos obligatorios o las dimensiones/matriz no son coherentes (R1), se devuelven solo esos errores, porque el resto de reglas no se puede comprobar sin un mapa bien formado. En los demás casos se reportan **todos** los errores juntos.
- **D-03 (portador):** el escenario guarda `portador` y `recurso` tal como vienen; dónde está el recurso cuando hay portador lo resuelve `estado_inicial` (spec 002).
- **D-04:** opciones como `profundidad_maxima_minimax` son opcionales; sus defectos viven en `config.py`.
- Validación **a mano** (sin `jsonschema`) para dar mensajes en español y mantener el núcleo en la librería estándar.
- **Atomicidad sin código extra:** `cargar_escenario` valida antes de construir y lanza `EscenarioInvalido` si hay errores; como la excepción ocurre antes de devolver, `escenario = cargar_escenario(ruta)` nunca deja un estado a medias.

## 4. Diseño (implementado)

```
tacticalgrid/
├── config.py                 # ORDEN_MOVIMIENTOS, DEFECTOS_JUEGO
├── __main__.py               # CLI: python -m tacticalgrid validar <rutas...>
└── escenario/
    ├── modelo.py             # Unidad (NamedTuple), Escenario (dataclass), DIRECCIONES
    ├── validador.py          # validar(datos) -> list[str]
    └── cargador.py           # cargar_escenario(ruta | dict) -> Escenario ; EscenarioInvalido
```

Posiciones = tuplas `(fila, columna)`, igual que en los notebooks.

```python
class Unidad(NamedTuple): id: str; bando: str; tipo: str; pos: tuple[int, int]

@dataclass(frozen=True, eq=False)
class Escenario:
    filas, columnas
    costos: dict[str, float | None]        # None = no transitable
    terreno: tuple[tuple[str, ...], ...]
    bases: {"A": (f, c), "B": (f, c)}
    recurso: (f, c)
    unidades: tuple[Unidad, ...]           # en el orden del JSON
    turno: "A" | "B"
    portador: str | None
    juego: dict                            # todo el bloque "juego", con campos extra
    prueba: dict | None

    dentro(pos) · transitable(pos) · costo(pos) · vecinos(pos, orden) · costo_minimo()
```

Mensajes de error: `"[código] campo: explicación"`, p. ej. `[R4] bases.B: (4, 3) está fuera del mapa 4x4`. Códigos: E00 (estructura), R1–R9 (enunciado), R10 (superposición).

## 5. Criterios de aceptación
- **CA-001-1** El JSON del enunciado carga como 4×4, pantano = 7, muro no transitable, 4 unidades, `prueba.modo == "busqueda"`. → `tests/test_escenario.py::test_carga_ejemplo_enunciado` ✅
- **CA-001-2** Cada regla violada en `escenarios/invalidos/*.json` produce su código. → `tests/test_validador.py::test_cada_regla[...]` ✅
- **CA-001-3** Varias violaciones a la vez se reportan todas. → `test_cada_regla[varios_errores]` ✅
- **CA-001-4** Un JSON inválido no reemplaza el escenario activo. → `tests/test_escenario.py::test_carga_atomica` ✅
- **CA-001-5** Pantano 7 → 15 en el JSON cambia `costo((2,2))` sin tocar código. → `test_costos_desde_json` ✅
- **CA-001-6** Campos extra se aceptan y se conservan. → `test_campos_extra` ✅
- **CA-001-7** `"bando": "a"` se normaliza a `"A"`. → `test_bando_minuscula` ✅
- **CA-001-8** Mapas no cuadrados cargan y `dentro()` respeta filas ≠ columnas. → `test_no_cuadrado` ✅

## 6. Pruebas y evidencia
- `escenarios/ejemplo_enunciado.json` (copia literal del PDF).
- `escenarios/invalidos/`: 14 archivos, uno por regla (+ superposición + varios errores). Cada uno lleva los campos extra `descripcion` y `errores_esperados`, que usa el test.
- Probar a mano: `python -m tacticalgrid validar escenarios/ejemplo_enunciado.json escenarios/invalidos/*.json`

## 7. Tareas
- [x] T1 Modelo (`modelo.py`) — Juan (con Claude)
- [x] T2 Validador con las 9 reglas + R10 — Juan (con Claude)
- [x] T3 Cargador atómico + `EscenarioInvalido` + CLI `validar` — Juan (con Claude)
- [x] T4 JSON del enunciado + 14 JSON inválidos — Juan (con Claude)
- [x] T5 Tests CA‑001‑1…8 (30 pruebas) — Juan (con Claude)
- [x] T6 `Student validation` completado en los docstrings (20 oct)
- [x] T7 Revisión cruzada y simulacro de preguntas — Daniel (20 oct, ver docs/USO_IA.md)

## Correcciones de auditoría (20 oct 2026)

Se validan también los campos opcionales que la aplicación consume: estructura de `prueba`, objetivo dentro del mapa, unidad existente, k/profundidad/max_turnos enteros positivos, orden de movimientos como permutación de las cuatro direcciones, booleanos y pesos numéricos finitos. Bases o recurso sobre muros siguen admitidos por el contrato; se tratan como destinos inalcanzables. Una prueba incompleta o mal tipada se rechaza antes de reemplazar el escenario.

Criterio de aceptación: regresiones en `tests/test_auditoria.py` y `tests/test_interfaz.py`, suite completa y diez casos mínimos aprobados.
