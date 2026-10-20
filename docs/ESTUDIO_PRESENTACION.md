# Estudio y presentación grupal — TacticalGrid

> **Mañana 21 oct, 7:20 a.m. — presentación GRUPAL de 20 minutos.** La sustentación individual es otro día (el profesor publicará horarios).
> Antes: **inscribir el grupo en la hoja que envió el profesor** (uno de los dos).
> Este documento es para estudiar esta noche: plan → guía de entendimiento → guion de 20 min → banco de preguntas con respuestas → tarjetas para memorizar.

---

## 0. Plan de estudio (esta noche y mañana)

| Bloque | Duración | Qué hacer | Resultado esperado |
|---|---|---|---|
| 1 | 20 min | Leer la **§1 (el proyecto en 10 ideas)** y ejecutar la demo completa de la §4 una vez, siguiendo los pasos | Ver todo funcionando y saber dónde está cada cosa |
| 2 | 60 min | **§2 Guía de entendimiento**: para cada parte, leer la explicación, abrir el archivo y ubicar la línea. Decir en voz alta la "frase para memorizar" | Poder explicar cada parte en 1 minuto |
| 3 | 15 min | Descanso | — |
| 4 | 45 min | **§3 Guion de 20 min**: ensayar SU parte en voz alta con cronómetro, dos veces. Llamada con Daniel para ensayar juntos una vez | Presentación fluida, sin leer |
| 5 | 45 min | **§5 Banco de preguntas**: tapar la respuesta, responder en voz alta, destapar y comparar. Marcar las que fallen y repetirlas | Responder sin mirar ≥ 80 % |
| 6 | 15 min | **§6 Tarjetas**: memorizar los números clave | Dar datos concretos (eso impresiona) |
| Noche | — | Dormir. La memoria se consolida durmiendo | — |
| Mañana 6:00 | 30 min | Repasar §6 y las preguntas marcadas. `git pull`, `pytest -q`, abrir la GUI (checklist §4.1) | Todo listo y probado |
| 7:00 | 15 min | Llegar, conectar el computador, dejar la GUI abierta en el caso 2 | Cero sorpresas técnicas |

**Reparto sugerido** (coincide con lo que cada uno revisó/decidió): **Juan** = introducción, JSON y validación, búsqueda (BFS/DFS/UCS/A\*/Beam), experimentos, uso de IA. **Daniel** = estado y reglas (él propuso D‑14), adversarial (utilidad, Minimax, alfa‑beta), verificación, conclusiones. **Ambos deben poder responder cualquier pregunta.**

---

## 1. El proyecto en 10 ideas (léelas hasta poder decirlas sin mirar)

1. **Qué es:** un juego por turnos en una cuadrícula. Dos bandos (A y B) con 3 unidades cada uno; gana quien lleve el **recurso** del centro a **su base**. El juego es solo el **entorno**: lo que se evalúa es la **IA que decide**.
2. **Pregunta central:** ¿cómo cambia la forma de decidir cuando se pasa de **encontrar una ruta** (BFS/DFS) → **la más barata** (UCS) → **usar conocimiento** (A\*, Beam) → **decidir frente a un rival** (Minimax, alfa‑beta)?
3. **Todo sale del JSON:** mapa, costos, unidades, bases. Nada está escrito en el código. El profesor puede traer un JSON nuevo y cambiar costos sin que toquemos código.
4. **Estado = 5 datos:** posiciones de las unidades, quién lleva el recurso, dónde está el recurso si está libre, de quién es el turno y cuántos turnos van. Lo que no cambia (mapa, costos, bases) está aparte, en el "escenario".
5. **BFS y DFS** son la misma función: BFS saca de la **cola** (el más antiguo), DFS de la **pila** (el más nuevo). BFS da el camino con **menos pasos**; DFS da *algún* camino.
6. **UCS es A\* con h = 0.** UCS minimiza el **costo**; A\* suma una estimación h(n) para explorar menos sin perder el óptimo si h es **admisible**.
7. **Heurística propia ("obstáculos"):** cuántos pasos faltan **esquivando muros** (un BFS hecho una vez desde el objetivo) × el costo más barato del mapa. Es admisible y **domina** a Manhattan → A\* expande menos (177 vs 282 en el caso 3).
8. **Beam Search** guarda solo los **k mejores** por nivel: ahorra memoria pero puede **fallar** (caso 5: k=1 falla, k≥2 encuentra).
9. **Minimax y alfa‑beta son la misma función**; la única diferencia es una línea: `if poda and alfa >= beta: break`. Eligen **la misma acción**, pero alfa‑beta evalúa muchísimo menos (427 vs 20 478 nodos).
10. **Evaluación = 20·posesión + 3·carrera + 0,1·movilidad**, donde *carrera* = lo que le falta al rival para ganar − lo que me falta a mí. Es igual para ambos bandos con signo contrario → **MIN no está en desventaja**.

