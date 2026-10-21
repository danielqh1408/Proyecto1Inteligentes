# Entrega de TacticalGrid — 21 de octubre de 2026

**Integrantes:** Daniel Quintero Hurtado y Juan David Ocampo González.
**Asignatura:** Sistemas Inteligentes I, Universidad de Caldas.
**Docente:** Jairo I. Vélez B.

## Archivos listos para entregar

| Entregable del enunciado | Ubicación |
|---|---|
| Repositorio y autores | [README](../README.md), historial Git real de ambos integrantes |
| Código e instalación | [tacticalgrid](../tacticalgrid/), [requirements.txt](../requirements.txt), README |
| Escenarios comunes, externos y casos mínimos | [escenarios](../escenarios/) |
| Manual de usuario | [PDF](../output/pdf/Manual_usuario_TacticalGrid.pdf) · [Markdown](MANUAL_USUARIO.md) |
| Documento técnico | [PDF](../output/pdf/Documento_tecnico_TacticalGrid.pdf) · [Markdown](DOCUMENTO_TECNICO.md) |
| Evidencia reproducible | [Resumen](../resultados/RESUMEN.md), CSV E1–E6 y [validación](../resultados/VALIDACION_ENTREGA.md) |
| Uso de IA | [USO_IA](USO_IA.md), sección 11 del informe y docstrings de métodos |
| Apoyo para la sustentación | [Guion PDF](../output/pdf/Guion_sustentacion_TacticalGrid.pdf) · [fuente](GUION_DEMO.md) |
| Rúbrica y trazabilidad | Sección 14 del documento técnico y [entendimiento](00_ENTENDIMIENTO.md) |
| Documento base | [Enunciado original](Primer%20proyecto.pdf) |

Los PDF se acompañan de fuentes editables y no sustituyen el repositorio. El enunciado pide manual y documento técnico; esta edición agrega PDF para facilitar lectura y entrega. Las figuras del informe provienen de datos reales en resultados/, no de ejemplos inventados.

## Versión y evidencia

El commit que contiene este índice, el código y los PDF identifica esta entrega. El tag histórico v1.0-sustentacion no corresponde a la versión corregida. El resumen experimental registra el commit base y cambios locales con que se regeneró; las huellas SHA-256 de los módulos y escenarios se guardan en resultados/MANIFIESTO_ENTREGA.json para vincular la evidencia al contenido exacto, independientemente del commit posterior de empaquetado.

La captura 08 fue aportada por Juan durante el ensayo y muestra la tabla actual. Las capturas 01–07 se conservan como historia; no se presentan como cifras vigentes. Los tiempos de la captura y de los CSV son ejecuciones distintas. Los conteos y resultados deterministas deben coincidir con igual configuración.

## Regeneración

Desde la raíz del proyecto, con el entorno de ejecución activo:

```bash
python -m pytest -o addopts='' -q
python -m tacticalgrid experimentos
```

Para documentos, use un entorno separado:

```bash
python3 -m venv .venv-docs
source .venv-docs/bin/activate
pip install -r herramientas/requirements-documentos.txt
python herramientas/generar_entregables.py
```

Esto genera los tres PDF en output/pdf y las figuras en docs/figuras a partir de Markdown y CSV. Si cambia código o escenarios, regenere primero las pruebas y experimentos y actualice la validación y el manifiesto antes de volver a emitir una entrega.

## Alcance de la comprobación

La edición actual aprobó 288 pruebas con Tk y los diez casos mínimos. Juan recorrió los casos durante el ensayo y confirmó la tabla visual. No se declara una revisión nueva de Daniel ni se garantiza la nota: la sustentación individual sigue siendo parte de la evaluación. Beam puede perder soluciones, la utilidad es aproximada y pueden repetirse tableros hasta el límite de turnos; estas limitaciones están documentadas.
