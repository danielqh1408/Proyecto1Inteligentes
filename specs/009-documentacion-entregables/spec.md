# 009 — Documentación técnica, uso de IA y entregables

| Campo | Valor |
|---|---|
| Estado | **casi completa** · solo falta la revisión de Juan y la sustentación |
| Responsable | Ambos |
| Rúbrica | Calidad y documentación técnica del código (10 %) + requisito de entrega |
| Depende de | todas |
| Fuente en el enunciado | "Documentación técnica de métodos", "Uso de inteligencia artificial generativa", "Entregables", "Sustentación" (pp. 8–10) |

## 1. Entregables (checklist del enunciado)
- [~] Repositorio Git que evidencie aportes de **cada** integrante (commits con cuentas propias, ramas por spec, PRs revisados por el otro).
- [x] `README.md` con nombres de los integrantes, instalación y ejecución.
- [x] Código fuente completo.
- [x] Escenarios JSON de desarrollo y casos mínimos (`escenarios/`).
- [x] **Manual de usuario** → `docs/MANUAL_USUARIO.md` (con capturas).
- [x] **Documento técnico** → `docs/DOCUMENTO_TECNICO.md` (Markdown; se ve formateado en GitHub) con: modelado del problema, representación de estados, reglas del juego, costos, heurísticas, función de utilidad, metodología experimental, resultados, análisis de complejidad, limitaciones y reporte del uso de IA.
- [x] Evidencia para reproducir experimentos (`resultados/` + comando).
- [x] Repositorio y documentos = **misma versión** que se sustenta (tag `v1.0-sustentacion`).

## 2. Documentación de métodos (obligatoria)
Plantilla en `AGENTS.md §7` con los 7 campos: **Purpose, Preconditions, Postconditions, Complexity, AI usage, AI intervention, Student validation**.

Métodos que **deben** tenerla: la lista `METODOS` de `tests/test_documentacion.py` (fuente única de verdad; 24 métodos: validador, cargador, costo/vecinos, estado inicial, reglas, sucesores, los 5 algoritmos, heurísticas, distancias, evaluación, decidir, orden de acciones y verificador).

**Arnés:** `tests/test_documentacion.py` importa cada método de la lista y falla si su docstring no contiene los 7 rótulos o si `Student validation` sigue en `PENDIENTE` al momento de la entrega (`pytest -m entrega`).

## 3. Uso de IA
- Registro cronológico en `docs/USO_IA.md`: fecha, herramienta, quién la usó, para qué, archivos afectados, cómo se validó.
- Cada método documenta su uso de IA con precisión. **Omitirlo deliberadamente es una inconsistencia.**
- El documento técnico incluye la sección "Reporte del uso de IA" resumiendo el registro.

## 4. Preparación de la sustentación (50 % individual)
- `docs/GUIA_SUSTENTACION.md`: banco de preguntas y respuestas cortas, mapa "dónde está cada cosa en el código", lista de modificaciones pequeñas ensayadas.
- Simulacro con el subagente `examinador-sustentacion` por cada spec (cada integrante, **también sobre las specs del otro**).
- Ensayo de "escenario externo": cada integrante crea un JSON sorpresa para el otro.

## 5. Criterios de aceptación
- **CA-009-1** `pytest tests/test_documentacion.py` en verde.
- **CA-009-2** `pytest -m entrega` en verde (sin `PENDIENTE`).
- **CA-009-3** El documento técnico tiene las 11 secciones exigidas y cada afirmación numérica referencia un archivo de `resultados/`.
- **CA-009-4** `git shortlog -sn` muestra commits de ambos integrantes en código (no solo en documentación).

## 6. Tareas
- [x] T1 `tests/test_documentacion.py` (auditor de docstrings) — implementado con Claude
- [x] T2 Manual de usuario con capturas — Daniel (20 oct)
- [x] T3 Documento técnico completo con cifras reales (Claude, revisado por el equipo; ver USO_IA)
- [x] T4 `Student validation` en los 24 métodos auditados (`pytest -m entrega` en verde)
- [ ] T5 Simulacros de sustentación — Juan (`/sustentacion NNN`)
- [x] T6 Tag `v1.0-sustentacion` (20 oct; moverlo si se cambia algo antes de sustentar)
