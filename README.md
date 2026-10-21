# TacticalGrid — Proyecto 1 de Sistemas Inteligentes I

Ingeniería de Sistemas y Computación · Universidad de Caldas · Primer corte

**Docente:** Jairo I. Vélez B.

## Entrega del proyecto

**Los documentos finales y el índice de todos los requisitos están en [entregables/](entregables/README.md).** El repositorio contiene el código, escenarios y evidencia para reproducir los experimentos; no es necesario descargar documentos de otro servicio.

- [Manual de usuario (PDF)](entregables/Manual_usuario_TacticalGrid.pdf).
- [Documento técnico (PDF)](entregables/Documento_tecnico_TacticalGrid.pdf).
- [Índice: requisito del enunciado y dónde encontrarlo](entregables/README.md).
- [Resultados y experimentos reproducibles](resultados/RESUMEN.md).

## Integrantes y aportes

| Integrante | GitHub |
|---|---|
| Daniel Quintero Hurtado | [danielqh1408](https://github.com/danielqh1408) |
| Juan David Ocampo González | [JuanGonzalezx](https://github.com/JuanGonzalezx) |

Los aportes se pueden consultar en el [historial real de commits](https://github.com/danielqh1408/Proyecto1Inteligentes/commits/main/) o con `git shortlog -sn HEAD` y `git log --format=fuller` tras clonar. No se atribuyen a cada integrante cambios distintos de los registrados.

## Qué implementa

Dos bandos compiten por recoger un recurso y llevarlo a su base sobre una cuadrícula con terrenos de distinto costo y obstáculos. La aplicación permite comparar BFS, DFS, UCS, A* con dos heurísticas admisibles, Beam Search y decisiones de Minimax con o sin poda alfa-beta.

El mapa, costos, unidades y configuración se leen del formato JSON común del enunciado. Las reglas y algoritmos están separados de la interfaz Tkinter. Los diez escenarios propios son de 20×20; también se acepta el ejemplo oficial de 4×4 y otras dimensiones válidas.

## Instalación y ejecución

Requiere Python 3.11 o superior. La interfaz necesita Tkinter; el núcleo utiliza la librería estándar.

```bash
git clone https://github.com/danielqh1408/Proyecto1Inteligentes.git
cd Proyecto1Inteligentes
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m tacticalgrid gui
```

En Windows, active el entorno con `.venv\Scripts\Activate.ps1` en PowerShell. Compruebe Tk con `python -m tkinter`. Si su Python de Homebrew no incluye Tk, instale el paquete correspondiente a esa versión, por ejemplo `python-tk@3.12` para Python 3.12. Más detalles en el [manual](entregables/Manual_usuario_TacticalGrid.pdf).

| Acción | Comando |
|---|---|
| Cargar un escenario en la GUI | `python -m tacticalgrid gui escenarios/ejemplo_enunciado.json` |
| Validar JSON | `python -m tacticalgrid validar escenarios/ejemplo_enunciado.json` |
| Ejecutar el modo del JSON | `python -m tacticalgrid ejecutar escenarios/ejemplo_enunciado.json` |
| Navegación UCS con verificación | `python -m tacticalgrid buscar escenarios/casos/caso02_ruta_corta_vs_economica.json --algoritmo UCS --verificar` |
| Decisión alfa-beta | `python -m tacticalgrid decidir escenarios/casos/caso08_minimax_vs_alfabeta.json --algoritmo ALFA_BETA --profundidad 4 --verificar` |
| Ayuda de todos los comandos | `python -m tacticalgrid --help` |

## Reproducción de resultados

```bash
python -m pytest -o addopts='' -q
python -m tacticalgrid experimentos --salida resultados/tmp/reproduccion
```

La revisión registrada aprobó **288 pruebas con Tk y los diez casos mínimos**. El comando de experimentos genera RESUMEN.md y seis CSV en una carpeta separada, conservando la evidencia entregada. Con igual código y escenarios deben coincidir los resultados y conteos, no necesariamente los tiempos.

El procedimiento completo, los parámetros de E1–E6 y cómo comparar la salida se encuentran en la **sección 10 del manual** y la **sección 15 del documento técnico**. La evidencia está en [resultados/](resultados/) y la comprobación realizada en [VALIDACION_ENTREGA.md](resultados/VALIDACION_ENTREGA.md).

## Estructura

| Carpeta | Contenido |
|---|---|
| [entregables/](entregables/README.md) | PDF finales e índice de requisitos. |
| [tacticalgrid/](tacticalgrid/) | Código fuente completo. |
| [escenarios/](escenarios/) | JSON, diez casos mínimos, ejemplo oficial y archivos inválidos de prueba. |
| [resultados/](resultados/) | CSV E1–E6, resumen, validación y huellas del código/escenarios. |
| [docs/](docs/) | Fuentes editables del manual e informe, arquitectura, decisiones, capturas, figuras y uso de IA. |
| [specs/](specs/README.md) | Especificaciones y criterios de aceptación. |
| [tests/](tests/) | Pruebas de algoritmos, reglas, carga, verificación, documentación e interfaz. |
| [herramientas/](herramientas/) | Generación de documentos; dependencias separadas del juego. |

## Uso de IA generativa

Claude Code, Gemini y Codex apoyaron implementación, revisión, pruebas y documentación. Se declara en [docs/USO_IA.md](docs/USO_IA.md), en el informe y en los campos AI usage, AI intervention y Student validation de los métodos. La validación automática no sustituye la responsabilidad y comprensión de los integrantes.
