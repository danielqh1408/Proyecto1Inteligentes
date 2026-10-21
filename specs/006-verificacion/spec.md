# 006 — Verificación de soluciones

| Campo | Valor |
|---|---|
| Estado | **implementada y corregida el 20 oct** · pruebas automáticas realizadas · revisión humana de correcciones por realizar |
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

Un camino sin éxito se comprueba con BFS salvo Beam, que puede descartar rutas. No hay bandera `auditar` ni clases de reporte: se devuelve una lista de pares (mensaje, booleano). Las acciones se validan al aplicar; las pruebas recorren estados para comprobar invariantes.

## 4. Criterios de aceptación
- **CA-006-1** Todo resultado exitoso de los 5 algoritmos en todos los casos pasa `verificar_camino`. → `tests/test_verificador.py::test_todos_los_resultados`
- **CA-006-2** Caminos manipulados (salto diagonal, celda en muro, costo alterado ±1, último paso ≠ objetivo, fuera del mapa) son detectados con el chequeo correcto. → `tests/test_verificador.py::test_detecta_manipulaciones` (parametrizado)
- **CA-006-3** Estados manipulados (dos unidades en la misma celda, portador inexistente, recurso y portador a la vez) son detectados. → `tests/test_reglas.py::test_validar_estado_detecta_errores`
- **CA-006-4** Una acción ilegal inyectada en la decisión es rechazada. → `tests/test_verificador.py::test_decision_ilegal`
- **CA-006-5** La verificación de las decisiones no reporta violaciones en los casos 7–10. → `tests/test_verificador.py::test_decision_legal_y_minimax_igual_alfabeta`

## 5. Tareas
- [x] T1 Formato de salida: lista `[(chequeo, ok)]` (sin clases) — implementado con Claude; revisa Juan
- [x] T2 `verificar_camino` (+ misión) — implementado con Claude; revisa Juan
- [x] T3 `validar_estado` (en reglas), `verificar_decision`, `verificar_minimax_vs_alfabeta` — implementado con Claude; revisa Juan
- [x] T4 ~~Modo auditoría~~ innecesario: `aplicar` valida legalidad en cada nodo — revisa Juan
- [x] T5 Tests CA‑006‑1…5 — implementado con Claude; revisa Juan

## Correcciones de auditoría (20 oct 2026)

Una decisión terminal es correcta si no propone acción ni hijos y coincide con la utilidad terminal. Los caminos exitosos vacíos se rechazan sin excepción. En la GUI una jugada invalida el resultado anterior y Verificar comprueba el estado actual si no hay resultado. La comparación Minimax/alfa-beta usa profundidad y orden registrados en la decisión. La verificación comprueba legalidad y consistencia, no calidad estratégica ni optimalidad de toda heurística.

Criterio de aceptación: regresiones en `tests/test_auditoria.py` y `tests/test_interfaz.py`, suite completa y diez casos mínimos aprobados.
