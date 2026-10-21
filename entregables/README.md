# Entregables — TacticalGrid

**Proyecto 1 · Sistemas Inteligentes I · Universidad de Caldas**

**Integrantes:** Daniel Quintero Hurtado y Juan David Ocampo González. Docente: Jairo I. Vélez B.

Esta carpeta es el punto de entrada de la entrega. Desde el enlace del repositorio se accede a todos los archivos y evidencias solicitados. Los documentos finales están aquí; el código, escenarios y datos permanecen en sus carpetas para ejecutarlos directamente.

## Dónde encontrar cada requisito del enunciado

| Requisito | Archivo o ubicación |
|---|---|
| Repositorio Git con evidencia de aportes de ambos integrantes | [Historial de commits](https://github.com/danielqh1408/Proyecto1Inteligentes/commits/main/). También puede ejecutar `git shortlog -sn HEAD` y `git log --format=fuller`. El registro conserva las autorías reales. |
| README con nombres de integrantes | [README principal](../README.md), sección Integrantes. |
| Código fuente completo | [tacticalgrid/](../tacticalgrid/), organizado en escenario, juego, búsqueda, adversarial, interfaz, verificación y experimentos. |
| Instalación y ejecución | [README principal](../README.md) y sección 1 del [manual](Manual_usuario_TacticalGrid.pdf). Dependencias en [requirements.txt](../requirements.txt). |
| Escenarios JSON y casos mínimos | [escenarios/](../escenarios/); diez casos en [escenarios/casos/](../escenarios/casos/), ejemplo oficial y escenarios inválidos de validación. |
| Manual de usuario | [Manual_usuario_TacticalGrid.pdf](Manual_usuario_TacticalGrid.pdf). Incluye instalación, controles, captura real, verificación y procedimiento de reproducción. [Fuente editable](../docs/MANUAL_USUARIO.md). |
| Documento técnico | [Documento_tecnico_TacticalGrid.pdf](Documento_tecnico_TacticalGrid.pdf). Incluye todos los temas enumerados abajo, gráficas y trazabilidad de rúbrica. [Fuente editable](../docs/DOCUMENTO_TECNICO.md). |
| Evidencia suficiente para reproducir experimentos | [resultados/RESUMEN.md](../resultados/RESUMEN.md), [CSV E1–E6](../resultados/), [validación](../resultados/VALIDACION_ENTREGA.md) y [runner](../tacticalgrid/experimentos/reporte.py). Procedimiento completo en sección 10 del manual y 15 del informe. |

## Contenido del documento técnico

| Tema solicitado | Sección del informe |
|---|---|
| Modelado del problema | 1 |
| Representación de estados | 2 |
| Reglas deterministas y estructuras de algoritmos | 3 |
| Costos | 4 |
| Heurísticas y justificación | 5 |
| Función de utilidad y MAX/MIN | 6 |
| Metodología experimental y métricas | 7 |
| Resultados e interpretación | 8 |
| Análisis de complejidad | 9 |
| Limitaciones | 10 |
| Reporte del uso de IA | 11, junto al [registro completo](../docs/USO_IA.md) y los docstrings |
| Contrato JSON, verificación e interfaz | 12 |
| Figuras derivadas de los experimentos | 13 |
| Correspondencia con la rúbrica | 14 |
| Reproducción de la evidencia y comparación automática | 15 |

## Reproducir sin sobrescribir la evidencia entregada

Desde la raíz del repositorio, con el entorno Python activo:

```bash
python -m pytest -o addopts='' -q
python -m tacticalgrid experimentos --salida resultados/tmp/reproduccion
```

El primer comando incluye las comprobaciones documentales de entrega. El segundo ejecuta los diez casos y E1–E6, guardando un resumen y CSV nuevos en la carpeta indicada. Compare las columnas no temporales con los archivos de resultados/: los tiempos pueden variar por equipo y caché. La sección 15 del informe incluye el código de comparación automática y los parámetros de cada experimento.

La validación registrada aprobó 288 pruebas con Tk y los diez casos. [MANIFIESTO_ENTREGA.json](../resultados/MANIFIESTO_ENTREGA.json) contiene las huellas del código y de los escenarios validados. El commit que incorpora esta carpeta identifica la versión de entrega; los tags históricos no sustituyen esa identificación.

## Fuentes y regeneración de documentos

Las fuentes Markdown se conservan en docs/ y las figuras se obtienen de E4/E5. Para reconstruir los dos PDF en esta carpeta:

```bash
python3 -m venv .venv-docs
source .venv-docs/bin/activate
pip install -r herramientas/requirements-documentos.txt
python herramientas/generar_entregables.py
```

Las dependencias documentales son independientes de las del juego. La captura del manual es una ejecución real aportada por Juan; sus tiempos no tienen que coincidir con otra ejecución de los CSV. Las notas privadas de preparación no forman parte de esta entrega. La declaración de IA y sus limitaciones se mantienen publicadas.
