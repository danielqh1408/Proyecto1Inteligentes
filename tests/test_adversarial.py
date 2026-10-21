"""Spec 005: utilidad, Minimax, alfa-beta y modo partida."""

import random


import pytest

from tacticalgrid.adversarial.minimax import alfa_beta, minimax
from tacticalgrid.adversarial.partida import jugar
from tacticalgrid.adversarial.utilidad import distancias, evaluar, utilidad_terminal
from tacticalgrid.config import PESOS_UTILIDAD
from tacticalgrid.escenario.cargador import cargar_escenario
from tacticalgrid.experimentos.casos import cargar
from tacticalgrid.juego.estado import Accion, EstadoJuego, estado_inicial
from tacticalgrid.juego.reglas import acciones_legales, aplicar, es_terminal, ganador


def estados_alcanzables(e, cantidad, jugadas, semilla=0):
    azar, estados = random.Random(semilla), []
    for _ in range(cantidad):
        s = estado_inicial(e)
        for _ in range(azar.randrange(jugadas)):
            if es_terminal(e, s):
                break
            s = aplicar(e, s, azar.choice(acciones_legales(e, s)))
        if not es_terminal(e, s):
            estados.append(s)
    return estados


@pytest.mark.parametrize("orden", ["natural", "inverso", "heuristico"])
def test_minimax_igual_alfabeta(datos_ejemplo, orden):  # CA-005-1
    e = cargar_escenario(datos_ejemplo)
    for s in estados_alcanzables(e, 25, 12):
        for p in (1, 2, 3):
            mm, ab = minimax(e, s, p, orden), alfa_beta(e, s, p, orden)
            assert (mm.accion, mm.valor) == (ab.accion, ab.valor)
            assert ab.nodos_evaluados <= mm.nodos_evaluados and mm.nodos_podados == 0


def test_suma_cero():  # CA-005-5
    e = cargar("caso08_minimax_vs_alfabeta")
    for s in estados_alcanzables(e, 30, 20) + estados_alcanzables(cargar("caso07_decision_adversarial"), 1, 1):
        assert evaluar(e, s, "A")[0] == -evaluar(e, s, "B")[0]


def test_preferencia_victoria_rapida(datos_ejemplo):  # CA-005-6
    e = cargar_escenario(datos_ejemplo)
    gana_b = EstadoJuego(((0, 1), (1, 0), (3, 3), (2, 3)), "B1", None, "A")
    assert utilidad_terminal(e, gana_b, "B", 1) > utilidad_terminal(e, gana_b, "B", 3) > 0
    assert utilidad_terminal(e, gana_b, "A", 1) < utilidad_terminal(e, gana_b, "A", 3) < 0


def test_recoger_mejora_en_ejemplo(datos_ejemplo):
    e = cargar_escenario(datos_ejemplo)
    junto = EstadoJuego(((0, 1), (1, 0), (3, 2), (2, 3)), None, (2, 2), "B")
    recogido = aplicar(e, junto, Accion("MOVER", "B1", (2, 2)))
    assert evaluar(e, recogido, "B")[0] > evaluar(e, junto, "B")[0]


def test_toma_la_victoria_inmediata(datos_ejemplo):
    e = cargar_escenario(datos_ejemplo)
    s = EstadoJuego(((0, 1), (1, 0), (3, 2), (2, 0)), "B1", None, "B")
    assert alfa_beta(e, s, 3).accion == Accion("MOVER", "B1", (3, 3))


def test_pesos_desde_json(datos_ejemplo):  # CA-005-7
    e = cargar_escenario(datos_ejemplo)
    s = estado_inicial(e)
    datos_ejemplo["juego"]["pesos_utilidad"] = {"carrera": 0, "movilidad": 0}
    e2 = cargar_escenario(datos_ejemplo)
    assert alfa_beta(e, s, 2).valor != alfa_beta(e2, s, 2).valor  # solo cuenta la posesión (B1 recoge en 2 jugadas)
    assert alfa_beta(e2, s, 2).valor == -PESOS_UTILIDAD["posesion"]


def test_acciones_legales_en_arbol():  # CA-005-8: aplicar() rechaza cualquier acción ilegal
    e = cargar("caso07_decision_adversarial")
    d = alfa_beta(e, estado_inicial(e), 3)
    assert d.accion in acciones_legales(e, estado_inicial(e))
    assert all(a in acciones_legales(e, estado_inicial(e)) for a, _ in d.valores_raiz)


def test_profundidad_desde_json(datos_ejemplo):  # CA-005-9
    e = cargar_escenario(datos_ejemplo)  # profundidad_maxima_minimax = 4 en el ejemplo
    assert alfa_beta(e, estado_inicial(e)).extra["profundidad"] == 4
    assert alfa_beta(e, estado_inicial(e), 2).extra["profundidad"] == 2


def test_distancias(datos_ejemplo):
    d = distancias(cargar_escenario(datos_ejemplo))
    assert d["base_A"][(0, 1)] == 1 and d["recurso_B"][(3, 2)] == 7  # entrar al pantano cuesta 7


def test_partida_termina(datos_ejemplo):
    e = cargar_escenario(datos_ejemplo)
    final, historial = jugar(e, {"A": "ALFA_BETA", "B": "VORAZ"}, {"A": 2})
    assert es_terminal(e, final) and len(historial) == final.turnos_jugados


def test_mas_profundidad_gana_en_mapa_simetrico():  # E6: resultado observado en este mapa, no garantía general
    e = cargar_escenario("escenarios/partida_simetrica.json")
    for agentes, profundidades, gana in (({"A": "ALFA_BETA", "B": "VORAZ"}, {"A": 3}, "A"),
                                         ({"A": "VORAZ", "B": "ALFA_BETA"}, {"B": 3}, "B")):
        final, historial = jugar(e, agentes, profundidades)
        assert final.turnos_jugados < 200 and sum("intercepta" in a for _, _, a, _ in historial) < 5

        assert ganador(e, final) == gana


def test_alias_y_profundidad_en_prueba(datos_ejemplo):  # robustez ante el JSON del profesor
    from tacticalgrid.adversarial.partida import decidir_con
    datos_ejemplo["prueba"] = {"modo": "adversarial", "algoritmo": "alfabeta", "profundidad": 2}
    e = cargar_escenario(datos_ejemplo)
    d = decidir_con(e.prueba["algoritmo"], e, estado_inicial(e))
    assert d.algoritmo == "ALFA_BETA" and d.extra["profundidad"] == 2
