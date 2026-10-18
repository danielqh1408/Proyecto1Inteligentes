---
description: Implementa una tarea de una spec aprobada (TDD + docstrings de 7 campos + registro de IA)
argument-hint: <NNN> [tarea, p. ej. T2]
---
Implementa la spec `$ARGUMENTS` de TacticalGrid usando el subagente `implementador`.

- Si no se indica tarea, toma la primera `- [ ]` pendiente de la spec cuyas dependencias estén listas.
- Antes de codificar, explícame en pocas líneas la idea y la decisión de diseño.
- Tests primero, luego código, luego `pytest -q`.
- Al terminar, lanza el subagente `verificador` sobre lo cambiado y muéstrame su tabla.
- Cierra con la sección "Para sustentar". No hagas commit: pregúntame.
