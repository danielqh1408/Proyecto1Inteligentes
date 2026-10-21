# TacticalGrid — Juego táctico 2D con búsqueda y toma de decisiones

**Proyecto 1 · Sistemas Inteligentes I · Primer corte**
Ingeniería de Sistemas y Computación — Universidad de Caldas · Docente: Jairo I. Vélez B.

## 👥 Integrantes

| Nombre | Correo | GitHub |
|---|---|---|
| **Daniel Quintero Hurtado** | danielqh321@gmail.com | [@danielqh1408](https://github.com/danielqh1408) |
| **Juan David Ocampo González** | juan.ocampo38402@ucaldas.edu.co | [@JuanGonzalezx](https://github.com/JuanGonzalezx) |

---

## 🎯 ¿Qué es?

Dos bandos (A y B), con al menos tres unidades cada uno, compiten por turnos sobre una cuadrícula con terrenos de distinto costo y obstáculos. En una zona neutral hay un **recurso**: gana el bando que lo lleve primero a su **base**.

El juego es solo el **entorno de experimentación**. Lo que se evalúa es el **sistema inteligente** que decide dentro de él, y cómo cambia su forma de decidir:

| Etapa | Pregunta | Algoritmos |
|---|---|---|
| 1. Búsqueda no informada | ¿Existe una ruta? | BFS, DFS |
| 2. Búsqueda por costo | ¿Cuál es la ruta más **barata**? | Costo Uniforme (UCS) |
| 3. Búsqueda informada | ¿Puedo usar conocimiento para buscar menos? | A\* (Manhattan + heurística propia), Beam Search (k = 1, 2, 4, 8) |
| 4. Decisión adversarial | ¿Cuál es mi mejor **acción** si el rival también razona? | Minimax, Minimax con poda alfa‑beta |

## 🚀 Instalación y ejecución

> Estado (20 oct 2026): correcciones de auditoría, diez casos mínimos cumplidos y experimentos regenerados. 284 pruebas sin Tk + 4 de interfaz con Tk. El tag `v1.0-sustentacion` corresponde a la versión anterior; la revisión corregida se identifica por el commit de `main`. La revisión humana se realiza con las guías actualizadas.

```bash
git clone git@github.com:danielqh1408/Proyecto1Inteligentes.git
cd Proyecto1Inteligentes
python3 -m venv .venv            # Python 3.11+
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

| Acción | Comando |
|---|---|
| Interfaz gráfica | `python -m tacticalgrid gui` (o `gui ruta/escenario.json`) |
| Validar un escenario JSON | `python -m tacticalgrid validar ruta/escenario.json` |
| Ejecutar la prueba que indica `prueba.modo` | `python -m tacticalgrid ejecutar ruta/escenario.json` |
| Búsqueda puntual | `python -m tacticalgrid buscar ruta.json --algoritmo A_ESTRELLA --heuristica obstaculos --verificar` |
| Comparar todos los algoritmos | `python -m tacticalgrid comparar ruta.json` |
| Decisión adversarial | `python -m tacticalgrid decidir ruta.json --algoritmo ALFA_BETA --profundidad 4 --verificar` |
| Partida completa | `python -m tacticalgrid partida ruta.json --a alfa_beta --b voraz --profundidad 3` |
| Regenerar todos los experimentos | `python -m tacticalgrid experimentos` |
| Pruebas automáticas | `pytest -q` |

macOS con Python de Homebrew: instalar Tk con `brew install python-tk@3.12`, o usar el Python de uv (`uv venv -p 3.11 .venv`), que ya trae Tk.

Manual completo: [docs/MANUAL_USUARIO.md](docs/MANUAL_USUARIO.md). Resultados de los experimentos: [resultados/RESUMEN.md](resultados/RESUMEN.md).

## 🗂️ Estructura

```
├── AGENTS.md / CLAUDE.md   # contexto e instrucciones para agentes de IA (SDD)
├── specs/                  # especificaciones por funcionalidad (fuente del diseño)
├── docs/                   # entendimiento, arquitectura, decisiones, manual, documento técnico, uso de IA
├── tacticalgrid/           # código fuente
├── escenarios/             # escenarios JSON (ejemplo del enunciado, casos mínimos, inválidos)
├── resultados/             # evidencia reproducible de los experimentos
└── tests/                  # pruebas automáticas
```

## 📚 Documentación

| Documento | Para qué |
|---|---|
| ⭐ [docs/01_LEEME_DANIEL.md](docs/01_LEEME_DANIEL.md) | **Empezar aquí:** metodología de trabajo explicada y decisiones a tomar en equipo |
| [docs/00_ENTENDIMIENTO.md](docs/00_ENTENDIMIENTO.md) | Qué pide el enunciado, explicado, y trazabilidad requisito → spec → código |
| [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md) | Capas, módulos, flujo de datos |
| [docs/DECISIONES.md](docs/DECISIONES.md) | Decisiones abiertas del enunciado y cómo las resolvimos (con justificación) |
| [docs/ROLES_Y_ARNESES.md](docs/ROLES_Y_ARNESES.md) | Reparto de trabajo, roles de agentes y arneses de verificación |
| [docs/GUIA_SUSTENTACION.md](docs/GUIA_SUSTENTACION.md) | Banco de preguntas y cómo prepararnos |
| ⭐ [docs/ESTUDIO_PRESENTACION.md](docs/ESTUDIO_PRESENTACION.md) | Plan de estudio, guion de la presentación grupal (20 min), demo y preguntas con respuesta |
| [docs/USO_IA.md](docs/USO_IA.md) | Registro honesto del uso de IA generativa |
| [specs/](specs/README.md) | Especificaciones 000–009 |
| [docs/MANUAL_USUARIO.md](docs/MANUAL_USUARIO.md) | Manual de usuario con capturas |
| [docs/DOCUMENTO_TECNICO.md](docs/DOCUMENTO_TECNICO.md) | Documento técnico (modelado, heurísticas, utilidad, resultados, complejidad, limitaciones, uso de IA) |
| [resultados/RESUMEN.md](resultados/RESUMEN.md) | Casos mínimos (esperado vs obtenido) y experimentos E1–E6 |

## Entrega del 21 de octubre

- [Índice y comprobación de entregables](docs/ENTREGA.md).
- [Manual de usuario en PDF](output/pdf/Manual_usuario_TacticalGrid.pdf) y [fuente editable](docs/MANUAL_USUARIO.md).
- [Documento técnico en PDF](output/pdf/Documento_tecnico_TacticalGrid.pdf), con gráficas y trazabilidad de la rúbrica; [fuente](docs/DOCUMENTO_TECNICO.md).
- [Guion breve de sustentación en PDF](output/pdf/Guion_sustentacion_TacticalGrid.pdf) y [fuente](docs/GUION_DEMO.md).
- [Validación de entrega](resultados/VALIDACION_ENTREGA.md): suite completa, casos y evidencia reproducible.

La tabla de métricas cambia con la pestaña: Búsqueda o Adversarial / Partida. Cada consulta de Decidir agrega una fila; al mover o reiniciar se limpia la comparación adversarial. Los PDF se regeneran con `python herramientas/generar_entregables.py`, instalando antes `herramientas/requirements-documentos.txt` en un entorno documental separado. El juego no depende de esas bibliotecas.

## 🤖 Uso de IA generativa

Se usaron **Claude Code**, **Gemini** y **Codex** como apoyo en implementación, revisión, pruebas y documentación. Todo uso queda registrado en [docs/USO_IA.md](docs/USO_IA.md) y en la documentación de cada método (campos *AI usage / AI intervention / Student validation*). Ambos integrantes son responsables de explicar y modificar cualquier parte de la solución.
