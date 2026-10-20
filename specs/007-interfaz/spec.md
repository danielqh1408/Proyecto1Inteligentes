# 007 — Interfaz gráfica y visualización

| Campo | Valor |
|---|---|
| Estado | **implementada** · revisada por Daniel (20 oct) · falta la revisión de Juan antes de la sustentación |
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
- **RF-007-4** (Valorado) Ver estados **explorados** y la **frontera**; animación paso a paso del `orden_expansion`.
- **RF-007-5** Tabla comparativa de métricas que acumula ejecuciones (para comparar algoritmos en el mismo escenario) + exportar a JSON/CSV.
- **RF-007-6** Adversarial: elegir Minimax / alfa‑beta, profundidad, orden de acciones ⇒ ver acción sugerida (resaltada en el mapa), valor, métricas, tabla `valores_raiz` y desglose de la evaluación.
- **RF-007-7** Partida: controlar cada bando como Humano / Minimax / Alfa‑beta / Voraz; botones "Siguiente turno", "Jugar hasta el final", "Deshacer"; historial de jugadas.
- **RF-007-8** Botón **Verificar** que muestra el `ReporteVerificacion` de lo último ejecutado.
- **RF-007-9** Funciona con cualquier dimensión (tamaño de celda calculado según el área disponible).

## 3. Decisión (D‑10): `tkinter` + `ttk`
Stdlib, diálogo de archivos nativo, `Canvas` suficiente para una cuadrícula, `ttk.Treeview` para tablas. Alternativas: Pygame (sin widgets ni diálogo de archivos), Streamlit (incómodo para juego por turnos), web (otro stack). Ver `docs/DECISIONES.md`.

## 4. Diseño

> **Implementado (un solo archivo):** `tacticalgrid/interfaz/app.py` (~330 líneas) con la clase `App`. Lienzo a la izquierda; pestañas *Búsqueda* y *Adversarial / Partida* a la derecha; tabla de métricas acumulada, exportar a JSON, cuadro de texto con resultados y botón **Verificar**. Clic en el mapa = objetivo de la búsqueda. Animación de la exploración con `after()`. Partida: cada bando puede ser HUMANO (lista de acciones legales), MINIMAX, ALFA_BETA o VORAZ. Comando: `python -m tacticalgrid gui [json]`.
> Probado con la ventana oculta (todos los botones, sin errores de callbacks). **Falta revisión visual humana.**
> Para ejecutar en macOS: el Python de Homebrew no trae Tk (`brew install python-tk@3.12`); el Python que instala `uv` sí lo trae (`uv venv -p 3.11`).
>
> Bosquejo original (se simplificó a un archivo):
```
tacticalgrid/interfaz/
├── app.py            # ventana principal, EstadoAplicacion (escenario activo, resultados)
├── lienzo.py         # dibujo de la cuadrícula y capas (terreno, explorados, frontera, camino, unidades)
├── panel_escenario.py
├── panel_busqueda.py
├── panel_adversarial.py
├── panel_partida.py
└── paleta.py         # colores por terreno (asignación determinista por nombre; no supone nombres fijos)
```
- Layout: lienzo a la izquierda; a la derecha un `ttk.Notebook` con pestañas *Escenario · Búsqueda · Adversarial · Partida · Métricas*.
- **La interfaz solo llama funciones públicas** de `busqueda`, `adversarial`, `verificacion`, `experimentos`. Ninguna lógica de IA vive aquí (P2).
- Colores de terreno: tabla para nombres conocidos (camino, pasto, bosque, pantano, muro) y color derivado del hash del nombre para terrenos desconocidos del profesor; obstáculos siempre oscuros. Leyenda con nombre y costo leídos del JSON.
- Capas: explorados (tono claro), frontera final (borde), camino (línea con flechas), acción adversarial sugerida (flecha resaltada).
- Animación con `after()` y velocidad ajustable; botón "paso" para avanzar manualmente.

## 5. Criterios de aceptación
- **CA-007-1** Cargar `ejemplo_enunciado.json` dibuja 4×4 con leyenda de 5 terrenos y 4 unidades etiquetadas. (manual + captura en `docs/capturas/`)
- **CA-007-2** Cargar un inválido muestra todos los errores y el mapa anterior sigue visible. (manual)
- **CA-007-3** Ejecutar BFS y UCS en el caso 2 deja ambas filas en la tabla de métricas y ambos caminos se pueden alternar. (manual)
- **CA-007-4** Un mapa 40×60 se ve completo sin barras de desplazamiento en 1366×768. (manual)
- **CA-007-5** `tests/test_interfaz_import.py` verifica que `tacticalgrid.interfaz` no es importado por ningún módulo de capas inferiores (prueba de arquitectura).

## 6. Tareas
- [x] T1 Lienzo + paleta + leyenda — implementado con Claude; revisa Juan
- [x] T2 Panel escenario (cargar / errores / info de turno y portador) — implementado con Claude; revisa Juan
- [x] T3 Panel búsqueda + animación + tabla de métricas — implementado con Claude; revisa Juan
- [x] T4 Panel adversarial (valores raíz, desglose) — implementado con Claude; revisa Juan
- [x] T5 Panel partida — implementado con Claude; revisa Juan
- [x] T6 Botón verificar + exportar — implementado con Claude; revisa Juan
- [x] T7 Capturas para el manual de usuario — Daniel (20 oct)
