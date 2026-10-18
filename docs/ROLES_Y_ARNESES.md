# Roles y arneses

> **Rol** = quién decide y responde por algo (humano o agente).
> **Arnés** (*harness*) = la estructura que rodea al trabajo para que sea correcto y verificable sin depender de la memoria de nadie: el contexto que lee el agente, las pruebas que lo atrapan si se equivoca, los comandos que lo guían y los registros que dejan evidencia.

---

## 1. Roles humanos

| Rol | Daniel | Juan |
|---|---|---|
| **Dueño de spec** (escribe código y tests, responde primero en la sustentación) | 002, 005, 006, 007 | 001, 003, 004, 008 |
| **Revisor obligatorio** (lee cada cambio del otro y debe poder explicarlo) | 001, 003, 004, 008 | 002, 005, 006, 007 |
| **Compartido** | 009 (documentación), diseño de casos mínimos, simulacros | 009, simulacros |

Reglas de trabajo en pareja:
1. **Rama por spec/tarea** (`feat/003-ucs`), PR hacia `main`, el otro revisa y aprueba. Así el historial evidencia aportes de cada uno.
2. **Revisión = explicación.** El revisor no aprueba hasta poder explicar el cambio en voz alta (o pasar 3 preguntas del examinador).
3. **Rotación de simulacro:** cada uno se examina sobre las specs **del otro**.
4. **Cada quien commitea con su cuenta.** La IA no commitea a nombre de nadie sin que esa persona lo pida.

> El reparto es una propuesta equilibrada por peso de rúbrica (Juan ≈ 50 %: 001+003+004+008; Daniel ≈ 50 %: 002+005+006+007). Ajústenlo en equipo y actualicen `AGENTS.md §2` y `specs/README.md`.

## 2. Roles de agentes (subagentes en `.claude/agents/`)

| Agente | Qué hace | Qué NO hace | Entrada → Salida |
|---|---|---|---|
| `arquitecto-specs` | Escribe/refina specs y ADRs a partir del PDF; detecta ambigüedades y las convierte en preguntas | No escribe código de producción | requisito/duda → spec actualizada + preguntas abiertas |
| `implementador` | Implementa **una** tarea de una spec aprobada: tests primero, código, docstrings con los 7 campos | No cambia el contrato JSON ni decisiones aceptadas; no commitea | spec + tarea → código + tests verdes + resumen "para sustentar" |
| `verificador` | Corre el arnés completo (pytest, casos, verificador, auditoría de docs, arquitectura) y reporta fallas con causa probable | No arregla código (reporta) | estado del repo → reporte ✔/✘ |
| `auditor-documentacion` | Revisa que docstrings describan el código **real**, que el uso de IA esté declarado y que `USO_IA.md` y el documento técnico estén al día | No inventa validaciones de estudiante | diff/módulo → lista de inconsistencias |
| `examinador-sustentacion` | Simula al profesor: pregunta, pide predicciones antes de ejecutar, propone modificaciones pequeñas y califica la respuesta | No da la respuesta antes de que el estudiante intente | spec/módulo → sesión de preguntas + retroalimentación |

**Flujo típico de una tarea:**
```
arquitecto-specs ─► (humanos aprueban spec) ─► implementador ─► verificador ─► auditor-documentacion
        ▲                                                                              │
        └──────────── dudas / cambios de diseño ◄────────── examinador-sustentacion ◄──┘
```

Comandos (`.claude/commands/`): `/nueva-spec`, `/implementar-spec NNN [tarea]`, `/verificar`, `/sustentacion NNN`.

## 3. Arneses

