# 007 — Interfaz gráfica y visualización

| Campo | Valor |
|---|---|
| Estado | **implementada y corregida el 20 oct** · pruebas automáticas realizadas · revisión humana de correcciones por realizar |
| Responsable | Daniel · Revisor: Juan |
| Rúbrica | Interfaz y visualización (5 %) — pero es **la herramienta de la sustentación** |
| Depende de | 001 (crece con cada spec) |
| Fuente en el enunciado | "Visualización", "Resultados y métricas comparables" (p. 7) |

## 1. Contexto y porqué
La GUI no es el centro de la nota, pero en la sustentación el profesor cargará su JSON, pedirá ejecutar algoritmos, cambiará profundidad/orden y pedirá **predicciones antes de ejecutar**. La GUI debe permitir hacer todo eso **sin tocar código** y **ver** lo que pasa.

## 2. Requisitos
- **RF-007-1** Mostrar: cuadrícula, tipo de terreno (color + leyenda con costo), obstáculos, bases A/B, recurso, unidades con su id, bando de cada unidad, portador del recurso y turno actual.
- **RF-007-2** Cargar un JSON desde archivo (diálogo) mostrando la lista de errores de validación si es inválido (sin perder el escenario anterior).
- **RF-007-3** Búsqueda: elegir unidad/inicio y objetivo (desde `prueba` o con clic), algoritmo (BFS, DFS, UCS, A\*, Beam), heurística, k, orden de movimientos, tipo de problema (navegación / misión) ⇒ ver el **camino**.
- **RF-007-4** (Valorado) Ver estados **explorados** y animar automáticamente `orden_expansion`.
- **RF-007-5** Tabla comparativa de métricas que acumula ejecuciones (para comparar algoritmos en el mismo escenario) + exportar a JSON.
- **RF-007-6** Adversarial: elegir Minimax / alfa‑beta, profundidad, orden de acciones ⇒ ver acción sugerida (resaltada en el mapa), valor, métricas, tabla `valores_raiz` y desglose de la evaluación.
- **RF-007-7** Partida: controlar cada bando como Humano / Minimax / Alfa‑beta / Voraz; botones "Siguiente turno", "Jugar hasta el final", "Reiniciar". El historial completo se imprime en la CLI.
- **RF-007-8** Botón **Verificar** que muestra la lista de chequeos de lo último ejecutado, o valida el estado actual si ya se movió.
- **RF-007-9** Funciona con cualquier dimensión (tamaño de celda calculado según el área disponible).

## 3. Decisión (D‑10): `tkinter` + `ttk`
Stdlib, diálogo de archivos nativo, `Canvas` suficiente para una cuadrícula, `ttk.Treeview` para tablas. Alternativas: Pygame (sin widgets ni diálogo de archivos), Streamlit (incómodo para juego por turnos), web (otro stack). Ver `docs/DECISIONES.md`.

## 4. Diseño implementado

Un solo archivo `tacticalgrid/interfaz/app.py`, clase `App`. Lienzo a la izquierda, pestañas Búsqueda y Adversarial / Partida, tabla de métricas, detalle y exportación JSON. El clic fija el objetivo. La animación usa `after()`. La GUI llama a los mismos algoritmos y reglas que la CLI.

No se implementaron las propuestas iniciales de deshacer, exportar CSV desde la GUI, dibujar frontera, seleccionar una fila para recuperar su camino o controlar manualmente los pasos de animación. No son necesarias para ejecutar y comparar los algoritmos del enunciado.

## 5. Criterios de aceptación

- Carga válida sincroniza opciones; carga inválida conserva escenario y estado anteriores.
- La tabla permite comparar resultados del mismo escenario y se limpia al cargar otro.
- La cuadrícula usa el tamaño disponible del lienzo. En mapas densos los textos pueden perder legibilidad.
- Decidir, mover y verificar no reutilizan una decisión de un estado anterior.
- Pruebas: `tests/test_interfaz.py` y `tests/test_arquitectura.py`; manual en `docs/MANUAL_USUARIO.md`.

## 6. Tareas
- [x] T1 Lienzo + paleta + leyenda — implementado con Claude; revisa Juan
- [x] T2 Panel escenario (cargar / errores / info de turno y portador) — implementado con Claude; revisa Juan
- [x] T3 Panel búsqueda + animación + tabla de métricas — implementado con Claude; revisa Juan
- [x] T4 Panel adversarial (valores raíz, desglose) — implementado con Claude; revisa Juan
- [x] T5 Panel partida — implementado con Claude; revisa Juan
- [x] T6 Botón verificar + exportar — implementado con Claude; revisa Juan
- [x] T7 Capturas para el manual de usuario — Daniel (20 oct)

## Correcciones de auditoría (20 oct 2026)

Cargar sincroniza algoritmo, heurística, k, bloqueo, misión, profundidad y órdenes desde el JSON, restableciendo valores por defecto cuando se omiten. La carga es atómica también ante prueba mal formada. Al cambiar escenario se limpia la tabla; al jugar se descarta la decisión anterior. Verificar sin resultado comprueba el estado. Los controles inválidos muestran mensajes; no dejan excepciones de callbacks. Se muestran las cotas de alfa-beta y las métricas totales. El dibujo se adapta al tamaño real del lienzo; no se promete deshacer, frontera dibujada ni historial GUI que no se implementan.

Criterio de aceptación: regresiones en `tests/test_auditoria.py` y `tests/test_interfaz.py`, suite completa y diez casos mínimos aprobados.
