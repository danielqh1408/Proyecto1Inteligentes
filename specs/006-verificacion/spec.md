# 006 — Verificación de soluciones

| Campo | Valor |
|---|---|
| Estado | **implementada** · revisada por Daniel (20 oct) · falta la revisión de Juan antes de la sustentación |
| Responsable | Daniel · Revisor: Juan |
| Rúbrica | Validación de escenarios y soluciones (5 %) |
| Depende de | 002, 003, 005 |
| Fuente en el enunciado | "Verificación de soluciones" (p. 8) |

## 1. Contexto y porqué
"El sistema no solo produce una respuesta, sino que puede comprobar propiedades básicas de esa respuesta." El verificador es **independiente** de los algoritmos: recalcula todo desde el escenario y las reglas, sin confiar en lo que reporta el algoritmo. Además es el **oráculo** del arnés de pruebas (P7).

## 2. Requisitos (lista del enunciado)
- **RF-006-1** Cada movimiento del camino es válido (celdas consecutivas 4‑adyacentes, dentro del mapa).
- **RF-006-2** Ninguna unidad atraviesa obstáculos.
- **RF-006-3** El costo reportado coincide con las transiciones realizadas.
- **RF-006-4** El estado final satisface la condición objetivo.
- **RF-006-5** No se generan estados inválidos.
- **RF-006-6** Las acciones consideradas por Minimax son legales.
- **RF-006-7** Opción de verificación accesible desde la GUI y la CLI (`--verificar`).

## 3. Diseño

> **Implementado (versión simple):** `tacticalgrid/verificacion/verificador.py` con `verificar_camino`, `verificar_decision`, `verificar_minimax_vs_alfabeta` y `texto`. Cada una devuelve `[(chequeo, ok), ...]` (sin clases). No hay "modo auditoría" aparte: `reglas.aplicar` ya rechaza cualquier acción ilegal, así que Minimax no puede generar un hijo ilegal, y `verificar_decision` comprueba que los estados de la raíz son válidos (`validar_estado`). CLI: `buscar ... --verificar`, `decidir ... --verificar`; `ejecutar` verifica siempre.
> Beam sin éxito no se compara con BFS: Beam no es completo y puede fallar aunque exista camino (caso 5).
>
> Bosquejo original (referencia):
```python
@dataclass(frozen=True)
class Chequeo: nombre: str; ok: bool; detalle: str

@dataclass(frozen=True)
class ReporteVerificacion:
    chequeos: tuple[Chequeo, ...]
    @property
    def ok(self) -> bool

verificar_camino(escenario, problema, resultado) -> ReporteVerificacion
    # inicio correcto · pasos adyacentes · dentro del mapa · transitables · costo recalculado (tolerancia 1e-9)
    # · longitud = len(camino) - 1 · estado final es objetivo (en misión: pasó por el recurso y terminó en la base)
verificar_estado(escenario, estado) -> ReporteVerificacion        # invariantes de spec 002 §3.5
verificar_decision(escenario, estado, resultado_decision) -> ReporteVerificacion
    # la acción recomendada ∈ acciones_legales(estado) · el sucesor es válido
verificar_minimax_vs_alfabeta(escenario, estado, profundidad, orden) -> ReporteVerificacion
    # misma acción y mismo valor; evaluados(αβ) ≤ evaluados(minimax)
```
**Modo auditoría:** `minimax(..., auditar=True)` y `alfa_beta(..., auditar=True)` llaman a `verificar_estado` en cada nodo generado y comprueban que cada acción expandida esté en `acciones_legales`; si algo falla, lanzan `ViolacionRegla` con el detalle. Se usa en tests y en el botón "Verificar" de la GUI (no en la ejecución normal, para no distorsionar tiempos).

Un camino con `exito = False` se verifica como: camino vacío, costo 0, y (opcional, `--confirmar-sin-ruta`) BFS confirma que el objetivo es inalcanzable.

## 4. Criterios de aceptación
- **CA-006-1** Todo resultado exitoso de los 5 algoritmos en todos los casos pasa `verificar_camino`. → `test_verificador.py::test_todos_los_resultados`
- **CA-006-2** Caminos manipulados (salto diagonal, celda en muro, costo alterado ±1, último paso ≠ objetivo, fuera del mapa) son detectados con el chequeo correcto. → `test_verificador.py::test_detecta_manipulaciones` (parametrizado)
- **CA-006-3** Estados manipulados (dos unidades en la misma celda, portador inexistente, recurso y portador a la vez) son detectados. → `test_verificador.py::test_estados_invalidos`
- **CA-006-4** Una acción ilegal inyectada en la decisión es rechazada. → `test_verificador.py::test_decision_ilegal`
- **CA-006-5** El modo auditoría no reporta violaciones en los casos 7–10. → `test_verificador.py::test_auditoria_arbol`

## 5. Tareas
- [x] T1 Formato de salida: lista `[(chequeo, ok)]` (sin clases) — implementado con Claude; revisa Juan
- [x] T2 `verificar_camino` (+ misión) — implementado con Claude; revisa Juan
- [x] T3 `validar_estado` (en reglas), `verificar_decision`, `verificar_minimax_vs_alfabeta` — implementado con Claude; revisa Juan
- [x] T4 ~~Modo auditoría~~ innecesario: `aplicar` valida legalidad en cada nodo — revisa Juan
- [x] T5 Tests CA‑006‑1…5 — implementado con Claude; revisa Juan

## 6. Para sustentar
- *¿Cómo sabe que el costo reportado es correcto?* → El verificador lo recalcula sumando `costo(celda)` del escenario, independiente del algoritmo.
- *¿Cómo garantiza que Minimax no considera jugadas ilegales?* → Modo auditoría: cada hijo se compara contra `acciones_legales` y se validan invariantes.