---

## 2. Guía de entendimiento (archivo por archivo)

> Abre cada archivo mientras lees. Las líneas son las de la versión `v1.0-sustentacion`.

### 2.1 El escenario y la validación — `escenario/` (Juan)
- **Qué hace:** lee el JSON, lo **valida completo** y construye un objeto `Escenario` que no cambia.
- **Validación** (`validador.py:27`): las 9 reglas de la p. 7 del PDF (dimensiones, terrenos que existen, costos > 0, todo dentro del mapa, unidades no sobre muros, ids únicos, bandos A/B, turno A/B, portador existente) + que dos unidades no compartan celda. Devuelve **todos** los errores juntos, cada uno con código y campo: `[R4] bases.B: (4, 3) está fuera del mapa 4x4`.
- **Carga atómica** (`cargador.py:17`): primero valida, después construye. Si hay error lanza `EscenarioInvalido` **antes** de devolver nada, así que el escenario anterior queda intacto.
- **Costo** (`modelo.py:44`): `costo(celda)` = costo de **entrar** a esa celda, leído del JSON.
- 🗣️ **Frase:** "Validamos todo antes de construir; si algo falla, el escenario anterior no se toca. Los costos solo salen del JSON."

### 2.2 El estado y las reglas — `juego/` (Daniel)
- **Estado** (`estado.py:16`): `EstadoJuego(posiciones, portador, recurso, turno, turnos_jugados)`. Es inmutable (no se modifica, se crea uno nuevo), por eso se puede guardar en conjuntos.
- **Acciones legales** (`reglas.py:25`): para cada unidad del bando en turno, primero INTERCEPTAR (si está al lado del portador enemigo) y luego MOVER a cada vecino libre, transitable y que no sea la base enemiga. Si no hay nada → PASAR.
- **Aplicar** (`reglas.py:59`): crea el estado siguiente. Al entrar al recurso lo recoge. Al **interceptar**: el recurso vuelve libre a su sitio y el antiguo portador a su posición inicial (línea 88). Cambia el turno y suma 1 a turnos jugados.
- **Ganar / terminar** (`reglas.py:97`, `:107`): gana el bando cuyo portador está en su propia base; empate al llegar a 200 turnos.
- 🗣️ **Frase:** "El estado guarda solo lo que cambia: posiciones, portador, recurso, turno y turnos. Con eso y el escenario se calcula todo."

### 2.3 Los problemas de búsqueda — `busqueda/problema.py`
- **Navegación:** estado = `(fila, columna)`; sucesores = vecinos con su costo.
- **Misión:** estado = `((fila, columna), lleva_recurso)`; al entrar a la celda del recurso, `lleva` pasa a `True`; objetivo = `(base propia, True)`. Es el **estado compuesto** (caso 6).
- Los algoritmos solo usan tres cosas del problema: `inicio`, `es_objetivo(s)` y `sucesores(s)`. Por eso el mismo BFS sirve para ambos.

