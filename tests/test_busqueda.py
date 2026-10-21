"""Specs 003 y 004: BFS, DFS, UCS, A*, Beam y heurísticas."""

import random

import pytest

from tacticalgrid.busqueda.algoritmos import a_estrella, beam_search, bfs, costo_uniforme, dfs
from tacticalgrid.busqueda.ejecutar import ejecutar_busqueda
from tacticalgrid.busqueda.heuristicas import crear_heuristica, manhattan, obstaculos
from tacticalgrid.busqueda.problema import ProblemaMision, ProblemaNavegacion
from tacticalgrid.escenario.cargador import cargar_escenario


def mapa_aleatorio(semilla: int, n: int = 12) -> dict:
    """Escenario n x n con costos y muros aleatorios (para comparar contra una referencia)."""
    azar = random.Random(semilla)
    tipos = {"t1": {"costo": 1, "transitable": True}, "t2": {"costo": 3, "transitable": True},
             "t3": {"costo": 0.5, "transitable": True}, "muro": {"transitable": False}}
    terreno = [[azar.choice(["t1", "t1", "t2", "t3", "muro"]) for _ in range(n)] for _ in range(n)]
    terreno[0][0] = terreno[n - 1][n - 1] = "t1"
    return {"version": "1.0", "mapa": {"filas": n, "columnas": n}, "tipos_terreno": tipos, "terreno": terreno,
            "bases": {"A": {"fila": 0, "columna": 0}, "B": {"fila": n - 1, "columna": n - 1}},
            "recurso": {"fila": 0, "columna": 0},
            "unidades": [{"id": "A1", "bando": "A", "tipo": "estandar", "fila": 0, "columna": 0}],
            "turno": "A", "juego": {"portador_recurso": None}}


def dijkstra_referencia(e, inicio, objetivo):
    """Dijkstra escrito aparte, sin compartir código con los algoritmos (oráculo)."""
    distancia, pendientes = {inicio: 0}, {inicio}
    while pendientes:
        s = min(pendientes, key=distancia.get)
        pendientes.remove(s)
        for v in e.vecinos(s):
            if distancia[s] + e.costo(v) < distancia.get(v, float("inf")):
                distancia[v] = distancia[s] + e.costo(v)
                pendientes.add(v)
    return distancia.get(objetivo)


def test_ejemplo_enunciado(datos_ejemplo):  # CA-003-1, ejercicio a mano de docs/01_LEEME_DANIEL.md
    e = cargar_escenario(datos_ejemplo)
    r_bfs, r_ucs = ejecutar_busqueda(e, "BFS"), ejecutar_busqueda(e, "UCS")
    assert r_bfs.como_dict()["camino"] == [[0, 1], [0, 2], [1, 2], [2, 2], [3, 2]] and r_bfs.costo == 14
    assert r_ucs.longitud == 6 and r_ucs.costo == 7
    datos_ejemplo["tipos_terreno"]["pantano"]["costo"] = 1
    assert ejecutar_busqueda(cargar_escenario(datos_ejemplo), "UCS").costo == 6


@pytest.mark.parametrize("semilla", range(20))
def test_optimos_contra_dijkstra(semilla):  # CA-003-4, CA-004-1
    e = cargar_escenario(mapa_aleatorio(semilla))
    p = ProblemaNavegacion(e, (0, 0), (11, 11))
    esperado = dijkstra_referencia(e, (0, 0), (11, 11))
    for r in (costo_uniforme(p), a_estrella(p, manhattan(e, (11, 11))), a_estrella(p, obstaculos(e, (11, 11)))):
        assert (r.costo if r.exito else None) == esperado
    if esperado is not None:
        assert bfs(p).exito and dfs(p).exito and bfs(p).longitud <= dfs(p).longitud


def test_h_cero_es_ucs(datos_ejemplo):  # CA-004-2
    e = cargar_escenario(datos_ejemplo)
    p = ProblemaNavegacion(e, (0, 1), (3, 2))
    ignorar = {"algoritmo": "", "tiempo_ms": 0, "preparacion_ms": 0, "tiempo_total_ms": 0}
    assert a_estrella(p, lambda s: 0).como_dict() | ignorar == costo_uniforme(p).como_dict() | ignorar


