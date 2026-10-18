"""Ejecuta una prueba de búsqueda (``prueba.modo = "busqueda"``) con cualquier algoritmo.

Punto único que usan la CLI, la GUI y los experimentos. Lo que no se pase como argumento
se toma de ``prueba`` en el JSON (algoritmo, heuristica, k, orden_movimientos, unidades_bloquean, mision).
"""

from __future__ import annotations

from tacticalgrid.busqueda.algoritmos import a_estrella, beam_search, bfs, costo_uniforme, dfs
from tacticalgrid.busqueda.heuristicas import crear_heuristica
from tacticalgrid.busqueda.problema import ProblemaMision, ProblemaNavegacion
from tacticalgrid.config import ORDEN_MOVIMIENTOS

ALGORITMOS = ("BFS", "DFS", "UCS", "A_ESTRELLA", "BEAM")


def crear_problema(escenario, unidad=None, objetivo=None, mision=None, orden=None, unidades_bloquean=None):
    """Problema de navegación (o de misión) según la prueba del JSON y los argumentos dados."""
    prueba = escenario.prueba or {}
    unidad = unidad or prueba.get("unidad_inicio")
    orden = orden or prueba.get("orden_movimientos", ORDEN_MOVIMIENTOS)
    mision = prueba.get("mision", False) if mision is None else mision
    if unidades_bloquean is None:
        unidades_bloquean = prueba.get("unidades_bloquean", False)
    bloqueadas = [u.pos for u in escenario.unidades if u.id != unidad] if unidades_bloquean else []
    if mision:
        return ProblemaMision(escenario, unidad, orden, bloqueadas)
    if objetivo is None:
        objetivo = (prueba["objetivo"]["fila"], prueba["objetivo"]["columna"])
    inicio = next(u.pos for u in escenario.unidades if u.id == unidad)
    return ProblemaNavegacion(escenario, inicio, tuple(objetivo), orden, bloqueadas)


def ejecutar_busqueda(escenario, algoritmo=None, heuristica=None, k=None, problema=None, **opciones_problema):
    """Corre ``algoritmo`` sobre la prueba del escenario y devuelve el ``Resultado``."""
    prueba = escenario.prueba or {}
    algoritmo = (algoritmo or prueba.get("algoritmo", "BFS")).upper()
    heuristica = heuristica or prueba.get("heuristica", "manhattan")
    k = k or prueba.get("k", 2)
    problema = problema or crear_problema(escenario, **opciones_problema)
    if algoritmo == "BFS":
        return bfs(problema)
    if algoritmo == "DFS":
        return dfs(problema)
    if algoritmo == "UCS":
        return costo_uniforme(problema)
    h = crear_heuristica(heuristica, problema)
    if algoritmo == "A_ESTRELLA":
        resultado = a_estrella(problema, h)
    elif algoritmo == "BEAM":
        resultado = beam_search(problema, h, k)
    else:
        raise ValueError(f"Algoritmo desconocido '{algoritmo}'. Válidos: {', '.join(ALGORITMOS)}")
    resultado.extra["heuristica"] = heuristica
    return resultado