### 2.4 BFS y DFS — `busqueda/algoritmos.py:27` (Juan)
```python
frontera = deque([problema.inicio]); padres = {problema.inicio: None}
while frontera:
    s = frontera.pop() if es_dfs else frontera.popleft()   # pila (DFS) o cola (BFS)
    if problema.es_objetivo(s): return ...                 # objetivo al SACAR
    for s2, c in problema.sucesores(s):
        if s2 not in padres:                               # padres = visitados
            padres[s2] = (s, c); frontera.append(s2)
```
- `padres` sirve de "visitados" y para reconstruir el camino al final.
- 🗣️ **Frase:** "Es la misma función; solo cambia si saco por delante (cola, BFS) o por detrás (pila, DFS)."

### 2.5 UCS y A\* — `busqueda/algoritmos.py:82` y `:126` (Juan)
```python
frontera = [(h(inicio), 0, next(desempate), inicio)]      # (f, g, contador, estado)
while frontera:
    f, g, _, s = heappop(frontera)                         # el de menor f = g + h
    if g != mejor_g[s]: continue                           # entrada vieja: ya hay un camino mejor
    ...
    for s2, c in problema.sucesores(s):
        if g + c < mejor_g.get(s2, inf):                    # encontré un camino más barato a s2
            heappush(frontera, (g + c + h(s2), g + c, next(desempate), s2))
```
- **UCS = A\* con h = 0** (`costo_uniforme` llama a `a_estrella` con `lambda s: 0`).
- `if g != mejor_g[s]: continue` = **eliminación perezosa**: el heap no permite bajar prioridades, así que se reinserta y se ignoran las entradas viejas.
- El contador `next(desempate)` hace que los empates se resuelvan siempre igual (determinismo).
- 🗣️ **Frase:** "A\* ordena por f = g + h; UCS es A\* con h = 0."

### 2.6 Heurísticas — `busqueda/heuristicas.py` (Juan)
- **c_min** = costo del terreno más barato del mapa (del JSON).
- **Manhattan** (`:15`): `c_min · (|Δfila| + |Δcolumna|)`.
- **Obstáculos, la propia** (`:32`): BFS **desde el objetivo** una sola vez → `pasos[celda]`; `h = c_min · pasos[celda]` (∞ si no hay camino).
- **Admisible** = nunca sobreestima. Prueba: todo camino real tiene al menos esos pasos y cada uno cuesta al menos c_min.
- **Domina** a Manhattan porque esquivar muros nunca da menos pasos que la línea recta.
- 🗣️ **Frase:** "Nuestra heurística es la distancia real en pasos esquivando muros, como si todo costara lo mínimo. Es admisible porque relaja el problema."

### 2.7 Beam Search — `busqueda/algoritmos.py:143` (Juan)
- Por niveles: expande todo el haz, junta los hijos nuevos, los ordena por h y se queda con los **k mejores** (línea 179). Lo descartado queda marcado como visitado y no vuelve.
- 🗣️ **Frase:** "Beam limita la memoria a k estados por nivel; por eso puede descartar el único camino bueno."

### 2.8 La función de evaluación — `adversarial/utilidad.py` (Daniel)
- `distancias` (`:37`): 4 Dijkstra **una sola vez** por escenario (a cada base y al recurso, por bando), con costos reales.
- `restante(X)` (`:67`): lo que le falta al bando X para ganar:
  - si X lleva el recurso: del portador a su base;
  - si está libre: de su unidad más cercana al recurso + del recurso a su base;
  - si lo lleva el rival: alcanzar al portador + de ahí a su base.
- `evaluar` (`:87`): **20·posesión + 3·carrera + 0,1·movilidad**. Devuelve también el **desglose** para explicar las decisiones.
- Terminal: ±10 000 (menos la profundidad, para preferir ganar antes).
- 🗣️ **Frase:** "Evaluamos quién está más cerca de ganar con distancias reales; la misma función con signo contrario sirve para los dos bandos."