### A. Arnés de contexto (lo que lee el agente antes de actuar)
| Pieza | Función |
|---|---|
| `AGENTS.md` | Fuente de verdad: proyecto, stack, estructura, reglas duras, plantilla de docstring, flujo SDD |
| `CLAUDE.md` | Específico de Claude Code: rol de tutor, comandos permitidos, cuándo preguntar |
| `specs/000-constitucion.md` | Principios no negociables (P1–P12) |
| `specs/NNN-*/spec.md` | Requisitos, diseño, criterios de aceptación ↔ tests, tareas, preguntas de sustentación |
| `docs/DECISIONES.md` | Por qué el diseño es así (evita que un agente "rediseñe" sin querer) |
| `docs/Primer proyecto.pdf` | Autoridad final |

### B. Arnés de pruebas (`tests/`, pytest) — atrapa errores automáticamente
| Archivo | Qué garantiza | Spec |
|---|---|---|
| `test_escenario.py`, `test_validador.py` | Contrato JSON, 9 reglas, atomicidad, costos desde JSON | 001 |
| `test_reglas.py` | Reglas R1–R10, estado compuesto, invariantes, simetría | 002 |
| `test_busqueda_*.py`, `test_a_estrella.py`, `test_heuristicas.py` | Corrección, optimalidad contra Dijkstra, admisibilidad/consistencia/dominancia | 003, 004 |
| `test_utilidad.py`, `test_adversarial.py` | Suma cero, MM ≡ αβ, legalidad en el árbol | 005 |
| `test_verificador.py` | El oráculo detecta manipulaciones | 006 |
| `test_casos.py` | Los 10 casos mínimos: esperado vs obtenido | 008 |
| `test_arquitectura.py` | Nadie de capas inferiores importa `interfaz`; algoritmos no importan `json` | 000 P2 |
| `test_documentacion.py` | Métodos clave con los 7 campos; sin `PENDIENTE` al entregar (`-m entrega`) | 009 |
| `test_cli.py` | Comandos y precedencia de configuración | 007/008 |

Tipos de prueba usados: unitarias, **de propiedad** (estados alcanzables aleatorios con semilla fija ⇒ invariantes), **diferenciales** (UCS vs Dijkstra de referencia; Minimax vs αβ), **de contrato** (JSON del enunciado), **golden** (`esperado` en los casos).

### C. Arnés de verificación en ejecución
`tacticalgrid/verificacion/` + botón **Verificar** en la GUI + `--verificar` en la CLI + modo `auditar=True` en Minimax/αβ. Es lo que pide el enunciado y a la vez el oráculo de B.

### D. Arnés de experimentos (reproducibilidad)
`python -m tacticalgrid experimentos` regenera `resultados/` con cabecera (fecha, commit, Python, parámetros) y `RESUMEN.md` (✔/✘). Determinismo garantizado por P5.

### E. Arnés de agentes
- `.claude/agents/*.md` (roles de la sección 2) y `.claude/commands/*.md` (flujos repetibles).
- Política de permisos en `CLAUDE.md`: ejecutar tests/CLI libremente; preguntar antes de commit/push, borrar evidencia o cambiar el contrato.
- *Opcional:* hook `PostToolUse` que corra `pytest -q -x` tras editar `tacticalgrid/**` (configurable con `/hooks` en una terminal `claude`). Recomendado activarlo cuando exista la base de código.

### F. Arnés de aprendizaje y sustentación
`docs/GUIA_SUSTENTACION.md` + `/sustentacion NNN` + sección "Para sustentar" en cada spec + `docs/USO_IA.md`. Objetivo: que cada integrante pueda **predecir antes de ejecutar** y **modificar en vivo**.

## 4. Definición de "terminado" (DoD) para una tarea
- [ ] Criterios de aceptación de la tarea cubiertos por tests y en verde (`pytest -q`).
- [ ] Resultados de búsqueda/decisión pasan el verificador.
- [ ] Docstrings con los 7 campos y uso de IA declarado con precisión.
- [ ] Spec actualizada (`[x]`) y `docs/USO_IA.md` con la entrada correspondiente.
- [ ] El revisor explicó el cambio (o pasó el simulacro de 3 preguntas).
- [ ] Commit del autor con mensaje Conventional Commits.
