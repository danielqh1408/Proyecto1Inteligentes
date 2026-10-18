# Registro de uso de IA generativa

> Requisito del enunciado: el uso de IA no baja la nota por sí mismo, pero **debe declararse**. "La omisión deliberada del uso realizado se considerará una inconsistencia." Cada entrada: fecha · herramienta · quién · propósito · archivos · validación humana.
> Este registro alimenta la sección "Reporte del uso de IA" del documento técnico. Los docstrings de cada método llevan su propia declaración (AI usage / AI intervention / Student validation).

| Fecha | Herramienta | Integrante | Propósito | Archivos | Validación por el estudiante |
|---|---|---|---|---|---|
| 2026-10-17 | Claude Code (Anthropic, modelo Claude Opus) | Juan David Ocampo González | Lectura del enunciado y de los notebooks del primer corte; propuesta de arquitectura SDD (AGENTS.md, CLAUDE.md, README, constitución, specs 001–009, decisiones, roles y arneses, guía de sustentación) | `AGENTS.md`, `CLAUDE.md`, `README.md`, `specs/**`, `docs/00_ENTENDIMIENTO.md`, `docs/ARQUITECTURA.md`, `docs/DECISIONES.md`, `docs/ROLES_Y_ARNESES.md`, `docs/GUIA_SUSTENTACION.md`, `.claude/**`, `escenarios/ejemplo_enunciado.json` | PENDIENTE: Juan y Daniel deben leer las specs, aceptar o modificar cada decisión de `docs/DECISIONES.md` (estado `propuesta` → `aceptada`) y registrar aquí qué cambiaron |
| 2026-10-17 | Claude Code (Anthropic, modelo Claude Opus) | Juan David Ocampo González | Redacción del documento de introducción para Daniel (metodología SDD, agentes, arneses, decisiones a discutir y ejercicio BFS vs UCS sobre el mapa del enunciado) | `docs/01_LEEME_DANIEL.md` | Las respuestas del ejercicio de la sección 7 se comprobaron ejecutando BFS y UCS sobre `escenarios/ejemplo_enunciado.json` (pantano 7, 15 y 1). PENDIENTE: Juan revisa la redacción; Daniel la discute |
| 2026-10-18 | Claude Code (Anthropic, modelo Claude Opus) | Juan David Ocampo González | Implementación de la spec 001: modelo del escenario, validador de las 9 reglas + R10, cargador atómico, CLI `validar`, 14 escenarios inválidos y 30 pruebas. A pedido de Juan, se simplificó una primera versión más compleja (clases de posición, advertencias extra) al estilo de los notebooks | `tacticalgrid/config.py`, `tacticalgrid/__main__.py`, `tacticalgrid/escenario/*.py`, `escenarios/invalidos/*.json`, `tests/test_escenario.py`, `tests/test_validador.py`, `pyproject.toml` | `pytest` en verde (30 pruebas) y `python -m tacticalgrid validar` sobre todos los JSON. PENDIENTE: Juan revisa el código línea por línea y completa *Student validation* en los docstrings; Daniel hace la revisión cruzada |

## Política acordada
1. Toda sesión con IA que produzca código o documentación entregable se registra aquí.
2. En los docstrings: `AI usage: Yes` si la IA generó o modificó el método; `AI intervention` dice **qué parte**; `Student validation` dice **cómo** se comprobó (test, traza a mano, comparación con el notebook, modificación propia).
3. Nadie integra código generado sin haberlo ejecutado, leído línea por línea y poder explicarlo.
4. Las respuestas conceptuales del documento técnico se redactan con nuestras palabras; la IA puede revisarlas, no escribirlas solas.