### 2.9 Minimax y alfa‑beta — `adversarial/minimax.py:72` (Daniel)
```python
def valor(s, nivel, alfa, beta):
    if es_terminal(s):            return utilidad_terminal(...)
    if nivel == profundidad:      return evaluar(...)
    mejor = -inf si juega MAX, +inf si juega MIN
    for accion in ordenar_acciones(...):
        v = valor(aplicar(s, accion), nivel + 1, alfa, beta)
        MAX: mejor = max(mejor, v); alfa = max(alfa, mejor)
        MIN: mejor = min(mejor, v); beta = min(beta, mejor)
        if poda and alfa >= beta: break        # ← la ÚNICA diferencia con Minimax
    return mejor
```
- En la raíz se elige la **primera** acción con valor **estrictamente** mayor → Minimax y alfa‑beta eligen lo mismo.
- `ordenar_acciones` (`:47`): natural, inverso o heurístico (ordena por evaluación de cada hijo).
- La profundidad sale del JSON (`juego.profundidad_maxima_minimax` o `prueba.profundidad`), de `--profundidad` o de la GUI.
- 🗣️ **Frase:** "Minimax supone que el rival juega lo mejor para él; alfa‑beta deja de explorar ramas que ya no pueden cambiar la decisión."

### 2.10 Verificación, experimentos e interfaz
- **Verificador** (`verificacion/verificador.py`): recalcula desde el escenario que el camino sea válido, sin muros, con el costo correcto y que termine en el objetivo; y que las acciones de Minimax sean legales.
- **Experimentos** (`python -m tacticalgrid experimentos`): corre los 10 casos y E1–E6 y escribe `resultados/RESUMEN.md`.
- **Interfaz** (`interfaz/app.py`): solo dibuja y llama a las funciones; no tiene lógica de IA.

---

## 3. Guion de la presentación (20 minutos)

> Objetivo: **15–16 min de presentación + 4–5 min para preguntas.** Cada bloque dice quién habla, qué mostrar y la idea que debe quedar.

| Min | Quién | Qué decir (idea principal) | Qué mostrar |
|---|---|---|---|
| 0:00–1:30 | Juan | Presentación del grupo. El juego (bandos, recurso, bases) es el entorno; lo evaluado es la IA. La pregunta central: ruta → costo → heurística → adversario | README / GUI con `ejemplo_enunciado.json` |
| 1:30–3:00 | Juan | Arquitectura en capas (escenario, juego, búsqueda, adversarial, verificación, interfaz). Todo sale del JSON. Validación de 9 reglas y carga atómica | GUI: *Cargar JSON…* → `escenarios/invalidos/varios_errores.json` (sale la lista de errores y el mapa anterior sigue) |
| 3:00–5:00 | Daniel | **Estado** de 5 campos y por qué cada uno. Acciones MOVER/INTERCEPTAR/PASAR. Reglas: no entrar a la base enemiga; **D‑14**: al interceptar, recurso y portador vuelven a su inicio (cuenta la historia: el ciclo de 166 intercepciones) | `docs/DOCUMENTO_TECNICO.md` §2–3 o diapositiva |
| 5:00–7:00 | Juan | BFS vs DFS (cola vs pila, misma función). **Caso 2**: BFS 17 pasos / costo 83; UCS 33 pasos / costo 33 | GUI: cargar `caso02`, *Comparar todos* → tabla |
| 7:00–9:30 | Juan | A\* y las 2 heurísticas; admisibilidad y dominancia. **Caso 3**: 282 → 177 expandidos con el mismo costo 32. Beam: **caso 5**, k=1 falla, k=2 encuentra | GUI: `caso03`, A\* *Animar exploración* con manhattan y luego con obstaculos; `caso05`, Beam k=1 y k=2 |
| 9:30–12:30 | Daniel | Función de evaluación (posesión, carrera, movilidad) y por qué MIN no está en desventaja. **Caso 7**: Minimax bloquea, no corre al recurso. **Caso 8**: misma acción, 427 vs 20 478 nodos | GUI: `caso07` → *Decidir* (flecha + valores); `caso08` con MINIMAX y con ALFA_BETA |
| 12:30–14:00 | Daniel | Orden de acciones (natural 427 vs inverso 10 234) y profundidad (12× por nivel en Minimax, ~3,6× en alfa‑beta ≈ √b). Partida: más profundidad gana | GUI: `partida_simetrica.json`, A = ALFA_BETA, B = VORAZ, *Jugar hasta el final* |
| 14:00–15:00 | Juan | Experimentos reproducibles (un comando), 10 casos ✔, 206 pruebas. Uso de IA declarado y cómo lo validamos | `resultados/RESUMEN.md`, `docs/USO_IA.md` |
| 15:00–16:00 | Daniel | Verificación (botón *Verificar*) y conclusiones: respuesta a la pregunta central + limitaciones | GUI: *Verificar* |
| 16:00–20:00 | Ambos | Preguntas | — |

