# Daniel: lee esto primero

> **De:** Juan · **Para:** Daniel · **Fecha:** 17 de octubre de 2026
> **Tiempo de lectura:** unos 40 minutos.
> **Nada de lo que hay en este repo está decidido.** Es una propuesta que armé con Claude Code para empezar con buen pie. La idea es que la discutamos, la entendamos los dos y la ajustemos antes de escribir una sola línea de código.

---

## 1. ¿Por qué te pido leer esto?

Antes de programar, quise organizar el proyecto de forma que:

1. **Los dos entendamos todo.** La sustentación es **individual** y vale **50 %**. El enunciado dice que una funcionalidad que funciona pero que uno no sabe explicar "no demostrará dominio suficiente". Así que no sirve que cada uno sepa solo su parte.
2. **Tomemos juntos las decisiones de diseño.** El enunciado deja muchas cosas abiertas: cómo es el estado, qué reglas aplican cuando alguien se bloquea, cuál es la segunda heurística, la función de utilidad, la interfaz… Si cada uno decide por su lado, terminamos con un sistema incoherente que ninguno de los dos puede defender completo.
3. **Usemos IA sin que nos perjudique.** El profesor permite IA, pero exige **declararla en cada método** y explicar cómo la validamos. Necesitamos una forma ordenada de usarla y de dejar registro.

Para eso propongo una forma de trabajo llamada **SDD (Spec‑Driven Development)**. Abajo te explico qué es, sin tecnicismos.

---

## 2. ¿Qué es SDD? (en simple)

**SDD = primero escribimos *qué* debe hacer cada parte y *cómo sabremos que está bien*; después programamos.**

Es lo mismo que haríamos en un parcial bien hecho: leer el enunciado, decidir el modelo, definir qué vamos a probar y solo después escribir el código. La diferencia es que lo dejamos **por escrito en el repo**, en archivos que se llaman *specs* (especificaciones).

Cada spec tiene:

| Sección | Para qué sirve |
|---|---|
| Requisitos | Lo que pide el PDF, citado. Así no se nos olvida nada de la rúbrica |
| Decisiones | Qué elegimos y **por qué**, con las alternativas descartadas. Es lo que nos van a preguntar |
| Diseño | Archivos, funciones y estructuras de datos |
| Criterios de aceptación | Frases como "dado X, cuando Y, entonces Z". **Cada una se vuelve una prueba automática** |
| Tareas | Lista de pendientes con responsable |
| Para sustentar | Preguntas que probablemente hará el profesor, con la respuesta corta |

**El ciclo de trabajo es siempre el mismo:**

```
leer/ajustar la spec  →  escribir las pruebas  →  programar  →  verificar  →  documentar  →  practicar la sustentación
```

### ¿Por qué nos sirve en este proyecto en particular?

- **La rúbrica es muy específica:** modelado 15 %, BFS/DFS/UCS 15 %, A\*/Beam 20 %, Minimax 20 %, etc. Hay una spec por cada criterio, así vemos qué falta.
- **El profesor va a probar con un JSON que nunca hemos visto** y cambiará costos en vivo. Las pruebas automáticas nos avisan si algo quedó "quemado" en el código.
- **Las secciones "Para sustentar" son nuestro material de estudio**, y lo vamos llenando mientras construimos.
- **La IA trabaja mejor con instrucciones claras.** Si le damos la spec, hace lo que acordamos y no lo que se le ocurra.

---

## 3. Recorrido por el repo: qué hay y en qué orden leerlo

