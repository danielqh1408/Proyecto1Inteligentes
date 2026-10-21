# Guion breve de demostración

**TacticalGrid · Juan David Ocampo González y Daniel Quintero Hurtado**
Sistemas Inteligentes I · Universidad de Caldas · 21 de octubre de 2026

## Antes de empezar

Abra la versión actual del repositorio y la interfaz. Use los escenarios de escenarios/casos. En cada prueba: **predecir, ejecutar, comparar y explicar**. Cambie una sola opción y no avance turnos durante comparaciones adversariales. La tabla conserva las consultas de Decidir del mismo estado; al mover se limpia.

Reparto sugerido: Juan presenta navegación, costos y heurísticas (casos 1–5); Daniel presenta estado compuesto y decisiones (6–10). Ambos deben poder explicar cualquier módulo. Si el tiempo es corto, prioricen casos 2, 3, 6, 8, 9 y 10 y mantengan los demás disponibles.

## Apertura

“TacticalGrid es un entorno para comparar cómo decide un sistema inteligente. Primero buscamos una ruta; después minimizamos su costo, incorporamos heurísticas y finalmente consideramos las respuestas del rival. Gana quien lleva el recurso a su propia base”.

“El escenario contiene mapa, terrenos, costos y bases. El estado contiene posiciones actuales, portador, recurso libre, turno y turnos jugados. El JSON define el escenario y la configuración sin modificar el código”.

## Casos 1 y 2: ruta y costo

**Caso 1.** Ejecute BFS y DFS con la configuración cargada. Verifique ambos.

“BFS explora por niveles y encuentra 29 movimientos. DFS profundiza por una rama y encuentra 137. Aquí DFS expandió menos estados, pero su ruta fue más larga: menos exploración no equivale a mejor solución”.

**Caso 2.** Ejecute BFS y UCS.

“BFS minimiza movimientos: cruza el pantano en 17 pasos y cuesta 83. UCS minimiza el costo acumulado: rodea en 33 pasos y cuesta 33. Si el pantano sube de 7 a 15, BFS mantiene la ruta y cuesta 163; UCS conserva su rodeo de costo 33”.

## Casos 3 y 4: heurísticas

**Caso 3.** Ejecute A* con Manhattan y obstáculos sobre el mismo estado.

“A* prioriza f = g + h. g es el costo acumulado y h estima el restante. Manhattan ignora los muros. Nuestra segunda heurística calcula pasos mínimos esquivando muros y multiplica por el menor costo transitable presente en el mapa”.

“Ambas son admisibles porque no sobreestiman el costo óptimo restante. Obtienen costo 32; obstáculos reduce expansiones de 282 a 177. Prepararla requiere un BFS, por lo que menos expansiones no garantiza menor tiempo total”.

**Caso 4.** Ejecute UCS y A* con ambas heurísticas.

“Los tres encuentran costo óptimo 64. Las expansiones son 332, 294 y 289. La mejora de obstáculos frente a Manhattan es pequeña aquí: su utilidad depende del mapa y no diferencia los terrenos caros más allá del costo mínimo”.

## Casos 5 y 6: alternativas y estado

**Caso 5.** Mantenga Beam con Manhattan y pruebe k = 1, 2, 4, 8.

“k limita los candidatos conservados para el siguiente nivel. Con uno, Beam pierde la ruta al escoger el callejón sin salida; con dos encuentra costo 21. Aumentar k explora más, pero aquí no mejora el costo. Beam no garantiza completitud ni optimalidad. k tampoco limita toda la memoria”.

**Caso 6.** Ejecute UCS con Misión activada.

“La unidad va al recurso y vuelve a su base: 20 movimientos y costo 22. Repite posiciones, pero no el mismo estado: una vez pasa sin recurso y otra con él. Por eso la misión representa posición y lleva_recurso. El objetivo es base propia con recurso”.

## Utilidad: antes de demostrar Minimax

“MAX es el bando que decide y MIN el rival dentro de ese árbol. MIN no está en desventaja: reducir la utilidad de MAX favorece sus propios intereses”.

“La evaluación es 20 por posesión, más 3 por carrera, más 0.1 por movilidad. Posesión vale 1 si lo llevo, -1 si lo lleva el rival y 0 si está libre. Carrera es restante rival menos restante propio. Movilidad es acciones propias menos rivales. Los valores son estimaciones, no probabilidades”.

