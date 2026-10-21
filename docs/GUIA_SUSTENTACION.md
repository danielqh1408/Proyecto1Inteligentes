# Guía de sustentación (versión final, 20 oct)

Actualizada con el código corregido del 20 oct. Tres diferencias clave para explicar:
- Una victoria domina cualquier evaluación; la suma no terminal se limita a ±9999.
- En caso 9, profundidad 4: natural 427 hojas / 428 evaluaciones totales; heurístico 426 hojas / 2976 totales. Ordenar también cuesta.
- Beam no garantiza completitud al subir k; recoger no garantiza mejorar la evaluación; más profundidad no garantiza ganar. Son límites que deben saber justificar.


> La sustentación es **individual** y vale **50 %**. Cada uno debe explicar **cualquier** parte, aunque no la haya escrito.
> Cómo usar esta guía: lee la sección 2 en voz alta; para cada respuesta, abre el archivo de la sección 5 y señala la función. Practica las predicciones (§3) y las modificaciones (§4) **sin mirar las respuestas**.

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

Y pruebas de adaptación: cambiar costos, mover obstáculos/bases/unidades/recurso, cambiar el objetivo, la profundidad o el orden, y **predecir antes de ejecutar**.

## 2. Banco de preguntas con respuesta corta

### Modelado (spec 002)
- **¿Qué es un estado en su juego?** → `EstadoJuego` tiene 5 campos: posiciones de las unidades, portador, posición del recurso si está libre, turno y turnos jugados. Lo fijo (terreno, costos, bases, identidad de las unidades) está en `Escenario`.
- **¿Por qué cada campo?**
  - posiciones: quién puede moverse a dónde;
  - portador / recurso: la misma casilla con y sin recurso es un estado distinto;
  - turno: cambia las acciones y el valor;
  - turnos jugados: el mismo tablero en el turno 200 es empate.
- **¿Por qué no basta `(fila, columna)`?** → Con varias unidades, turnos y posesión, la misma casilla corresponde a situaciones distintas. En el caso 6 la misión pasa dos veces por cada celda del pasillo: con y sin recurso.
- **¿Qué acciones hay?** → MOVER (4 direcciones, a celda libre, transitable y que no sea la base enemiga), INTERCEPTAR (al lado del portador enemigo) y PASAR (solo si no hay otra).
- **¿Qué pasa al interceptar?** → El portador pierde el recurso: el recurso vuelve libre a su posición inicial y el portador a la suya. Fue propuesta de Daniel (D‑14).
  - La primera versión daba el recurso al interceptor y producía un ciclo infinito: 166 intercepciones en 200 turnos.
- **¿Por qué no se puede entrar a la base enemiga?** → La base es una sola celda. Quedarse encima impediría ganar al rival para siempre.
- **¿Qué pasa si no hay ruta?** → `exito = false` con todas las métricas; el verificador confirma con BFS que es inalcanzable, salvo Beam, que puede fallar aun habiendo ruta.
- **¿Y si nadie puede moverse?** → Se PASA, y al llegar a 200 turnos (`juego.max_turnos`) es empate.

### Búsqueda no informada y costo (spec 003)
- **BFS vs DFS:** cola (FIFO) contra pila (LIFO); es una sola función `_busqueda_ciega` y la diferencia está en una línea: `pop()` o `popleft()`.
  - BFS es óptimo en número de movimientos.
  - DFS depende del orden de los sucesores y no es óptimo. Caso 1: BFS da 29 movimientos y DFS 137.
- **¿Por qué BFS y UCS dan caminos distintos en el caso 2?** → BFS minimiza pasos y cruza el pantano: 17 pasos, costo 83. UCS minimiza Σ costos y rodea por el camino: 33 pasos, costo 33.
- **Generados vs expandidos:** generado = entra a la frontera (cuenta el inicio). Expandido = sale de la frontera y se le calculan los sucesores; el objetivo no cuenta.
- **¿Cuándo se prueba el objetivo?** → Al **sacar** el estado de la frontera, en los 5 algoritmos. Es necesario para que UCS y A\* den el óptimo, y hace comparables las métricas.
- **¿Por qué UCS es A\* con h = 0?** → Con h = 0, f = g. Lo muestra el notebook ("Caso 1 — Sin heurística"), y así no se duplica código.
- **¿Qué hace `if g != mejor_g[s]: continue`?** → Es eliminación perezosa. `heapq` no permite bajar la prioridad de un elemento, así que se reinserta el estado y se ignoran las entradas viejas.
- **Complejidad UCS / A\*:** O((V+E) log V) en tiempo y O(V) en espacio.