| Orden | Archivo | Qué es | Tiempo |
|---|---|---|---|
| 1 | **Este documento** | Contexto y decisiones a discutir | 20 min |
| 2 | [`docs/00_ENTENDIMIENTO.md`](00_ENTENDIMIENTO.md) | El enunciado explicado: qué vimos en clase, qué cambia, qué hará el profesor en la sustentación, y una tabla que conecta cada requisito con la parte del código y de la rúbrica | 10 min |
| 3 | [`specs/000-constitucion.md`](../specs/000-constitucion.md) | 12 reglas que no rompemos (por ejemplo: "los costos solo salen del JSON") | 5 min |
| 4 | [`specs/002-modelo-estado-reglas/spec.md`](../specs/002-modelo-estado-reglas/spec.md) | Cómo representamos el estado y las reglas del juego. Es lo más importante para decidir juntos | 10 min |
| 5 | [`specs/005-adversarial/spec.md`](../specs/005-adversarial/spec.md) | Minimax, alfa‑beta y la función de utilidad (propuesta para ti) | 10 min |
| — | Las demás specs (001, 003, 004, 006–009) | Léelas cuando toque implementarlas o revisarlas | — |
| — | [`docs/DECISIONES.md`](DECISIONES.md), [`docs/ARQUITECTURA.md`](ARQUITECTURA.md) | Referencia técnica | — |

Estructura general:

```
PrimerProyecto/
├── README.md          → presentación del proyecto (integrantes, cómo correrlo)
├── AGENTS.md          → "manual" para cualquier IA que trabaje en el repo (y para nosotros)
├── CLAUDE.md          → instrucciones extra solo para Claude Code
├── specs/             → las especificaciones (000 a 009)
├── docs/              → entendimiento, arquitectura, decisiones, guía de sustentación, registro de IA
├── escenarios/        → archivos JSON (ya está el ejemplo del PDF)
├── tacticalgrid/      → (aún no existe) el código
├── tests/             → (vacío) las pruebas automáticas
└── .claude/           → configuración de los "agentes" (ver sección 5)
```

---

## 4. Cómo trabajaríamos día a día

### 4.1 Reparto (propuesta, se puede cambiar)

| | Juan | Daniel |
|---|---|---|
| **Responsable de** | 001 JSON y validación · 003 BFS/DFS/UCS · 004 A\*/heurísticas/Beam · 008 experimentos | 002 estado y reglas · 005 Minimax/alfa‑beta/utilidad · 006 verificación · 007 interfaz |
| **Revisor de** | 002, 005, 006, 007 | 001, 003, 004, 008 |
| **Los dos** | 009 documentación, diseño de los 10 casos mínimos, simulacros | ídem |

Quedan más o menos 50/50 según los porcentajes de la rúbrica. **Ser revisor significa poder explicar el código del otro.** Así nos preparamos para la sustentación.

### 4.2 Git (para que el repo muestre el aporte de cada uno, como pide el enunciado)

1. Una rama por tarea: `feat/003-ucs`, `feat/005-alfa-beta`…
2. Pull Request hacia `main`. **El otro revisa y aprueba**, y si algo no se entiende, se pregunta en el PR.
3. Cada uno hace commit **con su propia cuenta**. Mensajes tipo `feat(busqueda): costo uniforme con métricas`.

### 4.3 Ejemplo concreto: cómo se haría UCS

1. Juan abre `specs/003-…/spec.md` y lee los criterios. Por ejemplo, CA‑003‑3: "en el caso 2, BFS da menos pasos pero UCS da menor costo".
2. Escribe primero la prueba `test_caso02` (todavía falla, porque no hay código).
3. Programa `costo_uniforme` con el mismo estilo del notebook de clase (`heapq`, `count()`, `mejor_g`).
4. Corre `pytest`. Cuando pasa, el **verificador** revisa que el camino sea válido y que el costo reportado sea el real.
5. Documenta el método con los 7 campos que exige el profesor (Purpose, Preconditions, Postconditions, Complexity, AI usage, AI intervention, Student validation).
6. Abre el PR. **Daniel lo revisa** y, para aprobarlo, practica con el simulador de preguntas sobre UCS.

---

## 5. ¿Qué son AGENTS.md, CLAUDE.md, los "agentes" y los "arneses"?

Esto es lo más nuevo, así que va con calma.