**Respuesta a la pregunta central (para el cierre, memorizar):**
> "Al encontrar una ruta, el sistema solo explora (BFS/DFS). Al optimizar el costo, ordena por lo que lleva gastado (UCS). Con conocimiento heurístico, estima lo que falta y explora menos sin perder el óptimo (A\*), o limita la memoria a cambio de completitud (Beam). Y frente a un adversario ya no busca un camino sino una **acción**, suponiendo que el rival responde lo mejor para él (Minimax), y la poda alfa‑beta le permite mirar más lejos con el mismo esfuerzo."

---

## 4. Demo paso a paso (ensayarla esta noche)

```bash
cd PrimerProyecto
.venv-gui/bin/python -m tacticalgrid gui escenarios/ejemplo_enunciado.json
```
1. **Validación:** *Cargar JSON…* → `escenarios/invalidos/varios_errores.json` → se ven 3 errores (R3, R6, R8) y el mapa anterior sigue.
2. **Caso 2:** cargar `escenarios/casos/caso02_ruta_corta_vs_economica.json` → pestaña *Búsqueda* → *Comparar todos*. Señalar en la tabla BFS (17 / 83) y UCS (33 / 33).
3. **Caso 3:** cargar `caso03_obstaculo_heuristica.json` → Algoritmo `A_ESTRELLA`, heurística `manhattan` → *Animar exploración*; luego `obstaculos` → *Animar exploración*. Comparar los expandidos: 282 vs 177.
4. **Caso 5:** cargar `caso05_beam.json` → `BEAM`, k = 1 → *Ejecutar* (falla); k = 2 → *Ejecutar* (encuentra, costo 21).
5. **Caso 7:** cargar `caso07_decision_adversarial.json` → pestaña *Adversarial* → *Decidir*. Señalar la flecha (A2 → (9,12)) y el valor de cada acción.
6. **Caso 8:** cargar `caso08_minimax_vs_alfabeta.json` → Algoritmo `MINIMAX`, profundidad 4 → *Decidir*; luego `ALFA_BETA` → *Decidir*. Comparar nodos evaluados (20 478 vs 427) y la misma acción. → *Verificar*.
7. **Partida:** cargar `escenarios/partida_simetrica.json` → Juega A = `ALFA_BETA`, Juega B = `VORAZ`, profundidad 3 → *Jugar hasta el final*.

**Plan B si falla la GUI:** usar la terminal:
```bash
.venv/bin/python -m tacticalgrid comparar escenarios/casos/caso02_ruta_corta_vs_economica.json
.venv/bin/python -m tacticalgrid decidir escenarios/casos/caso08_minimax_vs_alfabeta.json --algoritmo MINIMAX --verificar
.venv/bin/python -m tacticalgrid partida escenarios/partida_simetrica.json --a alfa_beta --b voraz --profundidad 3
```

### 4.1 Checklist de la mañana
- [ ] Grupo inscrito en la hoja del profesor.
- [ ] `git pull` y `.venv/bin/pytest -q` → 206 en verde.
- [ ] GUI abierta y probada con el caso 2.
- [ ] Pestañas abiertas: `resultados/RESUMEN.md`, `docs/DOCUMENTO_TECNICO.md`, `juego/reglas.py`, `adversarial/minimax.py`.
- [ ] Batería y cargador del computador; adaptador HDMI si hace falta.

---

## 5. Banco de preguntas con respuesta modelo

