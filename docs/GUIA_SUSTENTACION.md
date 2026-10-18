# Guía de sustentación

> La sustentación es **individual** y vale **50 %**. Cada uno debe explicar **cualquier** parte, aunque no la haya escrito. Esta guía crece a medida que se implementa: cuando una spec pase a ✅, se completa su sección con rutas reales de código (`archivo.py:línea`).

## 1. Lo que el enunciado dice que pueden pedirnos
1. Explicar la representación de un estado.
2. Ejecutar BFS, DFS, UCS, A\* o Beam sobre un escenario **externo**.
3. Justificar una heurística y discutir su admisibilidad.
4. Explicar una decisión de Minimax y la función de utilidad.
5. Explicar por qué MIN no está en desventaja frente a MAX.
6. Analizar el efecto de cambiar la profundidad o el orden de acciones.
7. Explicar la complejidad de un método.
8. Explicar el uso de IA declarado y la validación realizada.
9. Hacer una modificación pequeña al código.

Y pruebas de adaptación: cambiar costos, mover obstáculos/bases/unidades/recurso, cambiar el objetivo, la profundidad, el orden; **predecir antes de ejecutar**.

## 2. Banco de preguntas con respuesta corta

### Modelado (spec 002)
- **¿Qué es un estado en su juego?** → `EstadoJuego`: posiciones de las unidades, portador, posición del recurso si está libre, turno y turnos jugados. Lo fijo (terreno, costos, bases, identidad de unidades) está en `Escenario`.
- **¿Por qué no basta `(fila, columna)`?** → Con varias unidades, turnos y posesión, la misma casilla puede corresponder a situaciones con acciones y valores distintos (caso 6).
- **¿Qué acciones hay?** → MOVER (4 direcciones), INTERCEPTAR (adyacente al portador enemigo), PASAR (solo si no hay otra).
- **¿Qué pasa si no hay ruta?** → `exito = false` con métricas; no es un error.

### Búsqueda no informada y costo (spec 003)
- **BFS vs DFS:** cola vs pila; BFS óptimo en número de movimientos; DFS depende del orden de sucesores y no es óptimo.
- **¿Por qué BFS y UCS dan caminos distintos en el caso 2?** → BFS minimiza pasos; UCS minimiza Σ costos: prefiere un rodeo largo por camino (costo 1) a cruzar pantano (costo 7).
- **Generados vs expandidos:** generado = entra a la frontera; expandido = sale y se le calculan sucesores.
- **Complejidad UCS:** O((V+E) log V) con heap.

### Heurísticas, A\* y Beam (spec 004)
- **¿Qué estima su heurística propia?** → El costo mínimo restante en un mapa relajado donde se respetan los muros pero todo cuesta c_min.
- **¿Es admisible? ¿Por qué?** → Todo camino real tiene al menos pasos_BFS movimientos y cada uno cuesta ≥ c_min.
- **¿Dónde falla?** → Mapas abiertos (igual a Manhattan) y mapas donde lo que importa es el costo del terreno.
- **¿Por qué multiplicar por c_min?** → Si un terreno cuesta < 1, la Manhattan pura sobreestima.
- **Beam con k=1 vs k=8:** k pequeño = poca memoria, pero puede descartar el único sucesor que llevaba al buen camino; con `visitados` global no se recupera.

### Adversarial (spec 005)
- **¿Por qué esta acción vale más?** → `python -m tacticalgrid decidir <json>`: valor de cada acción de la raíz y desglose (posesión, carrera, movilidad) del estado elegido.
- **¿Por qué MIN no está en desventaja?** → Mismas reglas; la evaluación es de suma cero, `E_A = −E_B`; minimizar E_A es maximizar E_B.
- **¿Por qué αβ da la misma decisión?** → Solo poda ramas que no pueden cambiar el valor de la raíz; desempate por la primera acción estrictamente mejor.
- **Efecto del orden de acciones:** cambia cuántas ramas se podan, no el resultado. Mejor caso ≈ O(b^(m/2)).
- **Efecto de la profundidad:** nodos crecen ~b por nivel; la acción puede cambiar al ver más lejos (efecto horizonte).

