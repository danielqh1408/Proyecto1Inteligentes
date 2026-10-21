"""Ejecuta una prueba de búsqueda (``prueba.modo = "busqueda"``) con cualquier algoritmo.

Punto único que usan la CLI, la GUI y los experimentos. Lo que no se pase como argumento
se toma de ``prueba`` en el JSON (algoritmo, heuristica, k, orden_movimientos, unidades_bloquean, mision).
"""

from __future__ import annotations

from time import perf_counter

from tacticalgrid.busqueda.algoritmos import a_estrella, beam_search, bfs, costo_uniforme, dfs
from tacticalgrid.busqueda.heuristicas import crear_heuristica
from tacticalgrid.busqueda.problema import ProblemaMision, ProblemaNavegacion
from tacticalgrid.config import ORDEN_MOVIMIENTOS

ALGORITMOS = ("BFS", "DFS", "UCS", "A_ESTRELLA", "BEAM")
# Otros nombres con los que el profesor podría escribir el algoritmo en el JSON.
ALIAS = {"A*": "A_ESTRELLA", "ASTAR": "A_ESTRELLA", "A_STAR": "A_ESTRELLA", "AESTRELLA": "A_ESTRELLA",
         "COSTO_UNIFORME": "UCS", "BEAM_SEARCH": "BEAM", "BEAMSEARCH": "BEAM"}


def crear_problema(escenario, unidad=None, objetivo=None, mision=None, orden=None, unidades_bloquean=None):
    """Problema de navegación (o de misión) según la prueba del JSON y los argumentos dados."""
    prueba = escenario.prueba or {}
    unidad = unidad or prueba.get("unidad_inicio")
    if unidad not in [u.id for u in escenario.unidades]:
        raise ValueError(f"La prueba de búsqueda necesita una unidad existente (unidad_inicio = {unidad!r})")
    orden = orden or prueba.get("orden_movimientos", ORDEN_MOVIMIENTOS)
    if len(orden) != 4 or set(orden) != set(ORDEN_MOVIMIENTOS):
        raise ValueError("El orden debe contener arriba, abajo, izquierda y derecha una vez cada una")
    mision = prueba.get("mision", False) if mision is None else mision
    if unidades_bloquean is None:
        unidades_bloquean = prueba.get("unidades_bloquean", False)
    bloqueadas = [u.pos for u in escenario.unidades if u.id != unidad] if unidades_bloquean else []
    if mision:
        return ProblemaMision(escenario, unidad, orden, bloqueadas)
    if objetivo is None:
        if "objetivo" not in prueba:
            raise ValueError("La prueba de búsqueda necesita un objetivo (prueba.objetivo o --objetivo f,c)")
        objetivo = (prueba["objetivo"]["fila"], prueba["objetivo"]["columna"])
    if len(objetivo) != 2 or any(type(x) is not int for x in objetivo) or not escenario.dentro(objetivo):
        raise ValueError("El objetivo debe ser una pareja fila,columna dentro del mapa")
    inicio = next(u.pos for u in escenario.unidades if u.id == unidad)
    return ProblemaNavegacion(escenario, inicio, tuple(objetivo), orden, bloqueadas)


def ejecutar_busqueda(escenario, algoritmo=None, heuristica=None, k=None, problema=None, **opciones_problema):
    """Corre ``algoritmo`` sobre la prueba del escenario y devuelve el ``Resultado``."""
    prueba = escenario.prueba or {}
    algoritmo = str(algoritmo or prueba.get("algoritmo", "BFS")).upper().replace("-", "_").replace(" ", "_")
    algoritmo = ALIAS.get(algoritmo, algoritmo)
    heuristica = heuristica or prueba.get("heuristica", "manhattan")
    k = prueba.get("k", 2) if k is None else k
    problema = problema or crear_problema(escenario, **opciones_problema)
    if algoritmo == "BFS":
        return bfs(problema)
    if algoritmo == "DFS":
        return dfs(problema)
    if algoritmo == "UCS":
        return costo_uniforme(problema)
    t0 = perf_counter()
    h = crear_heuristica(heuristica, problema)
    preparacion_ms = (perf_counter() - t0) * 1000
    if algoritmo == "A_ESTRELLA":
        resultado = a_estrella(problema, h)
    elif algoritmo == "BEAM":
        resultado = beam_search(problema, h, k)
    else:
        raise ValueError(f"Algoritmo desconocido '{algoritmo}'. Válidos: {', '.join(ALGORITMOS)}")
    resultado.extra["heuristica"] = heuristica
    resultado.preparacion_ms = preparacion_ms
    return resultado
