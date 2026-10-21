# Validación de entrega — 21 de octubre de 2026

Comprobaciones realizadas por Codex a solicitud de Juan. Esta evidencia automática no certifica dominio individual ni garantiza una calificación.

| Comprobación | Resultado |
|---|---|
| Suite completa con Python 3.11.16 y Tk, `python -m pytest -o addopts='' -q` | 288 aprobadas, sin omisiones. Incluye las 31 comprobaciones marcadas entrega. |
| `python -m tacticalgrid experimentos` | Diez casos mínimos aprobados; RESUMEN.md y E1–E6 regenerados. |
| Comparación CSV contra la revisión previa | Todas las columnas no temporales de E1–E6 idénticas; tiempos variables. |
| Tabla adversarial | Cinco consultas de profundidades 1–5 conservan turno 0; exportación JSON de cinco filas correcta. |
| Pestañas y limpieza | Cada pestaña mantiene su tabla; limpiar Búsqueda no borra Adversarial; reiniciar limpia la tabla adversarial. |
| Manual PDF | 9 páginas; imagen real actual, instrucciones, diez casos, verificación y límites. |
| Documento técnico PDF | 16 páginas; tablas, dos figuras de CSV y matriz de rúbrica. |
| Integridad documental | Texto extraído, nombres de ambos autores presentes, sin caracteres de sustitución; páginas renderizadas para revisión visual. |

## Procedencia

- Fuentes de PDF: docs/MANUAL_USUARIO.md, docs/DOCUMENTO_TECNICO.md.
- Generador: herramientas/generar_entregables.py; dependencias documentales independientes en herramientas/requirements-documentos.txt.
- Figuras: resultados/E4_profundidad.csv y E5_orden.csv. No se representan mediciones inventadas.
- Captura: docs/capturas/08_tabla_profundidad_actual.png, aportada por Juan durante su ensayo. No se usaron capturas históricas como evidencia actual.
- MANIFIESTO_ENTREGA.json contiene SHA-256 de los módulos Python y escenarios validados. El commit que incorpora la entrega fija también los documentos y los CSV.

## Revisión humana y límites

Juan ejecutó y discutió los casos 1–10 y confirmó visualmente la tabla. No se presume revisión de Daniel posterior al registro histórico, ni revisión línea por línea del código por Juan. La revisión de PDF fue realizada por Codex; no se atribuye a los estudiantes una lectura posterior aún no realizada.

Se documentan la incompletitud de Beam, el costo adicional del orden heurístico, la utilidad aproximada, las repeticiones hasta el límite de turnos y el alcance de la verificación de decisiones en la raíz. La verificación de caminos no demuestra por sí sola optimalidad; esta se contrasta con algoritmos de referencia y pruebas.

## Organización y reproducción final

Los dos PDF finales están en entregables/, junto a un índice que relaciona cada requisito con su archivo. El README principal enlaza esa carpeta. Se ejecutó el procedimiento documentado con --salida resultados/tmp/reproduccion: los diez casos cumplieron y las columnas no temporales de los seis CSV coincidieron con las entregadas. Las huellas del manifiesto siguen coincidiendo con código y escenarios. Se verificaron los enlaces y la exclusión del material privado de la versión actual de Git, conservando sus archivos locales.