### Heurísticas, A\* y Beam (spec 004)
- **H1:** c_min · Manhattan. **H2 (propia):** c_min · pasos BFS hasta el objetivo esquivando muros. El BFS se precalcula una sola vez desde el objetivo.
- **¿Qué estima la propia?** → El costo mínimo restante en un mapa relajado que respeta los muros pero donde todo cuesta c_min.
- **¿Es admisible?** → Sí. Todo camino real tiene al menos pasos_BFS movimientos y cada uno cuesta ≥ c_min. También es consistente: los pasos BFS de dos vecinos difieren en ≤ 1.
- **¿Domina a Manhattan?** → Sí: pasos_BFS ≥ Manhattan. Caso 3: 177 expandidos contra 282, con el mismo costo, 32.
- **¿Dónde falla?** → En mapas abiertos es igual a Manhattan (caso 2: 92 y 92). Tampoco ayuda cuando lo que importa es el costo del terreno (caso 4: 289 contra 294).
- **¿Por qué multiplicar por c_min?** → Si un terreno cuesta 0,5, la Manhattan pura sobreestima y A\* puede perder el óptimo.
- **¿Y una heurística que sobreestima?** → H3 `manhattan_promedio`, en el caso 2: A\* da costo 83 cuando el óptimo es 33.
- **Beam con k = 1 contra k = 8:** caso 5. k = 1 entra al pasillo sin salida y falla; k ≥ 2 encuentra el óptimo (21). Recortar descarta caminos, y como los visitados son globales, no se recuperan. Más k significa más expandidos (41, 81, 155).
- **¿Por qué el criterio f dio igual que h?** → En mapas con costo 1, los candidatos de un mismo nivel tienen la misma g.

### Adversarial (spec 005)
- **¿Quién es MAX?** → El bando que tiene el turno cuando se pide la decisión.
- **¿Por qué MIN no está en desventaja?** → Mismas reglas y la misma función con el signo cambiado: `evaluar(s,"A") = −evaluar(s,"B")`. Que MIN minimice la utilidad de A es lo mismo que B maximice la suya. Son roles, no inteligencias distintas.
- **Función de utilidad:**
  - terminal: ±(10 000 + max(0, max_turnos − profundidad)), para preferir ganar antes y perder después;
  - no terminal: **limitar(20·posesión + 3·carrera + 0,1·movilidad, −9999, 9999)**, donde carrera = lo que le falta al rival para ganar − lo que me falta a mí, como estimación: usa Dijkstra salvo la persecución al portador, que combina pasos Manhattan y costo a base.
- **¿Por qué esta acción vale más?** → `python -m tacticalgrid decidir <json>` muestra el valor de cada acción de la raíz (las no elegidas por alfa-beta pueden ser cotas) y los componentes del hijo inmediato elegido; esos componentes no explican por sí solos el valor de la hoja Minimax.
- **¿Por qué 3 componentes y no 5?** → Con 5 (posesión, carrera al recurso, entrega, presión, movilidad), una unidad al lado del recurso **no lo recogía**: la evaluación no era monótona. Unificar en `restante` simplificó la fórmula, pero no garantiza monotonicidad; existe un contraejemplo con costos 10.
- **¿Por qué posesión = 20?** → Daniel lo vio alto en 50. Probamos 10, 20 y 50 y el resultado no cambia, porque la carrera ya premia tener el recurso.
- **¿Por qué alfa‑beta da la misma decisión?** → Solo poda ramas que no pueden cambiar el valor de la raíz. Además se elige la **primera** acción con valor **estrictamente** mayor. Caso 8: misma acción y valor (−47), con 427 nodos evaluados contra 20 478.
- **¿Dónde está la poda?** → Una sola línea: `if poda and alfa >= beta: break` en `minimax.py`. Minimax y alfa‑beta son la misma función.
- **Efecto del orden de acciones:** cambia cuántas ramas se podan, no el valor. Caso 9, profundidad 4: natural 427, heurístico 426, inverso 10 234 evaluados. Con el mejor orden, alfa‑beta es O(b^(d/2)).
- **Efecto de la profundidad:** Minimax crece ~12 veces por nivel (b ≈ 12) y alfa‑beta ~3,6 veces (≈ √12).
  - La acción cambia: A1 con profundidad 1, A2 → (11,7) con 2 y 3, A2 → (12,6) con 4 y 5.
  - El valor oscila por el efecto horizonte.
- **Caso 7:** el voraz va directo hacia el recurso. Minimax con profundidad 4 pone a A2 en la entrada del pasillo de B1: **bloquear** vale más que perseguir.
- **Torneo E6:** en el mapa simétrico, alfa‑beta con profundidad 3 le gana al voraz y a profundidad 1 (como A o como B). Con 3 contra 3 hay empate: ambos se defienden.

