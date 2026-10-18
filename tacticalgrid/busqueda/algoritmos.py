"""Algoritmos de búsqueda (specs 003 y 004), con el mismo estilo de los notebooks de clase.

Todos reciben un problema con ``inicio``, ``es_objetivo(s)`` y ``sucesores(s) -> [(s2, costo)]``,
hacen la prueba de objetivo AL SACAR de la frontera (D-13) y devuelven un ``Resultado``.
``padres[s] = (padre, costo de entrar a s)`` sirve a la vez de conjunto de visitados.
"""

from __future__ import annotations

import math
from collections import deque
from heapq import heappop, heappush
from itertools import count
from time import perf_counter

from tacticalgrid.busqueda.resultado import Resultado, reconstruir


def _terminar(r: Resultado, padres: dict, s, t0: float) -> Resultado:
    if s is not None:
        r.exito = True
        r.camino, r.costo = reconstruir(padres, s)
    r.tiempo_ms = (perf_counter() - t0) * 1000
    return r


def _busqueda_ciega(problema, nombre: str, es_dfs: bool) -> Resultado:
    t0 = perf_counter()
    r = Resultado(nombre, estados_generados=1, maximo_frontera=1)
    frontera = deque([problema.inicio])
    padres = {problema.inicio: None}
    while frontera:
        s = frontera.pop() if es_dfs else frontera.popleft()  # pila (LIFO) o cola (FIFO)
        if problema.es_objetivo(s):
            return _terminar(r, padres, s, t0)
        r.estados_expandidos += 1
        r.orden_expansion.append(s)
        for s2, c in problema.sucesores(s):
            if s2 not in padres:
                padres[s2] = (s, c)
                frontera.append(s2)
                r.estados_generados += 1
        r.maximo_frontera = max(r.maximo_frontera, len(frontera))
    return _terminar(r, padres, None, t0)


def bfs(problema) -> Resultado:
    """Búsqueda en anchura con cola FIFO.

    Purpose: encontrar el camino con MENOS MOVIMIENTOS (ignora costos).
    Preconditions: ``problema`` tiene inicio, es_objetivo y sucesores; espacio de estados finito.
    Postconditions: si hay camino, ``exito`` y el camino tiene la menor longitud posible;
        métricas según spec 003 §3; si no hay camino, ``exito`` False y camino vacío.
    Complexity: O(V + E) tiempo y O(V) espacio, V estados y E transiciones (E <= 4V).
    AI usage: Yes
    AI intervention: Claude Code adaptó ``bfs_camino_laberinto`` del notebook: padres en vez de
        copiar caminos, métricas y prueba de objetivo al sacar; comparte código con dfs.
    Student validation: PENDIENTE: revisar test_bfs_ejemplo y el caso 1.
    """
    return _busqueda_ciega(problema, "BFS", es_dfs=False)


def dfs(problema) -> Resultado:
    """Búsqueda en profundidad con pila LIFO (visitados se marcan al apilar, como en clase).

    Purpose: encontrar ALGÚN camino profundizando por ramas.
    Preconditions: las mismas de bfs.
    Postconditions: si hay camino, ``exito``; el camino NO tiene por qué ser el más corto
        y depende del orden de los sucesores.
    Complexity: O(V + E) tiempo y O(V) espacio.
    AI usage: Yes
    AI intervention: Claude Code adaptó ``dfs_camino_laberinto`` del notebook (misma función que bfs).
    Student validation: PENDIENTE: revisar el caso 1 y test_orden_movimientos_dfs.
    """
    return _busqueda_ciega(problema, "DFS", es_dfs=True)


