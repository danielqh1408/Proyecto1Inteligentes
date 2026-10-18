"""Spec 006: el verificador acepta las soluciones correctas y detecta las manipuladas."""

from dataclasses import replace

import pytest

from tacticalgrid.adversarial.minimax import alfa_beta
from tacticalgrid.busqueda.ejecutar import ALGORITMOS, crear_problema, ejecutar_busqueda
from tacticalgrid.escenario.cargador import cargar_escenario
from tacticalgrid.experimentos.casos import cargar
from tacticalgrid.juego.estado import Accion, estado_inicial
from tacticalgrid.verificacion.verificador import verificar_camino, verificar_decision, verificar_minimax_vs_alfabeta

CASOS_BUSQUEDA = ["caso01_bfs_vs_dfs", "caso02_ruta_corta_vs_economica", "caso03_obstaculo_heuristica",
                  "caso04_comparacion_heuristicas", "caso05_beam", "caso06_estado_compuesto"]


def todo_ok(chequeos):
    return all(ok for _, ok in chequeos)


@pytest.mark.parametrize("caso", CASOS_BUSQUEDA)
@pytest.mark.parametrize("algoritmo", ALGORITMOS)
def test_todos_los_resultados(caso, algoritmo):  # CA-006-1 (incluye resultados sin éxito, p. ej. Beam k=1)
    e = cargar(caso)
    problema = crear_problema(e)
    for heuristica in ("manhattan", "obstaculos"):
        r = ejecutar_busqueda(e, algoritmo, heuristica, problema=problema)
        assert todo_ok(verificar_camino(e, problema, r)), verificar_camino(e, problema, r)


@pytest.mark.parametrize("manipular, chequeo", [
    (lambda r: replace(r, camino=[r.camino[0], r.camino[2]] + r.camino[2:]), "cada movimiento va a una celda vecina dentro del mapa"),
    (lambda r: replace(r, camino=r.camino[:2] + [(1, 1)] + r.camino[2:]), "ninguna celda es un obstáculo"),
    (lambda r: replace(r, costo=r.costo + 1), "el costo reportado coincide con las transiciones"),
    (lambda r: replace(r, camino=r.camino[:-1]), "el estado final cumple la condición objetivo"),
    (lambda r: replace(r, camino=[(9, 9)] + r.camino), "empieza en el estado inicial"),
    (lambda r: replace(r, exito=False), "sin solución: el camino está vacío"),
])
def test_detecta_manipulaciones(datos_ejemplo, manipular, chequeo):  # CA-006-2
    e = cargar_escenario(datos_ejemplo)
    problema = crear_problema(e)
    r = ejecutar_busqueda(e, "UCS", problema=problema)
    falla = dict(verificar_camino(e, problema, manipular(r)))
    assert falla[chequeo] is False


def test_decision_legal_y_minimax_igual_alfabeta():  # CA-006-4, CA-006-5
    e = cargar("caso07_decision_adversarial")
    s = estado_inicial(e)
    d = alfa_beta(e, s, 3)
    assert todo_ok(verificar_decision(e, s, d))
    assert todo_ok(verificar_minimax_vs_alfabeta(e, s, 3))


def test_decision_ilegal():  # CA-006-4
    e = cargar("caso07_decision_adversarial")
    s = estado_inicial(e)
    d = alfa_beta(e, s, 2)
    d.accion = Accion("MOVER", "B1", (10, 10))  # no es el turno de B
    assert dict(verificar_decision(e, s, d))["la acción elegida es legal"] is False