### Validación y verificación (specs 001 y 006)
- **¿Qué valida?** → Las 9 reglas de la p. 7 del PDF, más tipos de dato y "dos unidades no comparten celda". Reporta **todos** los errores juntos.
- **¿Carga atómica?** → Se valida todo antes de construir; si hay errores, la excepción ocurre antes de reemplazar el escenario anterior.
- **¿Qué verifica?** → Que el camino empiece en el inicio, que cada paso sea a una celda vecina, que no haya muros, que el costo coincida con las transiciones y que el final sea el objetivo. En las decisiones: acciones legales, estados válidos y que Minimax dé lo mismo que alfa‑beta.

### Uso de IA
- **¿Qué hizo la IA?** → Claude Code generó la estructura por especificaciones, el código, las pruebas, los mapas de los casos y los borradores de los documentos. Gemini apoyó a Daniel en la revisión y el manual. Codex realizó esta auditoría y las correcciones de código, pruebas y documentación. Todo está declarado en `docs/USO_IA.md` y en cada método.
- **¿Qué decidimos nosotros?**
  - pedir un código simple como el de los notebooks, lo que llevó a reescribir una versión más compleja;
  - aprobar cada decisión de diseño;
  - la regla de intercepción final y el peso de posesión (Daniel).
- **¿Cómo validamos?** → 284 pruebas sin Tk + 4 de interfaz automáticas (UCS y A\* contra un Dijkstra de referencia, Minimax = alfa‑beta en estados aleatorios, verificador sobre todos los resultados), 10 casos con lo esperado frente a lo obtenido, el ejercicio a mano BFS contra UCS y la revisión en la GUI.
- **¿Qué errores encontraron al probar?** → La evaluación no monótona y el ciclo infinito de intercepciones. La auditoría también encontró fallos con costos altos, carga de opciones y decisiones obsoletas; ya tienen pruebas de regresión.

## 3. Predicciones (hacerlas ANTES de ejecutar)
| # | Cambio | Predicción | Dato real |
|---|---|---|---|
| P1 | Pantano 7 → 15 (caso 2) | BFS: mismo camino, costo sube. UCS: igual, ya rodeaba | BFS 83 → 163; UCS 33 → 33 |
| P2 | Pantano 7 → 1 (caso 2) | UCS cruza el pantano; BFS y UCS coinciden | ambos: 17 pasos, costo 23 |
| P3 | Pantano 7 → 2 | Empate de costos: 33 por ambos lados; gana el directo por desempate | UCS: 17 pasos, costo 33 |
| P4 | Quitar el muro del caso 3 | H1 y H2 se igualan | ambas: 10 expandidos |
| P5 | Invertir el orden de movimientos | BFS: misma longitud; DFS: camino distinto | `test_orden_movimientos_dfs` |
| P6 | Profundidad 2 → 4 (caso 8) | ~12 veces más nodos por nivel en Minimax; la acción puede cambiar | 144 → 20 478; (11,7) → (12,6) |
| P7 | Orden `inverso` (caso 9) | Mismo valor, muchas menos podas útiles | 10 234 contra 427 evaluados |
| P8 | `pesos_utilidad: {"carrera": 0, "movilidad": 0}` | Solo cuenta la posesión: la IA no se acerca al recurso si no lo puede tomar dentro del horizonte | (probar en vivo) |
| P9 | Mapa 4×4 del enunciado, pantano 7 → 1 | UCS pasa a costo 6 por (2,2); BFS cuesta 8 | `test_ejemplo_enunciado` |

## 4. Modificaciones pequeñas que hay que saber hacer en vivo
| Petición | Dónde | Qué cambiar |
|---|---|---|
| Cambiar el orden de movimientos por defecto | `config.py` | reordenar la tupla `ORDEN_MOVIMIENTOS` (o usar `--orden` o el JSON, sin tocar código) |
| BFS con prueba de objetivo al generar | `busqueda/algoritmos.py` | dentro del `for` de sucesores, devolver si `problema.es_objetivo(s2)`; explicar que los generados bajan y que en UCS/A\* esto rompería el óptimo |
| Beam por f en vez de h | `busqueda/algoritmos.py` | ya existe `criterio="f"`; mostrar la línea `candidatos.sort(...)` |
| Agregar diagonales | `escenario/modelo.py` | agregar direcciones a `DIRECCIONES`, al orden y a su validación; adaptar también reglas y pruebas. **Ojo:** Manhattan deja de ser admisible (habría que usar Chebyshev) |
| Nuevo componente de la utilidad | `adversarial/utilidad.py` | agregar una entrada a `f` y su peso en `config.py`; mantener la simetría (suma cero) |
| Quitar la poda | `adversarial/minimax.py` | llamar `minimax(...)` (que pasa `poda=False`) en vez de `alfa_beta(...)`; mostrar que la línea `if poda and alfa >= beta: break` es la única diferencia |
| Cambiar el límite de turnos | JSON `juego.max_turnos` | sin tocar código |
| Otra regla de validación | `escenario/validador.py` | agregar un `if` que haga `errores.append("[Rxx] campo: explicación")` |

