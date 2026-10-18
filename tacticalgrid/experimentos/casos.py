"""Casos mínimos del enunciado (spec 008): cada función carga su JSON, ejecuta y compara
lo esperado con lo obtenido. Las usan tanto ``tests/test_casos.py`` como el reporte de resultados.

Cada función devuelve (ok, filas): ``ok`` dice si se cumplió lo esperado y ``filas`` son las
métricas obtenidas (una por ejecución) para mostrarlas en tablas.
"""

from __future__ import annotations

from pathlib import Path

from tacticalgrid.adversarial.minimax import alfa_beta, minimax, voraz
from tacticalgrid.busqueda.ejecutar import ejecutar_busqueda
from tacticalgrid.escenario.cargador import cargar_escenario
from tacticalgrid.juego.estado import estado_inicial

CARPETA = Path(__file__).resolve().parents[2] / "escenarios" / "casos"


def cargar(nombre: str):
    return cargar_escenario(CARPETA / f"{nombre}.json")


def caso01():
    e = cargar("caso01_bfs_vs_dfs")
    bfs, dfs = ejecutar_busqueda(e, "BFS"), ejecutar_busqueda(e, "DFS")
    ok = bfs.exito and dfs.exito and bfs.orden_expansion != dfs.orden_expansion and bfs.longitud <= dfs.longitud
    return ok, [bfs.como_dict(), dfs.como_dict()]


def caso02():
    e = cargar("caso02_ruta_corta_vs_economica")
    bfs, ucs = ejecutar_busqueda(e, "BFS"), ejecutar_busqueda(e, "UCS")
    ok = bfs.longitud < ucs.longitud and ucs.costo < bfs.costo
    return ok, [bfs.como_dict(), ucs.como_dict()]


def caso03():
    e = cargar("caso03_obstaculo_heuristica")
    ucs = ejecutar_busqueda(e, "UCS")
    h1 = ejecutar_busqueda(e, "A_ESTRELLA", "manhattan")
    h2 = ejecutar_busqueda(e, "A_ESTRELLA", "obstaculos")
    ok = h1.costo == h2.costo == ucs.costo and h2.estados_expandidos < h1.estados_expandidos
    return ok, [ucs.como_dict(), h1.como_dict(), h2.como_dict()]


def caso04():
    e = cargar("caso04_comparacion_heuristicas")
    ucs = ejecutar_busqueda(e, "UCS")
    h1 = ejecutar_busqueda(e, "A_ESTRELLA", "manhattan")
    h2 = ejecutar_busqueda(e, "A_ESTRELLA", "obstaculos")
    ok = h1.costo == h2.costo == ucs.costo and h2.estados_expandidos <= h1.estados_expandidos
    return ok, [ucs.como_dict(), h1.como_dict(), h2.como_dict()]


def caso05():
    e = cargar("caso05_beam")
    resultados = [ejecutar_busqueda(e, "BEAM", "manhattan", k) for k in (1, 2, 4, 8)]
    expandidos = [r.estados_expandidos for r in resultados]
    ok = not resultados[0].exito and resultados[-1].exito and len(set(expandidos)) == len(expandidos)
    return ok, [r.como_dict() for r in resultados]


def caso06():
    e = cargar("caso06_estado_compuesto")
    r = ejecutar_busqueda(e, "UCS")  # la prueba del JSON pide la misión
    celdas = [pos for pos, _ in r.camino]
    repetidas = {pos for pos in celdas if celdas.count(pos) > 1}
    ok = r.exito and bool(repetidas) and all(((pos, False) in r.camino and (pos, True) in r.camino) for pos in repetidas)
    return ok, [r.como_dict()]


CASOS = {
    "caso01": caso01,
    "caso02": caso02,
    "caso03": caso03,
    "caso04": caso04,
    "caso05": caso05,
    "caso06": caso06,
}


# ---------------------------------------------------------------- casos adversariales (spec 005)

def _decision(d):
    fila = d.como_dict()
    fila.pop("valores_raiz")
    fila.pop("desglose", None)
    return fila


def caso07():
    e = cargar("caso07_decision_adversarial")
    s = estado_inicial(e)
    mm, vz = alfa_beta(e, s), voraz(e, s)  # profundidad del JSON (4)
    return mm.accion != vz.accion, [_decision(mm), _decision(vz)]


def caso08():
    e = cargar("caso08_minimax_vs_alfabeta")
    s = estado_inicial(e)
    mm, ab = minimax(e, s), alfa_beta(e, s)
    ok = mm.accion == ab.accion and mm.valor == ab.valor and ab.nodos_evaluados < mm.nodos_evaluados
    return ok, [_decision(mm), _decision(ab)]


def caso09():
    e = cargar("caso09_orden_acciones")
    s = estado_inicial(e)
    decisiones = [alfa_beta(e, s, orden=o) for o in ("natural", "inverso", "heuristico")]
    ok = len({d.valor for d in decisiones}) == 1 and len({d.nodos_podados for d in decisiones}) > 1
    return ok, [_decision(d) for d in decisiones]


def caso10():
    e = cargar("caso10_profundidad")
    s = estado_inicial(e)
    decisiones = [alfa_beta(e, s, p) for p in (1, 2, 3, 4, 5)]
    evaluados = [d.nodos_evaluados for d in decisiones]
    ok = evaluados == sorted(evaluados) and len(set(evaluados)) == len(evaluados)
    return ok, [_decision(d) for d in decisiones]


CASOS.update({"caso07": caso07, "caso08": caso08, "caso09": caso09, "caso10": caso10})