### 5.1 AGENTS.md y CLAUDE.md
Son **archivos de contexto para la IA**. Cuando abrimos una herramienta de IA en el repo (Claude Code, Antigravity/Gemini, Copilot, Cursor…), esta lee automáticamente ese archivo y sabe de qué trata el proyecto, qué reglas seguir, cómo nombrar las cosas y qué no hacer. Así no hay que explicárselo todo cada vez.
- `AGENTS.md` es el estándar que leen varias herramientas, y también nos sirve a nosotros como resumen del proyecto.
- `CLAUDE.md` solo agrega instrucciones para Claude Code. Por ejemplo: "actúa como tutor, explica antes de programar, nunca digas que no se usó IA en algo que tú escribiste".

**No tienes que usar Claude Code.** Si prefieres Antigravity o Gemini (como en el primer corte), el `AGENTS.md` sirve igual. Lo único importante es que **las reglas son las mismas para los dos**.

### 5.2 Los "agentes" (roles de IA)
En `.claude/agents/` hay cinco "personajes" con instrucciones distintas. Es como pedirle a la IA que se ponga un sombrero específico:

| Agente | Hace | No hace |
|---|---|---|
| `arquitecto-specs` | Escribe y ajusta las specs a partir del PDF | No programa |
| `implementador` | Programa **una** tarea de una spec aprobada: pruebas primero, luego código y documentación | No cambia decisiones ni hace commits |
| `verificador` | Corre todas las pruebas y revisa reglas (por ejemplo, que no haya costos escritos a mano) | No arregla; solo reporta |
| `auditor-documentacion` | Revisa que la documentación coincida con el código y que el uso de IA esté declarado | No inventa validaciones |
| `examinador-sustentacion` | **Hace de profesor:** pregunta, pide predicciones antes de ejecutar y propone cambios pequeños | No da la respuesta antes de que uno intente |

Y hay atajos (comandos): `/implementar-spec 003`, `/verificar`, `/sustentacion 005`.

### 5.3 Los "arneses"
"Arnés" (*harness*) es todo lo que **rodea** al trabajo para atrapar errores sin depender de la memoria de nadie. Es como el arnés de un escalador: no te hace subir, pero evita que te caigas. Tenemos varios:

| Arnés | Qué atrapa |
|---|---|
| **De contexto** (AGENTS.md, specs, decisiones) | Que la IA o uno mismo cambie el diseño sin querer |
| **De pruebas** (`pytest`) | Errores de lógica, costos quemados, Minimax y alfa‑beta eligiendo acciones distintas, heurísticas que sobreestiman |
| **De verificación** (lo exige el PDF) | Caminos que atraviesan muros, costos mal sumados, jugadas ilegales en Minimax |
| **De experimentos** | Que los resultados del informe se puedan regenerar con un solo comando |
| **De sustentación** (examinador + guía) | Que lleguemos sin poder explicar algo |

---

## 6. Las decisiones que tenemos que tomar JUNTOS ⭐

Esta es la parte importante. Para cada decisión: qué propongo, por qué, qué alternativas hay y una pregunta para discutir. Marca tu opinión y lo hablamos.

> Leyenda: ✅ de acuerdo · ✏️ cambiaría algo · ❓ hay que discutirlo

### Bloque A: Modelado (15 % de la nota, y la base de todo)

**A1. ¿Qué es un "estado" del juego?**
Propuesta: lo que **no cambia** (mapa, costos, bases, quién es cada unidad) va aparte, en el *escenario*. El **estado** solo guarda lo que cambia:
- posición de cada unidad
- quién lleva el recurso (o nadie)
- dónde está el recurso si está libre
- de quién es el turno
- cuántos turnos se han jugado

*Por qué:* con eso se puede calcular todo: las jugadas legales, si alguien ganó, el valor para Minimax. Y cumple lo que pide el PDF: "dos estados con la unidad en la misma casilla pueden ser diferentes si una lleva el recurso".
*Pregunta:* ¿hace falta guardar "turnos jugados" en el estado? (Yo digo que sí: si hay límite de turnos, el mismo tablero en el turno 10 y en el 200 no es igual.)
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