def a_estrella(problema, h, nombre: str = "A_ESTRELLA") -> Resultado:
    """A*: expande primero el estado con menor f(n) = g(n) + h(n).

    Purpose: camino de MENOR COSTO usando una heurística para explorar menos.
    Preconditions: costos > 0; ``h(s)`` admisible para garantizar el óptimo
        (``h = inf`` marca estados que no pueden llegar al objetivo: no se insertan).
    Postconditions: con h admisible y consistente, el costo es el mínimo posible.
        Las entradas viejas del heap (g != mejor_g) se descartan sin contarse como expandidas.
    Complexity: O((V + E) log V) tiempo, O(V) espacio.
    AI usage: Yes
    AI intervention: Claude Code adaptó ``a_estrella`` del notebook (misma tupla (f, g, tie, s)
        y eliminación perezosa), agregando padres, métricas y el corte por h = inf.
    Student validation: PENDIENTE: revisar test_a_estrella_optimo y el caso 3.
    """
    t0 = perf_counter()
    r = Resultado(nombre, estados_generados=1, maximo_frontera=1)
    desempate = count()
    frontera = [(h(problema.inicio), 0, next(desempate), problema.inicio)]
    mejor_g = {problema.inicio: 0}
    padres = {problema.inicio: None}
    while frontera:
        f, g, _, s = heappop(frontera)
        if g != mejor_g[s]:
            continue  # entrada obsoleta: ya se encontró un camino mejor a s
        if problema.es_objetivo(s):
            return _terminar(r, padres, s, t0)
        r.estados_expandidos += 1
        r.orden_expansion.append(s)
        for s2, c in problema.sucesores(s):
            nuevo_g = g + c
            if nuevo_g < mejor_g.get(s2, math.inf):
                h2 = h(s2)
                if h2 == math.inf:
                    continue
                mejor_g[s2] = nuevo_g
                padres[s2] = (s, c)
                heappush(frontera, (nuevo_g + h2, nuevo_g, next(desempate), s2))
                r.estados_generados += 1
        r.maximo_frontera = max(r.maximo_frontera, len(frontera))
    return _terminar(r, padres, None, t0)


def costo_uniforme(problema) -> Resultado:
    """Búsqueda de Costo Uniforme (UCS): expande primero el menor g(n).

    Purpose: camino de MENOR COSTO sin heurística.
    Preconditions: costos > 0 (los garantiza el validador).
    Postconditions: costo mínimo; es exactamente A* con h(n) = 0 (como muestra el notebook,
        "Caso 1 — Sin heurística"), así que comparte código y métricas con a_estrella.
    Complexity: O((V + E) log V) tiempo, O(V) espacio.
    AI usage: Yes
    AI intervention: Claude Code propuso definir UCS como A* con h = 0 para no duplicar código.
    Student validation: PENDIENTE: revisar test_ucs_optimo y el caso 2.
    """
    return a_estrella(problema, lambda s: 0, nombre="UCS")


def beam_search(problema, h, k: int, criterio: str = "h") -> Resultado:
    """Beam Search por niveles: en cada nivel solo se conservan los ``k`` mejores candidatos.

    Purpose: búsqueda con memoria limitada (spec 004); muestra que recortar puede perder caminos.
    Preconditions: k >= 1; ``criterio`` es "h" (como en clase) o "f" (g + h).
    Postconditions: visitados global como en el notebook: lo descartado no se vuelve a generar,
        así que puede fallar aunque exista camino y no garantiza el óptimo.
        ``extra`` incluye k, criterio y ``descartados`` (candidatos eliminados por el recorte).
        ``maximo_frontera`` = mayor número de candidatos de un nivel antes de recortar.
    Complexity: O(d · k · b · log(k·b)) tiempo y O(k · b) memoria por nivel, d = niveles.
    AI usage: Yes
    AI intervention: Claude Code adaptó ``beam_search_mapa`` del notebook (mismo esquema por niveles)
        con métricas, criterio f opcional y orden estable en empates.
    Student validation: PENDIENTE: revisar el caso 5 con k = 1, 2, 4, 8.
    """
    t0 = perf_counter()
    r = Resultado("BEAM", estados_generados=1, maximo_frontera=1, extra={"k": k, "criterio": criterio, "descartados": 0})
    haz = [problema.inicio]
    padres = {problema.inicio: None}
    g = {problema.inicio: 0}
    while haz:
        candidatos = []
        for s in haz:
            if problema.es_objetivo(s):
                return _terminar(r, padres, s, t0)
            r.estados_expandidos += 1
            r.orden_expansion.append(s)
            for s2, c in problema.sucesores(s):
                if s2 not in padres:
                    padres[s2] = (s, c)
                    g[s2] = g[s] + c
                    candidatos.append(s2)
                    r.estados_generados += 1
        r.maximo_frontera = max(r.maximo_frontera, len(candidatos))
        candidatos.sort(key=lambda s: h(s) if criterio == "h" else g[s] + h(s))  # sort estable: empates por orden de generación
        r.extra["descartados"] += max(len(candidatos) - k, 0)
        haz = candidatos[:k]
    return _terminar(r, padres, None, t0)