@pytest.mark.parametrize("semilla", range(10))
def test_admisible_consistente_y_dominancia(semilla):  # CA-004-3, CA-004-4, CA-004-8 (hay terreno de costo 0.5)
    e = cargar_escenario(mapa_aleatorio(semilla))
    objetivo = (11, 11)
    h1, h2 = manhattan(e, objetivo), obstaculos(e, objetivo)
    for f in range(e.filas):
        for c in range(e.columnas):
            if not e.transitable((f, c)):
                continue
            assert h1((f, c)) <= h2((f, c))  # dominancia
            real = dijkstra_referencia(e, (f, c), objetivo)
            if real is not None:
                assert h2((f, c)) <= real  # admisible
                for v in e.vecinos((f, c)):
                    assert h2((f, c)) <= e.costo(v) + h2(v) and h1((f, c)) <= e.costo(v) + h1(v)


def test_h3_no_admisible():  # CA-004-9
    e = cargar_escenario("escenarios/casos/caso02_ruta_corta_vs_economica.json")
    assert ejecutar_busqueda(e, "A_ESTRELLA", "manhattan_promedio").costo > ejecutar_busqueda(e, "UCS").costo


def test_sin_ruta(datos_ejemplo):  # CA-003-5
    e = cargar_escenario(datos_ejemplo)
    for r in (bfs(ProblemaNavegacion(e, (0, 1), (1, 1))), costo_uniforme(ProblemaNavegacion(e, (0, 1), (1, 1)))):
        assert not r.exito and r.camino == [] and r.estados_expandidos > 0


def test_inicio_es_objetivo(datos_ejemplo):  # CA-003-6
    e = cargar_escenario(datos_ejemplo)
    r = bfs(ProblemaNavegacion(e, (0, 1), (0, 1)))
    assert r.exito and r.longitud == 0 and r.costo == 0 and r.estados_expandidos == 0


def test_orden_movimientos_dfs():  # CA-003-7
    e = cargar_escenario("escenarios/casos/caso01_bfs_vs_dfs.json")
    otro = ("izquierda", "arriba", "derecha", "abajo")
    assert ejecutar_busqueda(e, "DFS").camino != ejecutar_busqueda(e, "DFS", orden=otro).camino
    assert ejecutar_busqueda(e, "BFS").longitud == ejecutar_busqueda(e, "BFS", orden=otro).longitud


def test_formato_enunciado(datos_ejemplo):  # CA-003-8
    d = ejecutar_busqueda(cargar_escenario(datos_ejemplo), "A_ESTRELLA").como_dict()
    assert {"algoritmo", "exito", "camino", "costo", "estados_generados", "estados_expandidos", "maximo_frontera"} <= d.keys()
    assert d["algoritmo"] == "A_ESTRELLA"


@pytest.mark.parametrize("algoritmo", ["BFS", "DFS", "UCS", "A_ESTRELLA", "BEAM"])
def test_todos_resuelven_la_mision(datos_ejemplo, algoritmo):  # CA-003-9
    r = ejecutar_busqueda(cargar_escenario(datos_ejemplo), algoritmo, k=4, mision=True)
    assert r.exito and r.camino[-1] == ((0, 0), True)


def test_heuristica_mision(datos_ejemplo):
    e = cargar_escenario(datos_ejemplo)
    p = ProblemaMision(e, "A1")
    h = crear_heuristica("manhattan", p)
    assert h(((0, 1), False)) == 3 + 4  # (0,1)->recurso (2,2) = 3; recurso -> base A (0,0) = 4
    assert h(((2, 2), True)) == 4


def test_beam_descartados():
    e = cargar_escenario("escenarios/casos/caso05_beam.json")
    r1, r8 = (ejecutar_busqueda(e, "BEAM", "manhattan", k) for k in (1, 8))
    assert r1.extra["descartados"] > 0 and not r1.exito and r8.exito  # k=1 recorta y se queda sin salida
    assert beam_search(ProblemaNavegacion(e, (10, 1), (10, 1)), lambda s: 0, 1).exito


@pytest.mark.parametrize("nombre", ["A*", "astar", "a_estrella", "A-ESTRELLA"])
def test_alias_de_algoritmos(datos_ejemplo, nombre):  # robustez ante el JSON del profesor
    datos_ejemplo["prueba"]["algoritmo"] = nombre
    assert ejecutar_busqueda(cargar_escenario(datos_ejemplo)).algoritmo == "A_ESTRELLA"


def test_prueba_incompleta_da_error_claro(datos_ejemplo):
    del datos_ejemplo["prueba"]["unidad_inicio"]
    with pytest.raises(ValueError, match="unidad"):
        ejecutar_busqueda(cargar_escenario(datos_ejemplo))