**A2. ¿Qué acciones existen?**
Propuesta: **MOVER** (arriba, abajo, izquierda, derecha), **INTERCEPTAR** (si estoy al lado del portador enemigo, le quito el recurso) y **PASAR** (solo si no puedo hacer nada más).
*Alternativas:* agregar "ESPERAR" siempre disponible (más realista, pero el árbol de Minimax crece) o que el recurso caiga al suelo al interceptar (más estados y más casos raros).
*Pregunta:* ¿interceptar debe quitarle el recurso al otro, o "tumbarlo" y que quede en el suelo?
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

**A3. Regla: nadie puede entrar a la base enemiga**
*Por qué:* las bases son **una sola casilla**. Si no existe esta regla, la estrategia ganadora es parar una unidad encima de la base rival y el rival nunca puede ganar. El juego se rompe y Minimax lo descubriría.
*Pregunta:* ¿están de acuerdo, o prefieres otra solución (por ejemplo, que la base sea una zona de varias casillas)?
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

**A4. Bloqueos y empates**
Propuesta:
- Si un bando no tiene jugadas, **pasa**.
- Si los dos pasan seguidos, es empate.
- Si se llega a un límite de turnos (200 por defecto, se puede cambiar desde el JSON), es empate.

*Pregunta:* ¿200 está bien, o lo dejamos más bajo para que las partidas de demostración sean cortas?
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

**A5. En modo "búsqueda", ¿las otras unidades estorban?**
El PDF dice que en la primera etapa se ignora al adversario. Propuesta: **por defecto no estorban**, pero hay una opción en el JSON para tratarlas como obstáculos.
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

**A6. ¿Unidades iguales o de tipos distintos?**
Propuesta: **todas iguales** (`estandar`). El PDF lo permite y pide no complicar. Si sobra tiempo, se podría agregar un "explorador" al que el bosque le cueste menos.
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

### Bloque B: Búsqueda (35 % de la nota)

**B1. ¿Cuándo se revisa si se llegó al objetivo?**
Propuesta: **al sacar el estado de la frontera** en los cinco algoritmos, como en el notebook de UCS/A\*. Así las métricas se pueden comparar entre algoritmos, y es necesario para que UCS y A\* den el óptimo.
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

**B2. La segunda heurística (la "propia")**
- **H1 (Manhattan):** filas + columnas de distancia, multiplicado por el costo del terreno más barato del mapa.
  - ¿Por qué multiplicar? Si el profesor pone un terreno que cuesta 0.5, la Manhattan normal **sobreestima** y A\* deja de dar el óptimo. Es una pregunta trampa típica.
- **H2 (propuesta: "distancia con obstáculos"):** cuántos pasos hay realmente hasta el objetivo **esquivando muros** (un BFS hecho una sola vez desde el objetivo), multiplicado por el costo más barato.
  - Nunca sobreestima, así que es **admisible**.
  - Siempre es ≥ Manhattan, así que **domina** a H1 y A\* expande menos estados. Es justo lo que vimos en clase.
  - Funciona muy bien cuando hay muros (el caso 3 del PDF: "el objetivo parece cercano pero una barrera obliga a rodearlo").
  - No ayuda cuando no hay muros (queda igual a Manhattan) ni cuando lo que importa son los costos del terreno.

*Alternativa:* una heurística que use el costo promedio del terreno. Ayuda más, pero **no es admisible**; la dejaríamos solo como experimento para mostrar que A\* puede equivocarse.
*Pregunta:* ¿te convence H2 o se te ocurre otra?
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

**B3. Beam Search**
Propuesta: igual que en el notebook. Va por niveles, se queda con los k mejores según la heurística, y lo que se descarta ya no se vuelve a visitar. Por eso con k = 1 puede fallar aunque exista camino, que es exactamente lo que el PDF pide analizar.
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

### Bloque C: Adversarial (20 % de la nota)

