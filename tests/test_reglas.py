"""Spec 002: estado, acciones y reglas (CA-002-1 … CA-002-9).

Mapa del enunciado (4x4):      A1=(0,1) A2=(1,0) B1=(3,2) B2=(2,3)
    camino camino pasto  pasto      Base A=(0,0)  Base B=(3,3)  Recurso=(2,2)
    camino MURO   bosque pasto
    camino camino PANTANO pasto
    pasto  pasto  camino camino
"""

import random

from tacticalgrid.busqueda.problema import ProblemaMision
from tacticalgrid.escenario.cargador import cargar_escenario
from tacticalgrid.juego.estado import Accion, EstadoJuego, estado_inicial
from tacticalgrid.juego.reglas import acciones_legales, aplicar, es_terminal, ganador, validar_estado


def destinos(acciones, unidad):
    return [a.destino for a in acciones if a.unidad == unidad and a.tipo == "MOVER"]


def test_estado_inicial(datos_ejemplo):  # CA-002-1
    e = cargar_escenario(datos_ejemplo)
    s = estado_inicial(e)
    assert s == EstadoJuego(((0, 1), (1, 0), (3, 2), (2, 3)), None, (2, 2), "A", 0)


def test_portador_desde_json(datos_ejemplo):  # D-03
    datos_ejemplo["juego"]["portador_recurso"] = "B1"
    s = estado_inicial(cargar_escenario(datos_ejemplo))
    assert s.portador == "B1" and s.recurso is None


def test_estado_compuesto(datos_ejemplo):  # CA-002-2 (caso 6)
    e = cargar_escenario(datos_ejemplo)
    mision = ProblemaMision(e, "B1")
    assert ((2, 2), False) != ((2, 2), True)
    assert not mision.es_objetivo(((3, 3), False)) and mision.es_objetivo(((3, 3), True))
    # Misma posición física de B1 en su base: con el recurso gana, sin él no.
    con = EstadoJuego(((0, 1), (1, 0), (3, 3), (2, 3)), "B1", None, "A")
    sin = EstadoJuego(((0, 1), (1, 0), (3, 3), (2, 3)), None, (2, 2), "A")
    assert ganador(e, con) == "B" and ganador(e, sin) is None


def test_mover_restricciones(datos_ejemplo):  # CA-002-3
    e = cargar_escenario(datos_ejemplo)
    acciones = acciones_legales(e, estado_inicial(e))
    assert destinos(acciones, "A1") == [(0, 2), (0, 0)]  # (1,1) es muro; puede entrar a su propia base
    assert destinos(acciones, "A2") == [(2, 0), (0, 0)]
    assert all(a.unidad in ("A1", "A2") for a in acciones)  # solo actúa el bando en turno
    # A1 junto a la base B: no puede entrar (R3)
    s = EstadoJuego(((3, 2), (1, 0), (0, 2), (0, 3)), None, (2, 2), "A")
    assert (3, 3) not in destinos(acciones_legales(e, s), "A1")
    # Celda ocupada: B1 no puede entrar donde está B2
    s = EstadoJuego(((0, 1), (1, 0), (3, 2), (3, 1)), None, (2, 2), "B")
    assert (3, 1) not in destinos(acciones_legales(e, s), "B1")


def test_recoger_y_entregar(datos_ejemplo):  # CA-002-4
    e = cargar_escenario(datos_ejemplo)
    s = estado_inicial(e)
    for accion in [
        Accion("MOVER", "A1", (0, 2)),
        Accion("MOVER", "B1", (2, 2)),  # B1 recoge el recurso
        Accion("MOVER", "A2", (2, 0)),
        Accion("MOVER", "B1", (3, 2)),
        Accion("MOVER", "A2", (2, 1)),
    ]:
        s = aplicar(e, s, accion)
        assert not es_terminal(e, s)
    assert s.portador == "B1" and s.recurso is None and s.turno == "B" and s.turnos_jugados == 5
    s = aplicar(e, s, Accion("MOVER", "B1", (3, 3)))  # entrega en su base
    assert ganador(e, s) == "B" and es_terminal(e, s)


