"""Heurísticas para A* y Beam (spec 004). Todas reciben una celda (fila, columna).

c_min = menor costo de terreno transitable del mapa cargado (sale del JSON, no es constante).
Multiplicar por c_min mantiene la admisibilidad aunque algún terreno cueste menos de 1.
"""

from __future__ import annotations

import math
from collections import deque

from tacticalgrid.busqueda.problema import ProblemaMision


def manhattan(escenario, objetivo):
    """H1: h(n) = c_min · (|f - f_obj| + |c - c_obj|).

    Purpose: estimar el costo restante si no hubiera muros y todo costara c_min.
    Preconditions: ``objetivo`` es una celda del mapa.
    Postconditions: admisible y consistente: cualquier camino necesita >= Manhattan pasos de costo >= c_min.
    Complexity: O(1) por evaluación.
    AI usage: Yes
    AI intervention: Claude Code agregó el factor c_min a la Manhattan del notebook.
    Student validation: pruebas test_admisible_consistente_y_dominancia (mapas con costo 0,5) y casos 3 y 4, en verde.
        Revisado por Daniel Quintero (20 oct: código, pytest y GUI; ver docs/USO_IA.md)
        y por Juan Ocampo antes de la sustentación.
    """
    c_min = escenario.costo_minimo()
    return lambda p: c_min * (abs(p[0] - objetivo[0]) + abs(p[1] - objetivo[1]))


def obstaculos(escenario, objetivo):
    """H2 (propia): h(n) = c_min · (pasos BFS desde n hasta el objetivo esquivando muros).

    Purpose: estimar el costo restante en un mapa relajado que SÍ respeta los muros pero donde
        todo terreno transitable cuesta c_min.
    Preconditions: ``objetivo`` es una celda del mapa.
    Postconditions: admisible (todo camino real tiene >= pasos_BFS pasos de costo >= c_min),
        consistente (pasos_BFS de dos vecinos difiere en <= 1) y domina a H1 (pasos_BFS >= Manhattan).
        Devuelve inf en celdas que no pueden llegar al objetivo.
    Complexity: O(F·C) una sola vez (BFS desde el objetivo) y O(1) por evaluación; O(F·C) memoria.
    AI usage: Yes
    AI intervention: Claude Code propuso la heurística y escribió el BFS inverso.
    Student validation: pruebas test_admisible_consistente_y_dominancia y caso 3 (177 vs 282 expandidos), en verde.
        Revisado por Daniel Quintero (20 oct: código, pytest y GUI; ver docs/USO_IA.md)
        y por Juan Ocampo antes de la sustentación.
    """
    c_min = escenario.costo_minimo()
    pasos = {objetivo: 0}
    cola = deque([objetivo])
    while cola:
        p = cola.popleft()
        for v in escenario.vecinos(p):
            if v not in pasos:
                pasos[v] = pasos[p] + 1
                cola.append(v)
    return lambda p: c_min * pasos[p] if p in pasos else math.inf


def manhattan_promedio(escenario, objetivo):
    """H3 (solo para experimentar, NO admisible): costo promedio de las celdas transitables · Manhattan."""
    costos = [escenario.costos[t] for fila in escenario.terreno for t in fila if escenario.costos[t] is not None]
    promedio = sum(costos) / len(costos)
    return lambda p: promedio * (abs(p[0] - objetivo[0]) + abs(p[1] - objetivo[1]))


HEURISTICAS = {"manhattan": manhattan, "obstaculos": obstaculos, "manhattan_promedio": manhattan_promedio}


def crear_heuristica(nombre: str, problema):
    """Heurística ``nombre`` lista para usar con los estados de ``problema``.

    Purpose: adaptar las heurísticas de celdas a los dos tipos de problema.
    Preconditions: ``nombre`` es "cero" o una clave de HEURISTICAS.
    Postconditions: navegación: h(celda hacia el objetivo). Misión: si lleva el recurso,
        h(celda -> base); si no, h(celda -> recurso) + h(recurso -> base). Sigue siendo admisible
        porque cualquier camino real debe pasar por el recurso y luego llegar a la base.
    Complexity: la de la heurística elegida (dos precálculos en la misión).
    AI usage: Yes
    AI intervention: Claude Code escribió la función y la versión para la misión.
    Student validation: pruebas test_heuristica_mision y test_todos_resuelven_la_mision, en verde.
        Revisado por Daniel Quintero (20 oct: código, pytest y GUI; ver docs/USO_IA.md)
        y por Juan Ocampo antes de la sustentación.
    """
    if nombre == "cero":
        return lambda s: 0
    base = HEURISTICAS[nombre]
    e = problema.escenario
    if isinstance(problema, ProblemaMision):
        destino = problema.objetivo[0]
        hacia_base = base(e, destino)
        hacia_recurso = base(e, e.recurso)
        resto = hacia_base(e.recurso)
        return lambda s: hacia_base(s[0]) if s[1] else hacia_recurso(s[0]) + resto
    return base(e, problema.objetivo)
