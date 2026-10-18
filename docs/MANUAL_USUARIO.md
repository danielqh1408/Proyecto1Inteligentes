# Manual de usuario — TacticalGrid

> Borrador redactado con Claude Code (ver `docs/USO_IA.md`). **Pendiente:** agregar capturas de pantalla de la interfaz (carpeta `docs/capturas/`) y revisarlo.

## 1. Instalación

Requisitos: Python 3.11 o superior con `tkinter` (solo para la interfaz gráfica).

```bash
git clone git@github.com:danielqh1408/Proyecto1Inteligentes.git
cd Proyecto1Inteligentes
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt      # solo pytest (y matplotlib opcional); el programa usa la librería estándar
```

**macOS con Python de Homebrew:** no trae `tkinter`. Opciones: `brew install python-tk@3.12`, o crear el entorno con el Python de `uv` (que sí lo trae): `uv venv -p 3.11 .venv`.

Comprobar que todo funciona: `pytest -q` (deben pasar todas las pruebas).

## 2. El escenario JSON

Todo sale del archivo JSON con el formato común del enunciado (`escenarios/ejemplo_enunciado.json` es el ejemplo del PDF). Campos opcionales propios que entiende el programa:

| Campo | Para qué | Por defecto |
|---|---|---|
| `juego.profundidad_maxima_minimax` | profundidad de Minimax / alfa‑beta | 3 |
| `juego.max_turnos` | límite de turnos de la partida (empate) | 200 |
| `juego.orden_acciones` | `natural`, `inverso` o `heuristico` | `natural` |
| `juego.pesos_utilidad` | p. ej. `{"posesion": 50, "carrera": 3, "movilidad": 0.1}` | esos valores |
| `prueba.algoritmo` | `BFS`, `DFS`, `UCS`, `A_ESTRELLA`, `BEAM` (o `MINIMAX`, `ALFA_BETA`, `VORAZ`) | `BFS` / `ALFA_BETA` |
| `prueba.heuristica` | `manhattan`, `obstaculos`, `manhattan_promedio`, `cero` | `manhattan` |
| `prueba.k` | ancho del haz de Beam Search | 2 |
| `prueba.orden_movimientos` | p. ej. `["arriba", "abajo", "izquierda", "derecha"]` | abajo, arriba, derecha, izquierda |
| `prueba.mision` | `true`: recoger el recurso y llevarlo a la base | `false` |
| `prueba.unidades_bloquean` | `true`: las otras unidades son obstáculos en la búsqueda | `false` |

Si el JSON tiene errores, el programa los lista todos (con el campo y la regla) y no lo carga.

## 3. Línea de comandos

| Comando | Qué hace |
|---|---|
| `python -m tacticalgrid validar a.json b.json …` | valida uno o varios escenarios |
| `python -m tacticalgrid ejecutar a.json` | hace lo que pida `prueba.modo` (búsqueda, adversarial o partida) y verifica |
| `python -m tacticalgrid buscar a.json [--algoritmo X --heuristica H --k N --mision --orden … --objetivo f,c --verificar]` | una búsqueda; imprime el resultado en el formato del enunciado |
| `python -m tacticalgrid comparar a.json` | tabla con BFS, DFS, UCS, A\* (2 heurísticas) y Beam k = 1, 2, 4, 8 |
| `python -m tacticalgrid decidir a.json [--algoritmo MINIMAX\|ALFA_BETA\|VORAZ --profundidad N --orden O --verificar]` | mejor acción del bando en turno y valor de cada acción |
| `python -m tacticalgrid partida a.json --a ALFA_BETA --b VORAZ --profundidad 3` | partida completa entre dos agentes |
| `python -m tacticalgrid experimentos` | regenera `resultados/` (10 casos + experimentos E1–E6) |
| `python -m tacticalgrid gui [a.json]` | interfaz gráfica |

## 4. Interfaz gráfica

**Barra superior:** *Cargar JSON…*, *Verificar* (comprueba lo último que se ejecutó) e información del turno, del portador del recurso y del resultado.

**Mapa:** cada color es un tipo de terreno (leyenda con costos debajo); gris oscuro = obstáculo; bordes azul/rojo = bases A/B; rombo amarillo = recurso libre; círculos = unidades (azul A, rojo B) con su id; borde dorado = portador del recurso. **Clic en una celda** = objetivo de la búsqueda (✕ naranja).

**Pestaña Búsqueda:** elegir unidad, algoritmo, heurística, k y orden de movimientos; casillas *Misión* y *Las otras unidades bloquean*.
- *Ejecutar*: dibuja los estados expandidos (puntos blancos) y el camino (línea naranja); agrega una fila a la tabla de métricas.
- *Animar exploración*: muestra la expansión paso a paso.
- *Comparar todos*: agrega a la tabla todos los algoritmos sobre el mismo problema.

**Pestaña Adversarial / Partida:** algoritmo, profundidad y orden de acciones.
- *Decidir*: flecha amarilla con la acción recomendada; en el cuadro de texto, métricas, desglose de la evaluación y valor de cada acción.
- *Juega A / Juega B*: HUMANO o un agente. *Siguiente turno* juega un turno; *Jugar hasta el final* juega hasta que alguien gane o se llegue al límite.
- Para jugar como HUMANO: elegir una acción de la lista y pulsar *Aplicar acción seleccionada*.
- *Reiniciar* vuelve al estado del JSON.

**Tabla de métricas:** acumula ejecuciones para comparar; *Limpiar tabla* y *Exportar JSON…*.

## 5. Ejemplos rápidos
- BFS vs UCS (caso 2): `python -m tacticalgrid comparar escenarios/casos/caso02_ruta_corta_vs_economica.json`
- Muro en U y heurísticas (caso 3): en la GUI, cargar el caso 3, algoritmo A_ESTRELLA, *Animar exploración* con `manhattan` y luego con `obstaculos`.
- Decisión adversarial (caso 7): `python -m tacticalgrid decidir escenarios/casos/caso07_decision_adversarial.json --verificar`