“Una victoria tiene valor de al menos 10000 y domina cualquier ventaja provisional. La aproximación de persecución tiene limitaciones: combina Manhattan y costos e ignora el reinicio del recurso tras interceptar”.

## Casos 7 y 8: anticipación y poda

**Caso 7.** Minimax natural, profundidades 1 y 4. Pulse Decidir, no Siguiente turno.

“A profundidad 1 elige A2 hacia (8,11), favorable inmediatamente. A profundidad 4 prefiere (9,12), una posición útil frente a la respuesta de B. Elegimos el mejor resultado suponiendo que el adversario responde a favor suyo”.

**Caso 8.** Compare Minimax y alfa-beta, ambos con profundidad 4 y orden natural. Verifique.

“Los dos eligen A2 hacia (12,6) con valor -47. Minimax evalúa 20478 hojas; alfa-beta, 427. Alfa-beta evita ramas que ya no pueden cambiar la elección y conserva el resultado del árbol limitado”.

“Si todas las opciones son negativas, MAX elige la menos desfavorable. El desglose es del hijo inmediato: no tiene por qué sumar el valor calculado varios niveles después”.

## Casos 9 y 10: orden y profundidad

**Caso 9.** Alfa-beta, profundidad 4; natural, inverso y heurístico.

“Los tres mantienen valor -47. Inverso puede seleccionar otra acción empatada. Natural usa 428 evaluaciones totales; heurístico usa 2976, aunque ahorra una hoja. El costo de ordenar debe incluirse: no basta con comparar las hojas”.

“Los valores de acciones no elegidas en alfa-beta pueden ser cotas, porque se podó antes de calcular su valor exacto”.

**Caso 10.** Alfa-beta natural, profundidades 1–5. Señale la tabla acumulada.

| Profundidad | Acción | Valor | Hojas evaluadas |
|---|---|---|---|
| 1 | A1 a (9,8) | -35 | 12 |
| 2 | A2 a (11,7) | -41 | 34 |
| 3 | A2 a (11,7) | -38 | 166 |
| 4 | A2 a (12,6) | -47 | 427 |
| 5 | A2 a (12,6) | -44 | 2012 |

“Cada nivel agrega una acción individual: A, B, A… El trabajo aumenta. La primera acción puede mantenerse mientras cambia el valor, porque ahora se evalúan continuaciones más lejanas. No hay obligación de que el valor aumente ni garantía de ganar por usar más profundidad”.

## Verificación, límites y cierre

“Verificar revisa rutas, costos y objetivos. En adversarial comprueba acciones de la raíz, sucesores y equivalencia entre Minimax y alfa-beta. No vuelve a recorrer todos los nodos internos del árbol; las transiciones comparten el generador de acciones legales”.

“Si no hay acciones, se pasa. Una intercepción devuelve el recurso al origen y al antiguo portador a su inicio si está libre. El juego puede repetir movimientos y termina en empate al alcanzar el límite sin ganador. No prometemos progreso constante”.

“El repositorio incluye código, escenarios, experimentos reproducibles, manual, documento técnico y declaración de IA. Las pruebas automáticas verifican comportamiento; la explicación y responsabilidad sobre la entrega son nuestras”.

## Respuestas rápidas para no confundir conceptos

| Pregunta | Respuesta corta |
|---|---|
| ¿Por qué h es admisible? | Porque h no supera el costo óptimo restante; no exige que exista una ruta de costo exactamente h. |
| ¿Qué es c_min? | El menor costo de una entrada a terreno transitable presente en el mapa. |
| ¿La misma acción debe conservar el mismo valor a distinta profundidad? | No; el horizonte evaluado cambia. |
| ¿Más k siempre mejora? | No; puede aumentar trabajo sin mejorar solución y no garantiza completitud. |
| ¿Orden heurístico usa obstáculos? | No; usa la evaluación de posesión, carrera y movilidad. |
| ¿Qué significa negativo? | Desfavorable según la evaluación para el bando MAX, no derrota segura. |
| ¿Qué cambia el algoritmo superior de la GUI? | El agente de Decidir. Juega A/B controla la ejecución de turnos. |
| ¿Uso de IA? | Declarado por método y en USO_IA.md; no sustituye la comprensión individual. |

Fuente: código actual y resultados/RESUMEN.md, E1–E6. Los tiempos se interpretan en la ejecución presente; no se memorizan como constantes. Guion preparado con apoyo de Codex a partir del ensayo de Juan.