> Tapa la respuesta, responde en voz alta y compara. ⭐ = muy probable.

### Modelado y reglas
1. ⭐ **¿Qué es un estado en su proyecto y por qué no basta (fila, columna)?**
   → Son 5 datos: posiciones de todas las unidades, quién lleva el recurso, dónde está el recurso si está libre, de quién es el turno y cuántos turnos van. (fila, columna) no basta porque hay varias unidades, posesión y turnos: la misma unidad en la misma casilla puede estar en estados distintos. Por ejemplo, sobre su base con el recurso gana y sin él no.
2. **¿Qué decidieron no guardar en el estado?**
   → Lo que no cambia: mapa, costos, bases e identidad de las unidades. Va en el `Escenario`, así el estado es pequeño y fácil de comparar.
3. **¿Para qué sirve "turnos jugados"?**
   → Para el empate por límite de turnos. El mismo tablero en el turno 10 y en el 200 no es igual: en el 200 la partida terminó.
4. ⭐ **¿Qué pasa cuando se intercepta al portador?**
   → El recurso vuelve libre a su posición inicial y el portador a la suya (propuesta de Daniel). La primera versión le daba el recurso al interceptor y se formaba un ciclo infinito: 166 intercepciones en 200 turnos.
5. **¿Por qué no se puede entrar a la base enemiga?**
   → La base es una sola casilla. Si una unidad se para encima, el rival nunca puede ganar.
6. **¿Qué pasa si una unidad queda bloqueada? ¿Y si no hay ruta?**
   → Si ninguna unidad del bando puede actuar, pasa. Si no hay ruta en una búsqueda, el resultado es "sin solución" con todas las métricas, y el verificador confirma con BFS que es inalcanzable.
7. **¿MAX y MIN tienen reglas distintas?**
   → No. Las mismas reglas y la misma función de evaluación; solo cambia el signo.

### Búsqueda
8. ⭐ **Diferencia entre BFS y DFS en su código.**
   → Es la misma función: BFS saca el más antiguo (cola) y DFS el más reciente (pila). BFS garantiza el menor número de movimientos; DFS no, y depende del orden de los vecinos (caso 1: 29 contra 137 movimientos).
9. ⭐ **¿Por qué BFS y UCS dan caminos distintos en el caso 2?**
   → BFS minimiza pasos y cruza el pantano: 17 pasos, costo 83. UCS minimiza costo y rodea por el camino: 33 pasos, costo 33.
10. **¿Qué es un estado generado y uno expandido?**
    → Generado: entra a la frontera. Expandido: sale de la frontera y se le calculan los sucesores.
11. **¿Cuándo comprueban si llegaron al objetivo? ¿Por qué?**
    → Al sacar el estado de la frontera. En UCS y A\* es necesario para garantizar el óptimo, porque un camino más barato podría aparecer después. Lo hacemos igual en todos para comparar métricas.
12. **¿Qué hace `if g != mejor_g[s]: continue`?**
    → Ignora entradas viejas del heap. Cuando encontramos un camino más barato a un estado lo reinsertamos, y la entrada anterior queda obsoleta.
13. **¿Por qué UCS es A\* con h = 0?**
    → Porque f = g + 0 = g, que es justo el criterio de UCS. Así no duplicamos código.
14. ⭐ **Expliquen su heurística propia y su admisibilidad.**
    → Es la distancia en pasos hasta el objetivo esquivando muros, calculada con un BFS desde el objetivo una sola vez, multiplicada por el costo más barato del mapa. Es admisible porque cualquier camino real tiene al menos esos pasos y cada paso cuesta al menos c_min: nunca sobreestima. Domina a Manhattan, porque esquivar muros nunca da menos pasos que la línea recta.
15. **¿Por qué multiplican por c_min?**
    → Si el profesor pone un terreno de costo 0,5, la Manhattan normal sobreestimaría y A\* podría dar un camino que no es el óptimo.
16. **¿Dónde funciona mal su heurística?**
    → En mapas abiertos es igual a Manhattan (caso 2: 92 expandidos con ambas). Tampoco ayuda cuando lo que importa es el costo del terreno, porque supone todo al mínimo.
