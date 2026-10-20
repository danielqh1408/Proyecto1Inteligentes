# Documento técnico — TacticalGrid

> **Esqueleto.** Por la política de `docs/USO_IA.md`, el análisis se redacta **con nuestras palabras**. Debajo de cada sección hay: lo que exige el enunciado, dónde están los datos y las preguntas que la sección debe responder. Borren estas notas al redactar.
> Integrantes: Daniel Quintero Hurtado · Juan David Ocampo González. Versión: tag `v1.0-sustentacion`.

## 1. Modelado del problema
- Fuente: `specs/002-modelo-estado-reglas/spec.md` §1–3.
- Responder: ¿qué es un problema de búsqueda aquí (navegación y misión) y qué es la partida adversarial? ¿Qué es fijo (escenario) y qué cambia (estado)?

## 2. Representación de estados
- Fuente: `juego/estado.py`, spec 002 §3.1, caso 6 (`resultados/RESUMEN.md`).
- Responder: los 5 campos de `EstadoJuego` y por qué cada uno es necesario; el estado `((f, c), lleva)` de la misión; por qué `(fila, columna)` no basta.

## 3. Reglas del juego
- Fuente: spec 002 §3.3 (R1–R10), `docs/DECISIONES.md` D‑14.
- Responder: turnos, movimiento, recoger, interceptar (por qué el recurso y el antiguo portador vuelven a su posición inicial: propuesta de Daniel, D‑14), base enemiga, bloqueo, empate. Mismas reglas para ambos bandos.

## 4. Costos
- Fuente: `Escenario.costo`, E3 (`resultados/E3_sensibilidad.csv`).
- Responder: costo = entrar a la celda; vienen del JSON; qué pasa con BFS y UCS al cambiar el pantano (E3: con costo ≥ 3, UCS toma el rodeo).

## 5. Heurísticas
- Fuente: spec 004 §3, `busqueda/heuristicas.py`, casos 3 y 4, `tests/test_busqueda.py::test_admisible_consistente_y_dominancia`.
- Para **cada** heurística (manhattan y obstaculos), las 5 preguntas del enunciado: qué estima, qué información usa, costo computacional, admisibilidad (y por qué), dónde orienta bien y dónde pierde discriminación. Por qué se multiplica por c_min. H3 no admisible (caso 2: costo 83 vs 33).

## 6. Función de utilidad
- Fuente: spec 005 §3–4, `adversarial/utilidad.py`.
- Responder: perspectiva MAX/MIN y por qué MIN no está en desventaja (suma cero); los 3 componentes y sus pesos; por qué se descartó la versión de 5 componentes (no monótona); qué pasa al cambiar los pesos.

## 7. Metodología experimental
- Fuente: spec 008, `tacticalgrid/experimentos/`, `escenarios/casos/`.
- Responder: escenarios usados (10 casos ≥ 20×20 + mapa simétrico), métricas y su definición exacta (spec 003 §3, spec 005 §5), cómo reproducir (`python -m tacticalgrid experimentos`), qué es determinista y qué no (tiempo).

## 8. Resultados
- Fuente: `resultados/RESUMEN.md` y CSV E1–E6.
- Interpretar con nuestras palabras: casos 1–10 (esperado vs obtenido), Beam con k (E2), sensibilidad al costo (E3), profundidad (E4), orden y poda (E5), torneo (E6).

## 9. Análisis de complejidad
- Fuente: los campos *Complexity* de los docstrings; spec 003 §5; spec 005 §5.
- Tabla tiempo/espacio de BFS, DFS, UCS, A\*, Beam, Minimax y alfa‑beta (mejor y peor orden), validador y evaluación; comparar con los números de E4/E5.

## 10. Limitaciones
- Ideas a discutir: unidades idénticas; horizonte limitado de Minimax; empates entre agentes de igual profundidad (E6); Beam con visitados global; la heurística propia no considera costos de terreno; sin tabla de transposiciones; tiempos medidos en un solo computador.

## 11. Reporte del uso de IA
- Fuente: `docs/USO_IA.md` y los campos *AI usage / AI intervention / Student validation* de los docstrings.
- Responder: herramienta, en qué partes intervino, qué decisiones cambiamos nosotros, cómo validamos cada parte.
