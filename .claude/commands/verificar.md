---
description: Corre el arnés completo (pytest, casos, verificador, reglas duras, documentación) y reporta
---
Usa el subagente `verificador` para revisar el estado actual de TacticalGrid.
Luego usa `auditor-documentacion` sobre los archivos modificados según `git status`.
Entrega un resumen único: qué está ✔, qué está ✘, y qué arreglar primero (priorizado por peso en la rúbrica).
