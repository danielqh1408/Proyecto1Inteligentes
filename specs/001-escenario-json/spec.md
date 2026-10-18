# 001 — Escenario JSON: modelo, carga y validación atómica

| Campo | Valor |
|---|---|
| Estado | borrador |
| Responsable | Juan · Revisor: Daniel |
| Rúbrica | Validación de escenarios y soluciones (5 %) — y es la base de todo lo demás |
| Depende de | — |
| Fuente en el enunciado | "Escenario de juego", "Formato común de escenarios JSON", "Modos de prueba", "Validación del escenario", "Compatibilidad con escenarios externos" (pp. 2, 5–7) |

## 1. Contexto y porqué
El profesor llevará **al menos un JSON nunca visto** y podrá cambiar costos, obstáculos, bases, unidades y recurso. Si la carga falla o algo está quemado en el código, se cae todo lo demás. Esta capa traduce el JSON a un objeto `Escenario` **inmutable** que el resto del sistema consulta.

## 2. Requisitos
- **RF-001-1** Cargar un archivo con los campos obligatorios: `version`, `mapa.filas`, `mapa.columnas`, `tipos_terreno`, `terreno`, `bases.A`, `bases.B`, `recurso`, `unidades`, `turno`, `juego.portador_recurso`; y el opcional `prueba`.
- **RF-001-2** Aceptar cualquier dimensión válida (mínimo de desarrollo 20×20, pero la app admite otras; p. ej. el 4×4 del enunciado).
- **RF-001-3** Los costos se leen de `tipos_terreno[nombre].costo`; un terreno con `transitable: false` puede omitir `costo`.
- **RF-001-4** Aceptar campos extra propios (p. ej. `juego.profundidad_maxima_minimax`, `juego.max_turnos`, `juego.orden_acciones`, `juego.pesos_utilidad`, `prueba.algoritmo`, `prueba.heuristica`, `prueba.k`, `prueba.orden_movimientos`, `esperado`) sin romper la carga.
- **RF-001-5** **Validación completa antes de aplicar** (lista del enunciado):
  1. `filas` y `columnas` enteros positivos y consistentes con la matriz `terreno` (número de filas y longitud de **cada** fila).
  2. Todo terreno usado en la matriz existe en `tipos_terreno`.
  3. Todo terreno transitable tiene `costo` numérico **> 0**.
  4. Bases, recurso y unidades dentro del mapa.
  5. Ninguna unidad sobre celda no transitable.
  6. Identificadores de unidad únicos.
  7. Cada unidad pertenece a `A` o `B`.
  8. `turno` es `A` o `B`.
  9. Si `portador_recurso` no es `null`, identifica una unidad existente.
- **RF-001-6** Un escenario inválido se rechaza **sin modificar** el escenario actual, y se informan **todos** los errores encontrados (no solo el primero), cada uno con ruta del campo y explicación.
- **RF-001-7** Modos de `prueba.modo`: `busqueda`, `partida`, `adversarial`.

## 3. Decisiones de diseño
- **D-01 (bando en minúsculas):** el enunciado dice "a o b" en la validación pero usa `"A"` en el ejemplo. Se aceptan `A/B` y `a/b` y se **normalizan a mayúsculas**.
- **D-02 (validaciones extra = advertencias):** reglas que el enunciado no exige (base o recurso sobre obstáculo, dos unidades en la misma celda, recurso en una base, mapa < 20×20, `version` desconocida, portador lejos del recurso) se reportan como **advertencias**, no como errores, para no rechazar un JSON válido del profesor. Excepción: dos unidades en la misma celda sí es **error**, porque viola el modelo de estado (spec 002) — *decisión a confirmar en equipo*.
- **D-03 (portador y recurso):** si `portador_recurso` no es `null`, la posición del recurso se toma de la unidad portadora (el campo `recurso` se conserva como posición original informativa).
- **D-04 (`profundidad_maxima_minimax`):** aunque aparece en el ejemplo dentro de `juego`, se trata como opcional con valor por defecto en `config.py`.
- Validación implementada **a mano** (sin `jsonschema`) para dar mensajes en español y mantener el núcleo en stdlib.

## 4. Diseño (interfaces)

```
tacticalgrid/escenario/
├── modelo.py      # Posicion, TipoTerreno, UnidadDef, ConfigPrueba, Escenario (frozen dataclasses)
├── cargador.py    # cargar_escenario(ruta|dict) -> Escenario  (valida y construye; atómico)
├── validador.py   # validar(dict) -> ReporteValidacion(errores: list[ErrorValidacion], advertencias: list)
└── errores.py     # EscenarioInvalido(Exception) con .reporte
```