**C1. ¿Quién es MAX?**
Propuesta: **el bando que tiene el turno** cuando se pide la decisión. La función de evaluación es **la misma para los dos con el signo contrario** (lo bueno para A es igual de malo para B). Por eso **MIN no está en desventaja**, que es una pregunta segura en la sustentación.
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

**C2. La función de utilidad (la diseñamos nosotros)**
Propuesta:
- **Si alguien ganó:** ±10 000, con un pequeño bono por ganar en menos jugadas.
- **Si no:** la suma ponderada de cinco cosas:

| Componente | Idea | Peso inicial |
|---|---|---|
| Posesión | ¿Quién tiene el recurso? | 50 |
| Carrera al recurso | ¿Quién está más cerca del recurso libre? (distancia real con costos) | 2 |
| Progreso de entrega | ¿Qué tan lejos está el portador de su base? | 3 |
| Presión | ¿Qué tan cerca está el enemigo de mi portador, o yo del suyo? | 1.5 |
| Movilidad | ¿Cuántas jugadas tengo yo frente a las del rival? (si estoy bloqueado, es malo) | 0.1 |

- Los pesos se pueden cambiar **desde el JSON**, así que si el profesor pregunta "¿qué pasa si cambias los pesos?", lo mostramos en vivo.
- La interfaz mostrará el **desglose**: por qué una jugada vale más que otra.

*Preguntas:* ¿falta algo? ¿Te parecen bien los pesos como punto de partida? (Los vamos a ajustar con experimentos.)

> **Actualización (18 oct, al implementar):** al jugar partidas, la versión de 5 componentes hacía que una unidad al lado del recurso **no lo recogiera** (perdía el término de "carrera al recurso" y ganaba uno negativo de "entrega"). Se simplificó a 3 componentes: **posesión**, **carrera** = lo que le falta a cada bando para ganar (con costos reales) y **movilidad**. Detalle en `specs/005-adversarial/spec.md §4`. Revísalo y dime si estás de acuerdo.
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

**C3. Desempates**
Propuesta: si dos jugadas valen lo mismo, gana **la primera** en el orden de generación. Así Minimax y alfa‑beta siempre eligen **la misma** jugada (el PDF lo exige y lo vamos a probar automáticamente).
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

### Bloque D: Tecnología y organización

**D1. Lenguaje:** Python 3.12, como en los notebooks. El núcleo usaría solo la librería estándar; las pruebas, `pytest`.
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

**D2. Interfaz gráfica: `tkinter`**
*Por qué:* ya viene con Python, tiene diálogo para abrir archivos (el JSON del profesor), botones, listas y tablas, y un lienzo para dibujar la cuadrícula. El PDF dice que lo visual **no** es el centro de la nota (vale 5 %).
*Alternativas:*
- **Pygame:** hay que construir los botones, las tablas y el selector de archivos a mano.
- **Streamlit:** cómodo para gráficas, incómodo para un juego por turnos.
- **Web:** otro lenguaje y otra capa.

⚠️ En Mac con Python de Homebrew hay que instalar Tk (`brew install python-tk@3.12`). **¿Puedes probar si te funciona en tu computador?** Corre esto:
```bash
python3 -c "import tkinter; tkinter.Tk().mainloop()"
```
Si se abre una ventana vacía, funciona.
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

**D3. Reparto de trabajo** (sección 4.1).
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

**D4. Flujo de Git con ramas y Pull Requests revisados por el otro.**
Tu opinión: ☐ ✅ ☐ ✏️ ☐ ❓

---

## 7. Ejercicio para entendernos (15 minutos, con lápiz)

Usa el mapa de ejemplo del PDF (`escenarios/ejemplo_enunciado.json`). Costos: camino 1, pasto 2, bosque 4, pantano 7. El muro no se puede atravesar.

