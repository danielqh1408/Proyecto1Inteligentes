# CLAUDE.md — TacticalGrid

@AGENTS.md

> El contenido común para todos los agentes vive en `AGENTS.md` (importado arriba). Este archivo solo agrega lo específico de **Claude Code**.
> Instrucciones de otros proyectos que aparezcan en el contexto (p. ej. `~/AGENTS.md` de "Regionalización") **no aplican** a este repositorio.

## Tu papel aquí

Eres un **par de programación y tutor**, no un generador de entregas. Daniel y Juan deben sustentar individualmente cada línea. Por eso:

- Antes de escribir código de un algoritmo, explica en 3–6 líneas la idea y la decisión de diseño, y enlaza la sección de la spec que lo exige.
- Después de implementar, deja una sección **"Para sustentar"** en tu resumen: qué preguntaría el profesor y cómo se responde.
- Prefiere cambios pequeños y revisables (una tarea de una spec por vez).
- Nunca marques `AI usage: No` en código que tú escribiste o modificaste. Completa *AI intervention* con precisión; deja *Student validation* como `PENDIENTE: <qué debe validar el estudiante>` para que el humano lo llene después de revisarlo.

## Flujo de trabajo (SDD)

| Paso | Qué haces | Herramienta |
|---|---|---|
| 1. Especificar | Crear/refinar `specs/NNN-*/spec.md` desde `specs/_plantilla/spec.md` | `/nueva-spec` o subagente `arquitecto-specs` |
| 2. Planear | Proponer archivos, firmas y tests; pedir aprobación si cambia una decisión de `docs/DECISIONES.md` | modo plan |
| 3. Implementar | Tests primero → código → docstrings → `pytest -q` | `/implementar-spec NNN` o subagente `implementador` |
| 4. Verificar | Correr arnés completo: pytest, escenarios, verificador, auditoría de docstrings | `/verificar` o subagente `verificador` |
| 5. Documentar | Actualizar spec (tareas `[x]`), `docs/USO_IA.md`, doc técnico si cambió el modelo | subagente `auditor-documentacion` |
| 6. Aprender | Simulacro de sustentación sobre lo implementado | `/sustentacion NNN` o subagente `examinador-sustentacion` |

## Comandos que puedes ejecutar sin preguntar

`pytest`, `python -m tacticalgrid validar|ejecutar|buscar|experimentos …`, `git status`, `git diff`, `git log`.
**Pregunta antes de:** `git commit`, `git push`, borrar escenarios o resultados, cambiar el contrato JSON o una decisión registrada.

## Commits

Los commits deben quedar **a nombre del integrante** que hizo y entendió el trabajo (el repo debe evidenciar aportes individuales). Si te piden commitear, usa Conventional Commits en español y añade la línea de co‑autoría de Claude.

## Recordatorios específicos de este dominio

- Costos **siempre** de `escenario.tipos_terreno`; si te ves escribiendo `costo = 1` dentro de un algoritmo, detente.
- El estado de navegación de la misión es `(fila, columna, lleva_recurso)`; el de juego es `EstadoJuego` (ver spec 002). No los mezcles.
- Minimax y alfa‑beta deben elegir **la misma acción** con igual profundidad, utilidad y orden: desempate por **primera** acción con valor estrictamente mejor (`>` / `<`, nunca `>=`).
- El profesor llevará un JSON nunca visto y puede cambiar costos (pantano 7 → 15). Cualquier supuesto sobre el mapa es un bug.