## 5. Mapa "dónde está cada cosa" (buscar por nombre de función)
| Pregunta del profesor | Archivo / función |
|---|---|
| Representación del estado | `juego/estado.py` `EstadoJuego` |
| Estado inicial | `juego/estado.py` `estado_inicial` |
| Acciones legales (sucesores del juego) | `juego/reglas.py` `acciones_legales` |
| Transición / intercepción | `juego/reglas.py` `aplicar` |
| Victoria / terminal | `juego/reglas.py` `ganador`,  `es_terminal` |
| Invariantes del estado | `juego/reglas.py` `validar_estado` |
| Sucesores y costo en la búsqueda | `busqueda/problema.py`: `ProblemaNavegacion.sucesores` y `ProblemaMision.sucesores` |
| Costo de una celda | `escenario/modelo.py` `Escenario.costo` |
| Vecinos y orden de movimientos | `escenario/modelo.py` `vecinos`, `config.py` |
| BFS y DFS | `busqueda/algoritmos.py` `_busqueda_ciega` |
| A\* y UCS | `busqueda/algoritmos.py`: `a_estrella` y `costo_uniforme`  |
| Beam Search | `busqueda/algoritmos.py`: `beam_search` |
| Heurísticas | `busqueda/heuristicas.py` manhattan,  obstaculos,  crear_heuristica |
| Distancias reales (Dijkstra) | `adversarial/utilidad.py` `distancias` |
| Función de evaluación | `adversarial/utilidad.py` `restante`,  `evaluar` |
| Pesos de la utilidad | `config.py` (o `juego.pesos_utilidad` en el JSON) |
| Minimax y alfa‑beta | `adversarial/minimax.py` `decidir`; buscar `if poda and alfa >= beta` |
| Orden de acciones | `adversarial/minimax.py` `ordenar_acciones` |
| Agente voraz | `adversarial/minimax.py`: `voraz` |
| Profundidad configurable | `prueba.profundidad` o `juego.profundidad_maxima_minimax` en el JSON → `--profundidad` → GUI (por defecto en `config.py`) |
| Validación del JSON | `escenario/validador.py` `validar` |
| Carga atómica | `escenario/cargador.py` `cargar_escenario` |
| Verificación | `verificacion/verificador.py`: `verificar_camino` y `verificar_decision` |

## 6. Comandos para la sustentación
```bash
cd PrimerProyecto && source .venv/bin/activate          # o .venv-gui para la interfaz
python -m tacticalgrid validar ruta/del/profesor.json
python -m tacticalgrid ejecutar ruta/del/profesor.json   # hace lo que pida prueba.modo y verifica
python -m tacticalgrid comparar ruta.json                # tabla con todos los algoritmos
python -m tacticalgrid buscar ruta.json --algoritmo A_ESTRELLA --heuristica obstaculos --verificar
python -m tacticalgrid buscar ruta.json --algoritmo BEAM --k 1 --objetivo 10,18
python -m tacticalgrid decidir ruta.json --algoritmo MINIMAX --profundidad 3 --orden inverso --verificar
python -m tacticalgrid partida ruta.json --a alfa_beta --b voraz --profundidad 3
.venv-gui/bin/python -m tacticalgrid gui ruta.json
pytest -q
```

## 7. Checklist de la mañana (15 minutos antes)
- [ ] Ejecutar `.venv/bin/python -m pytest -q -o addopts=''` sobre la copia corregida y ensayada.
- [ ] Abrir la GUI con `.venv-gui/bin/python -m tacticalgrid gui escenarios/casos/caso03_obstaculo_heuristica.json`.
- [ ] Tener abiertos `juego/reglas.py`, `busqueda/algoritmos.py`, `adversarial/utilidad.py` y `adversarial/minimax.py`.
- [ ] Tener a mano `resultados/RESUMEN.md` y `docs/DOCUMENTO_TECNICO.md`.
- [ ] Repasar en voz alta: estado (5 campos), heurística propia (admisibilidad), por qué MIN no está en desventaja y la línea de la poda.

## 8. Simulacro
Con Claude Code: `/sustentacion 005` (o cualquier spec). Hace preguntas, pide una predicción, propone una modificación pequeña y da retroalimentación. Hazlo también **sobre las specs que no son tuyas**.