```
        col0     col1     col2      col3
fila0   camino   camino   pasto     pasto      Base A = (0,0)
fila1   camino   MURO     bosque    pasto
fila2   camino   camino   pantano   pasto      Recurso = (2,2)
fila3   pasto    pasto    camino    camino     Base B = (3,3)
```

La unidad A1 está en (0,1) y debe llegar a (3,2). El costo de un camino es la suma de los costos de las casillas a las que **entra** (no cuenta la de inicio).

1. ¿Qué camino encuentra **BFS** (el de menos pasos)? ¿Cuántos pasos y cuánto cuesta?
2. ¿Qué camino encuentra **UCS** (el más barato)? ¿Cuántos pasos y cuánto cuesta?
3. Si el profesor cambia el pantano de 7 a **15**, ¿qué le pasa a cada uno?
4. ¿Y si lo cambia a **1**?

<details>
<summary>Respuestas (no mires antes 😉)</summary>

1. **BFS:** (0,1) → (0,2) → (1,2) → (2,2) → (3,2). Son **4 pasos**, el mínimo posible, porque (1,1) es muro. Costo = 2 + 4 + 7 + 1 = **14**.
2. **UCS:** (0,1) → (0,0) → (1,0) → (2,0) → (2,1) → (3,1) → (3,2). Son **6 pasos** con costo = 1 + 1 + 1 + 1 + 2 + 1 = **7**. Más largo pero la mitad de caro: este es justamente el **caso 2** del PDF ("ruta corta vs. ruta económica").
3. **Pantano = 15:** BFS sigue eligiendo el mismo camino, porque no mira costos, pero ahora cuesta 22. UCS no cambia, porque no pasaba por el pantano: sigue costando 7.
4. **Pantano = 1:** BFS cuesta 2 + 4 + 1 + 1 = 8. UCS encuentra (0,0) → (1,0) → (2,0) → (2,1) → (2,2) → (3,2), con costo **6**.

Este es el tipo de **predicción antes de ejecutar** que pedirá el profesor.
</details>

---

## 8. Lo que te pido

1. Leer este documento y los archivos 2–5 de la tabla de la sección 3.
2. Marcar tu opinión en cada decisión de la sección 6. Puedes editar este archivo, comentar en el PR o mandarme tus notas.
3. Probar si `tkinter` te funciona (D2).
4. Hacer el ejercicio de la sección 7.
5. Cuadrar una reunión corta (unos 45 min) para cerrar las decisiones. Después marcamos cada una como `aceptada` en [`docs/DECISIONES.md`](DECISIONES.md) y empezamos a programar por la spec 001 (cargar y validar el JSON) y la 002 (estado y reglas) en paralelo.

**Si algo de la metodología te parece demasiado, también lo hablamos.** La idea es que nos sirva para aprender y sustentar bien, no que sea burocracia. Lo mínimo que yo no negociaría es:
- las pruebas automáticas
- revisar el código del otro
- declarar la IA

---

## 9. Mini‑glosario

| Término | Significado |
|---|---|
| **Spec** | Documento que dice qué debe hacer una parte del sistema y cómo comprobarlo |
| **Criterio de aceptación** | Frase verificable ("dado… cuando… entonces…") que se vuelve una prueba |
| **Test / prueba automática** | Código que comprueba otro código; se corre con `pytest` |
| **Arnés (harness)** | Todo lo que rodea al trabajo para atrapar errores: pruebas, verificador, specs, reglas |
| **Agente / subagente** | Una IA con instrucciones de un rol específico (implementar, verificar, examinar…) |
| **AGENTS.md / CLAUDE.md** | Archivos que las herramientas de IA leen solas para entender el proyecto |
| **ADR / decisión** | Registro de una decisión de diseño con su porqué (`docs/DECISIONES.md`) |
| **PR (Pull Request)** | Propuesta de cambio en GitHub que el otro revisa antes de unirla a `main` |
| **Admisible** | Heurística que nunca sobreestima el costo real |
| **Dominancia** | h₂ ≥ h₁ y ambas admisibles ⇒ h₂ es mejor guía (expande menos) |