def test_interceptar(datos_ejemplo):  # CA-002-5
    e = cargar_escenario(datos_ejemplo)
    lejos = EstadoJuego(((0, 1), (1, 0), (2, 2), (2, 3)), "B1", None, "A")
    assert Accion("INTERCEPTAR", "A2") not in acciones_legales(e, lejos)
    cerca = EstadoJuego(((0, 1), (2, 1), (2, 2), (2, 3)), "B1", None, "A")
    acciones = acciones_legales(e, cerca)
    assert acciones[acciones.index(Accion("INTERCEPTAR", "A2")) + 1].tipo == "MOVER"  # interceptar va primero
    despues = aplicar(e, cerca, Accion("INTERCEPTAR", "A2"))
    assert despues.portador == "A2" and despues.posiciones == cerca.posiciones
    # No se intercepta a un compañero
    propio = EstadoJuego(((0, 1), (2, 1), (2, 2), (2, 3)), "B1", None, "B")
    assert all(a.tipo != "INTERCEPTAR" for a in acciones_legales(e, propio))


def test_bloqueo_y_empate(datos_ejemplo):  # CA-002-6
    e = cargar_escenario(datos_ejemplo)
    # A1 en (0,0) y A2 en (1,0) rodeados por B1 (0,1), B2 (2,0) y el muro (1,1)
    s = EstadoJuego(((0, 0), (1, 0), (0, 1), (2, 0)), None, (2, 2), "A")
    assert acciones_legales(e, s) == [Accion("PASAR")]
    assert aplicar(e, s, Accion("PASAR")).turno == "B"
    assert es_terminal(e, EstadoJuego(s.posiciones, None, (2, 2), "A", 200))
    assert ganador(e, EstadoJuego(s.posiciones, None, (2, 2), "A", 200)) is None
    datos_ejemplo["juego"]["max_turnos"] = 5
    assert es_terminal(cargar_escenario(datos_ejemplo), EstadoJuego(s.posiciones, None, (2, 2), "A", 5))


def test_accion_ilegal(datos_ejemplo):
    e = cargar_escenario(datos_ejemplo)
    try:
        aplicar(e, estado_inicial(e), Accion("MOVER", "A1", (1, 1)))  # muro
    except ValueError:
        return
    raise AssertionError("debió rechazar la acción")


def test_orden_determinista(datos_ejemplo):  # CA-002-7
    e = cargar_escenario(datos_ejemplo)
    s = estado_inicial(e)
    assert acciones_legales(e, s) == acciones_legales(e, s)
    otro_orden = acciones_legales(e, s, orden=("izquierda", "derecha", "arriba", "abajo"))
    assert destinos(otro_orden, "A1") == [(0, 0), (0, 2)]


def test_invariantes_alcanzables(datos_ejemplo):  # CA-002-8 (prueba de propiedad)
    e = cargar_escenario(datos_ejemplo)
    azar = random.Random(0)
    for _ in range(300):
        s = estado_inicial(e)
        for _ in range(30):
            if es_terminal(e, s):
                break
            s = aplicar(e, s, azar.choice(acciones_legales(e, s)))
            assert validar_estado(e, s) == []


def test_simetria_bandos(datos_ejemplo):  # CA-002-9
    e = cargar_escenario(datos_ejemplo)
    espejo = dict(datos_ejemplo)
    espejo["unidades"] = [dict(u, bando="B" if u["bando"] == "A" else "A") for u in datos_ejemplo["unidades"]]
    espejo["bases"] = {"A": datos_ejemplo["bases"]["B"], "B": datos_ejemplo["bases"]["A"]}
    espejo["turno"] = "B"
    e2 = cargar_escenario(espejo)
    assert acciones_legales(e, estado_inicial(e)) == acciones_legales(e2, estado_inicial(e2))


def test_validar_estado_detecta_errores(datos_ejemplo):
    e = cargar_escenario(datos_ejemplo)
    malo = EstadoJuego(((1, 1), (1, 1), (3, 2), (2, 3)), "B1", (2, 2), "C")
    assert len(validar_estado(e, malo)) == 5  # 2 unidades en el muro, celda repetida, recurso doble, turno
