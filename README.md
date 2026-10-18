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

> ⚠️ El código está en construcción siguiendo las specs de `specs/`. Los comandos de abajo son el contrato objetivo.

```bash
git clone git@github.com:danielqh1408/Proyecto1Inteligentes.git
cd Proyecto1Inteligentes
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

| Acción | Comando |
|---|---|
| Interfaz gráfica | `python -m tacticalgrid gui` (o `gui ruta/escenario.json`) |
| Validar un escenario JSON | `python -m tacticalgrid validar ruta/escenario.json` |
| Ejecutar la prueba que indica `prueba.modo` | `python -m tacticalgrid ejecutar ruta/escenario.json` |
| Búsqueda puntual | `python -m tacticalgrid buscar ruta.json --algoritmo A_ESTRELLA --heuristica obstaculos` |
| Decisión adversarial | `python -m tacticalgrid decidir ruta.json --algoritmo ALFA_BETA --profundidad 4` |
| Regenerar todos los experimentos | `python -m tacticalgrid experimentos` |
| Pruebas automáticas | `pytest -q` |

macOS con Python de Homebrew: instalar Tk con `brew install python-tk@3.12`.

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
| [docs/USO_IA.md](docs/USO_IA.md) | Registro honesto del uso de IA generativa |
| [specs/](specs/README.md) | Especificaciones 000–009 |
| `docs/MANUAL_USUARIO.md` · `docs/DOCUMENTO_TECNICO.md` | Entregables finales (se completan al implementar) |

## 🤖 Uso de IA generativa

Se usa **Claude Code (Anthropic)** como apoyo para estructurar la documentación SDD, las especificaciones y, más adelante, partes del código. Todo uso queda registrado en [docs/USO_IA.md](docs/USO_IA.md) y en la documentación de cada método (campos *AI usage / AI intervention / Student validation*). Ambos integrantes son responsables de explicar y modificar cualquier parte de la solución.