17. **¿Costo computacional de cada heurística?**
    → Manhattan: O(1). Obstáculos: un BFS de O(filas × columnas) una sola vez, y después O(1) por consulta.
18. ⭐ **¿Qué pasa con Beam si k = 1?**
    → Solo conserva el mejor candidato por nivel. En el caso 5 entra a un pasillo sin salida y falla, aunque sí existe camino. Con k = 2 ya encuentra el óptimo. Lo que se descarta no vuelve.

### Adversarial
19. ⭐ **¿Por qué MIN no está en desventaja frente a MAX?**
    → Los dos usan las mismas reglas y la misma evaluación con signo contrario. Que MIN minimice la utilidad de A es exactamente lo mismo que B maximice la suya. MAX y MIN son roles en el árbol, no inteligencias distintas.
20. ⭐ **Expliquen su función de utilidad.**
    → Si alguien ganó: ±10 000. Si no: 20·posesión + 3·carrera + 0,1·movilidad.
    - Posesión: +1 si yo tengo el recurso, −1 si lo tiene el rival.
    - Carrera: lo que le falta al rival para ganar menos lo que me falta a mí, con distancias reales calculadas con Dijkstra.
    - Movilidad: mis acciones menos las suyas; penaliza quedar bloqueado.
21. **¿Por qué la cambiaron de 5 a 3 componentes?**
    → Con 5, una unidad al lado del recurso prefería no recogerlo: al recogerlo desaparecía un término grande y aparecía uno negativo. Unificamos todo en "lo que falta para ganar" y ahora recoger nunca empeora el valor.
22. **¿Qué pasa si cambian los pesos?**
    → Se cambian desde el JSON sin tocar código. Probamos posesión en 10, 20 y 50 y los resultados no cambian, porque la carrera ya premia tener el recurso. Si se pone carrera = 0, la IA deja de acercarse al recurso.
23. ⭐ **¿Por qué alfa‑beta da la misma decisión que Minimax?**
    → Solo deja de explorar ramas que ya no pueden cambiar el valor de la raíz. Y en empate elegimos la primera acción con valor estrictamente mayor. Caso 8: la misma acción y el mismo valor (−47), con 427 nodos evaluados contra 20 478.
24. ⭐ **¿Qué pasa si cambian el orden de las acciones?**
    → El valor no cambia, pero sí cuántas ramas se podan. Con el orden natural, alfa‑beta evaluó 427 nodos; con el inverso, 10 234. Si la mejor jugada se ve primero, se poda más: en el mejor caso es O(b^(d/2)).
25. ⭐ **¿Qué pasa si suben la profundidad?**
    → Minimax crece unas 12 veces por nivel, porque hay ~12 acciones por turno. Alfa‑beta crece unas 3,6 veces, cercano a √12. La acción puede cambiar porque la IA ve más lejos, y el valor oscila según quién juega en el último nivel (efecto horizonte).
26. **¿Por qué en el caso 7 Minimax no va directo al recurso?**
    → B1 lo recogerá primero, así que A2 se pone en la entrada del pasillo que B1 necesita para llegar a su base. Bloquear vale más que perseguir. Eso es pensar en la respuesta del rival.
27. **¿Dónde está la poda en el código?**
    → En una sola línea de `minimax.py`: `if poda and alfa >= beta: break`. Minimax y alfa‑beta son la misma función.

### Proceso, validación e IA
28. ⭐ **¿Qué pasa si les doy un JSON que nunca vieron?**
    → Se valida completo. Si es inválido, sale la lista de errores; si es válido, `python -m tacticalgrid ejecutar archivo.json` hace lo que diga `prueba.modo`. Nada depende de un mapa fijo; los costos salen del JSON.
29. **¿Cómo verifican que una solución es correcta?**
    → El verificador recalcula todo desde el escenario: camino continuo, sin muros, costo igual a la suma de las celdas y que termine en el objetivo. En Minimax, que las acciones sean legales y que dé lo mismo que alfa‑beta.