```python
@dataclass(frozen=True)
class Posicion: fila: int; columna: int

@dataclass(frozen=True)
class TipoTerreno: nombre: str; transitable: bool; costo: float | None

@dataclass(frozen=True)
class UnidadDef: id: str; bando: str; tipo: str; inicio: Posicion

@dataclass(frozen=True)
class Escenario:
    version: str
    filas: int; columnas: int
    tipos: Mapping[str, TipoTerreno]
    terreno: tuple[tuple[str, ...], ...]
    bases: Mapping[str, Posicion]            # {"A": ..., "B": ...}
    recurso: Posicion
    unidades: tuple[UnidadDef, ...]          # orden del JSON (determinismo)
    turno: str
    portador_recurso: str | None
    juego: Mapping[str, Any]                 # campos extra de "juego"
    prueba: ConfigPrueba | None
    crudo: Mapping[str, Any]                 # JSON original (para exportar/reproducir)

    def dentro(self, p) -> bool
    def transitable(self, p) -> bool
    def costo(self, p) -> float              # costo de ENTRAR a la celda p
    def costo_minimo(self) -> float          # mínimo costo transitable (para heurísticas admisibles)
    def vecinos(self, p, orden) -> list[Posicion]   # 4-vecindad transitable, en el orden dado
```

`EstadoAplicacion` (en la capa de interfaz/CLI) guarda el escenario actual y solo lo reemplaza si `cargar_escenario` **no** lanza excepción ⇒ atomicidad trivial porque `Escenario` es inmutable y se construye completo antes de asignarse.

## 5. Criterios de aceptación
- **CA-001-1** *Dado* el JSON del enunciado (`escenarios/ejemplo_enunciado.json`), *cuando* se carga, *entonces* se obtiene un `Escenario` 4×4 con costo(pantano)=7, `muro` no transitable, 4 unidades y `prueba.modo == "busqueda"`. → `tests/test_escenario.py::test_carga_ejemplo_enunciado`
- **CA-001-2** *Dado* un JSON por cada regla de RF‑001‑5 violada (`escenarios/invalidos/*.json`), *cuando* se valida, *entonces* el reporte contiene un error que nombra el campo y la regla. → `test_validador.py::test_cada_regla[...]` (parametrizado)
- **CA-001-3** *Dado* un JSON con **varias** violaciones, *entonces* se reportan todas. → `test_validador.py::test_reporta_todos_los_errores`
- **CA-001-4** *Dado* un escenario cargado E1 y un JSON inválido, *cuando* se intenta cargar, *entonces* el escenario activo sigue siendo E1 (mismo objeto). → `test_escenario.py::test_carga_atomica`
- **CA-001-5** *Dado* el ejemplo con `pantano.costo` cambiado de 7 a 15, *entonces* `escenario.costo((2,2)) == 15` sin tocar código. → `test_escenario.py::test_costos_desde_json`
- **CA-001-6** *Dado* un JSON con campos extra desconocidos, *entonces* carga sin error y los conserva en `crudo`. → `test_escenario.py::test_campos_extra`
- **CA-001-7** *Dado* `"bando": "a"`, *entonces* se normaliza a `"A"`. → `test_escenario.py::test_bando_minuscula`
- **CA-001-8** Mapas no cuadrados (p. ej. 20×35) cargan y `dentro()` respeta filas ≠ columnas. → `test_escenario.py::test_no_cuadrado`

## 6. Pruebas y evidencia
- `escenarios/ejemplo_enunciado.json` (copia literal del PDF).
- `escenarios/invalidos/`: `filas_cero.json`, `matriz_inconsistente.json`, `terreno_desconocido.json`, `costo_no_positivo.json`, `base_fuera.json`, `recurso_fuera.json`, `unidad_fuera.json`, `unidad_en_muro.json`, `id_duplicado.json`, `bando_invalido.json`, `turno_invalido.json`, `portador_inexistente.json`, `multiples_errores.json`.

## 7. Tareas
- [ ] T1 Modelo inmutable (`modelo.py`) — Juan
- [ ] T2 Validador con las 9 reglas + advertencias — Juan
- [ ] T3 Cargador atómico + `EscenarioInvalido` — Juan
- [ ] T4 JSON del enunciado + 13 JSON inválidos — Juan
- [ ] T5 Tests CA‑001‑1…8 — Juan
- [ ] T6 Revisión cruzada y simulacro de preguntas — Daniel

## 8. Para sustentar
- *¿Qué pasa si el JSON tiene un error a mitad de la carga?* → Se valida todo antes de construir; el escenario activo solo se reemplaza al final. No hay estado parcial porque `Escenario` es inmutable.
- *Si cambio el pantano de 7 a 15, ¿qué cambia en el código?* → Nada. `escenario.costo(p)` lee `tipos_terreno`.
- *¿Por qué no rechazan una base sobre un muro?* → El enunciado no lo exige; lo reportamos como advertencia para no rechazar un escenario válido del profesor.
