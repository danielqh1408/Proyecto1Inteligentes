# 009 — Documentación técnica, uso de IA y entregables

| Campo | Valor |
|---|---|
| Estado | **entregables generados el 21 oct** · ensayo de Juan realizado; revisión individual de Daniel y sustentación no certificadas |
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
- [x] Código y documentos corregidos en la misma revisión; el commit de `main` identifica la entrega. El tag histórico `v1.0-sustentacion` corresponde a la versión anterior.

## 2. Documentación de métodos (obligatoria)
Plantilla en `AGENTS.md §7` con los 7 campos: **Purpose, Preconditions, Postconditions, Complexity, AI usage, AI intervention, Student validation**.

Métodos que **deben** tenerla: la lista `METODOS` de `tests/test_documentacion.py` (fuente única de verdad; 31 métodos: validador, cargador, costo/vecinos, estado inicial, reglas, sucesores, los 5 algoritmos, heurísticas, distancias, evaluación, decidir, orden de acciones y verificador).

**Arnés:** `tests/test_documentacion.py` importa cada método de la lista y falla si su docstring no contiene los 7 rótulos o si no identifica pruebas como evidencia de validación (`pytest -m entrega`).

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
- **CA-009-2** `pytest -m entrega` en verde (evidencia de pruebas identificada; no certifica revisión humana).
- **CA-009-3** El documento técnico tiene las 11 secciones exigidas y cada afirmación numérica referencia un archivo de `resultados/`.
- **CA-009-4** `git shortlog -sn` debe evidenciar aportes reales de ambos integrantes, como exige el PDF. El historial disponible atribuye a Daniel documentación y revisión; no se inventan commits de código.

## 6. Tareas
- [x] T1 `tests/test_documentacion.py` (auditor de docstrings) — implementado con Claude
- [x] T2 Manual de usuario con capturas — Daniel (20 oct)
- [x] T3 Documento técnico completo con cifras reales (Claude y Codex; revisión humana de correcciones por realizar)
- [x] T4 `Student validation` en los 31 métodos auditados (`pytest -m entrega` en verde)
- [x] T5 Ensayo de Juan: recorrido de diez casos y explicación de resultados (21 oct); no equivale a certificar dominio de todo el código.
- [x] T6 Tag `v1.0-sustentacion` (histórico; no mover automáticamente)

## Correcciones de auditoría (20 oct 2026)

Ampliar el arnés de los siete campos a todas las funciones relevantes identificadas en la auditoría. Actualizar informe, manual, guías, arquitectura y trazabilidad con nombres reales. Declarar la intervención de Codex y distinguir validación automática de revisión humana, sin afirmar revisiones futuras como completadas. El tag v1.0-sustentacion es histórico mientras las correcciones estén sin commit; no se mueve ni se publica automáticamente. Git debe evidenciar aportes reales de ambos, conforme al PDF, sin inventar autorías de código.

Criterio de aceptación: regresiones en `tests/test_auditoria.py` y `tests/test_interfaz.py`, suite completa y diez casos mínimos aprobados.

## Edición final de documentos (21 oct)

Manual y documento técnico refinados, con fuentes Markdown y PDF en output/pdf. Se incluye guion breve, figura real de la tabla adversarial y gráficas derivadas de E4/E5. El índice docs/ENTREGA.md relaciona cada archivo con su propósito y la comprobación final. Regeneración: herramientas/generar_entregables.py; dependencias documentales separadas del juego.