30. ⭐ **¿Cómo usaron la IA y cómo validaron lo que hizo?**
    → Claude Code generó la estructura, el código y las pruebas; Gemini apoyó a Daniel en la revisión y el manual. Todo está declarado en `USO_IA.md` y en cada método. Nosotros decidimos las reglas y la simplificación. Validamos con 206 pruebas automáticas (incluido un Dijkstra de referencia), con los 10 casos y con la interfaz. Además encontramos y corregimos dos errores jugando partidas.
31. **¿Cómo reproducen los experimentos?**
    → Con un comando, `python -m tacticalgrid experimentos`, que regenera las tablas. Todo es determinista menos el tiempo.

### Predicciones (el profesor las pide ANTES de ejecutar)
32. ⭐ **"Cambio el pantano de 7 a 15. ¿Qué pasa con BFS y UCS?"**
    → BFS sigue con el mismo camino porque no mira costos, pero su costo sube de 83 a 163. UCS no cambia: ya rodeaba el pantano (33).
33. **"¿Y si lo bajo a 1?"**
    → UCS cruza el pantano y coincide con BFS: 17 pasos, costo 23.
34. **"Quito el muro del caso 3. ¿Qué pasa con sus dos heurísticas?"**
    → Se vuelven iguales y expanden lo mismo (10 cada una).

### Modificaciones pequeñas
35. **"Cambie el orden de los movimientos."**
    → En `config.py:4`, `ORDEN_MOVIMIENTOS`, o sin tocar código con `prueba.orden_movimientos` en el JSON o el combo *Orden* de la GUI. BFS mantiene la longitud; DFS cambia de camino.
36. **"Haga que Minimax no pode."**
    → Usar `minimax(...)` en vez de `alfa_beta(...)`; las dos llaman a `decidir` con `poda=False` o `True`.
37. **"Agregue movimientos en diagonal."**
    → En `escenario/modelo.py:13` agregar direcciones a `DIRECCIONES` y al orden. Importante: Manhattan dejaría de ser admisible y habría que usar la distancia de Chebyshev.

---

## 6. Tarjetas para memorizar (números que dan seguridad)

| Dato | Valor |
|---|---|
| Pruebas automáticas | **206** (más 24 de documentación) |
| Casos mínimos cumplidos | **10/10** |
| Caso 2 BFS / UCS | 17 pasos, costo **83** / 33 pasos, costo **33** |
| Caso 3, expandidos A\* Manhattan / propia | **282 / 177** (costo 32 ambos) |
| Caso 5, Beam | k=1 **falla**, k=2 encuentra (costo 21) |
| Caso 8, nodos evaluados Minimax / alfa‑beta (prof. 4) | **20 478 / 427**, misma acción y valor (−47) |
| Orden natural / inverso (prof. 4) | **427 / 10 234** evaluados |
| Crecimiento por nivel | Minimax ×**12** (b ≈ 12), alfa‑beta ×**3,6** (≈ √12) |
| Pantano 7 → 15 | BFS 83 → **163**, UCS **33** sin cambio |
| Ciclo de intercepción (primera versión) | **166** intercepciones en 200 turnos |
| Pesos de la evaluación | posesión **20**, carrera **3**, movilidad **0,1** |
| Victoria | ±**10 000** (− profundidad) |
| Límite de turnos | **200** (empate) |
| Reglas de validación | **9** del PDF + unidades superpuestas |

---

## 7. Qué queda faltando (al 20 oct en la noche)
- [ ] **Inscribir el grupo** en la hoja del profesor.
- [ ] **Estudiar con este documento** y ensayar el guion con Daniel (una vez completa, con cronómetro).
- [ ] **Revisar el código** que se va a mostrar: `reglas.py`, `algoritmos.py`, `heuristicas.py`, `utilidad.py` y `minimax.py`.
- [ ] *(Opcional)* Diapositivas para apoyar la presentación.
- [ ] Más adelante: preparar la sustentación **individual** con el banco de preguntas y `/sustentacion NNN`.
