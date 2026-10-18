# 000 — Constitución del proyecto

Principios **no negociables**. Toda spec, plan, código o revisión se contrasta contra esta lista. Si una tarea exige violar uno, se detiene y se discute en equipo.

## P1. El enunciado y el JSON común son el contrato
- El PDF (`docs/Primer proyecto.pdf`) prevalece sobre cualquier otro documento.
- El formato JSON común se carga **sin modificar código**. Los nombres de campos y valores del enunciado se respetan; los campos extra propios no cambian el significado de los obligatorios.
- Durante la sustentación no habrá cambios de código para adaptar el mapa del profesor ⇒ **ningún supuesto** sobre dimensiones, posiciones, número de unidades o costos.

## P2. Separación de capas
Escenario (representación) · Juego (estado y reglas) · Búsqueda/Decisión (algoritmos) · Interfaz (GUI). Las dependencias solo apuntan hacia abajo. Los algoritmos reciben un **problema** abstracto; no conocen la GUI ni el formato JSON.

## P3. Nada quemado
Costos ⇒ `tipos_terreno`. Profundidad Minimax ⇒ `juego.profundidad_maxima_minimax` / CLI / GUI. `k` de Beam, heurística, orden de acciones y pesos de utilidad ⇒ configuración externa. Las constantes por defecto viven **solo** en `tacticalgrid/config.py`, nunca dispersas en algoritmos.

## P4. Modelado explícito y suficiente
Para cada problema se declara: estado, estado inicial, acciones válidas, función sucesor, prueba de objetivo y costo. Se justifica por qué el estado contiene **toda** la información necesaria (p. ej. dos estados con la unidad en la misma casilla difieren si una lleva el recurso).

## P5. Determinismo y reproducibilidad
Sin aleatoriedad (o con semilla fija registrada). Orden de sucesores explícito y configurable. Empates en colas de prioridad resueltos por contador de inserción. Todo experimento reportado puede regenerarse con un comando.

## P6. Métricas uniformes
Las métricas (solución, longitud, costo, generados, expandidos, máximo de frontera, tiempo; y para adversarial: generados, evaluados, podados, profundidad, tiempo, acción, valor) tienen **una única definición** (specs 003 y 005) y todos los algoritmos las reportan igual.

## P7. Verificabilidad
Toda respuesta de un algoritmo puede comprobarse con el verificador (spec 006). En los tests, **todo** resultado de búsqueda exitoso pasa por el verificador.

## P8. Carga atómica y errores claros
Validar primero, reemplazar después. Un escenario inválido produce la **lista completa** de errores legibles y deja intacto el estado anterior.

## P9. Documentación de ingeniería honesta
Métodos relevantes con: Purpose, Preconditions, Postconditions, Complexity, AI usage, AI intervention, Student validation. La documentación describe la versión **real** del método; si el código cambia, la doc cambia en el mismo commit.

## P10. Comprensión antes que funcionalidad
"Una funcionalidad que opere correctamente, pero que el estudiante no pueda explicar, justificar o adaptar durante la sustentación, no demostrará dominio suficiente." Ningún código se integra sin que el otro integrante lo haya revisado y pueda explicarlo. La IA se declara siempre.

## P11. Simplicidad
Núcleo con librería estándar. Sin combate complejo ni efectos visuales. Se prefiere la solución que se pueda explicar en el tablero.

## P12. Spec primero
Cambio de comportamiento ⇒ spec ⇒ test ⇒ código ⇒ documentación. Un PR/commit que cambie comportamiento sin tocar la spec se rechaza en revisión.