## 3. Ejercicios de predicción (hacerlos ANTES de ejecutar)
| # | Cambio | Predicción esperada |
|---|---|---|
| P1 | Pantano 7 → 15 | BFS igual; UCS/A\* evitan más el pantano; costo óptimo ≥ anterior; expandidos de UCS pueden subir |
| P2 | Pantano 7 → 1 | UCS puede cruzar el pantano; BFS y UCS podrían coincidir |
| P3 | Quitar el muro del caso 3 | H1 y H2 se igualan (mismos expandidos) |
| P4 | Invertir orden de movimientos | BFS: misma longitud; DFS: camino distinto |
| P5 | Profundidad 2 → 4 | Más nodos (~b²), más tiempo; la acción puede cambiar |
| P6 | Orden `heuristico` en vez de `natural` | Más podas, misma acción y valor |
| P7 | `juego.pesos_utilidad = {"carrera": 0}` en el caso 7 | Solo cuenta posesión y movilidad: la IA deja de acercarse al recurso o al portador mientras no pueda tomarlo dentro del horizonte |
| P8 | Mover el recurso junto a la base de B | B gana rápido; Minimax de A prioriza bloquear/interceptar |

## 4. Modificaciones pequeñas que hay que saber hacer en vivo
- Agregar diagonales a `orden_movimientos` (¡y explicar por qué Manhattan dejaría de ser admisible!).
- Cambiar la prueba de objetivo de BFS a "al generar" y explicar el efecto en las métricas.
- Agregar un componente nuevo a la utilidad (p. ej. distancia de los defensores a la base propia).
- Cambiar el criterio de Beam de h a f.
- Imprimir el árbol de Minimax hasta profundidad 2 (versión `*_debug` como en clase).
- Agregar una regla de validación nueva.

## 5. Mapa "dónde está cada cosa" (código real, 18 oct)
| Pregunta del profesor | Archivo:línea |
|---|---|
| Representación del estado | [`juego/estado.py:16`](../tacticalgrid/juego/estado.py) `EstadoJuego` (5 campos) |
| Estado inicial | `juego/estado.py:37` `estado_inicial` |
| Acciones legales / sucesores del juego | `juego/reglas.py:25` `acciones_legales` |
| Transición (aplicar una acción) | `juego/reglas.py:57` `aplicar` |
| Condición de victoria / terminal | `juego/reglas.py:93` `ganador`, `:103` `es_terminal` |
| Sucesores y costo en la búsqueda | `busqueda/problema.py:26` (navegación), `:55` (misión, estado compuesto) |
| Costo de una celda | `escenario/modelo.py:44` `Escenario.costo` |
| Orden de movimientos | `config.py:4` `ORDEN_MOVIMIENTOS` (o `prueba.orden_movimientos`, `--orden`, GUI) |
| BFS y DFS (una sola función) | `busqueda/algoritmos.py:27` `_busqueda_ciega` |
| A\* y UCS (UCS = A\* con h=0) | `busqueda/algoritmos.py:78` y `:120` |
| Beam Search | `busqueda/algoritmos.py:135` |
| Heurísticas | `busqueda/heuristicas.py:15` manhattan, `:30` obstaculos, `:66` crear_heuristica (misión) |
| Función de evaluación | `adversarial/utilidad.py:85` `evaluar`, `:65` `restante` |
| Pesos de la utilidad | `config.py:14` (o `juego.pesos_utilidad` en el JSON) |
| Minimax y alfa‑beta | `adversarial/minimax.py:70` `decidir`; la poda es la línea `:115` |
| Orden de acciones | `adversarial/minimax.py:47` `ordenar_acciones` |
| Profundidad configurable | `juego.profundidad_maxima_minimax` en el JSON → `--profundidad` → GUI (por defecto `config.py:7`) |
| Validación del JSON | `escenario/validador.py:27` `validar` |
| Carga atómica | `escenario/cargador.py:17` `cargar_escenario` |
| Verificación | `verificacion/verificador.py:12` (caminos), `:47` (decisiones) |

> Si cambian el código, actualicen esta tabla (los números de línea se mueven).

## 5.1 Comandos para la sustentación
```bash
python -m tacticalgrid validar ruta/del/profesor.json
python -m tacticalgrid ejecutar ruta/del/profesor.json          # hace lo que pida prueba.modo y verifica
python -m tacticalgrid comparar ruta.json                         # tabla con todos los algoritmos
python -m tacticalgrid buscar ruta.json --algoritmo A_ESTRELLA --heuristica obstaculos --verificar
python -m tacticalgrid decidir ruta.json --algoritmo MINIMAX --profundidad 3 --orden inverso --verificar
python -m tacticalgrid partida ruta.json --a alfa_beta --b voraz --profundidad 3
python -m tacticalgrid gui ruta.json
```

## 6. Simulacro
Con Claude Code: `/sustentacion 005` (o cualquier spec). El examinador hace 5 preguntas, pide una predicción, propone una modificación pequeña y da retroalimentación. Hacerlo **sobre las specs del compañero**.
