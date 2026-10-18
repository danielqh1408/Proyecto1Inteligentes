"""Spec 002 §3.4: problemas de búsqueda."""

from tacticalgrid.busqueda.problema import ProblemaMision, ProblemaNavegacion
from tacticalgrid.escenario.cargador import cargar_escenario


def test_navegacion_sucesores(datos_ejemplo):
    e = cargar_escenario(datos_ejemplo)
    p = ProblemaNavegacion(e, (0, 1), (3, 2))
    assert p.sucesores((0, 1)) == [((0, 2), 2), ((0, 0), 1)]  # pasto 2, camino 1
    assert ProblemaNavegacion(e, (0, 1), (3, 2), bloqueadas=[(0, 2)]).sucesores((0, 1)) == [((0, 0), 1)]


def test_mision_estado_compuesto(datos_ejemplo):
    e = cargar_escenario(datos_ejemplo)
    p = ProblemaMision(e, "B1")
    assert p.inicio == ((3, 2), False) and p.objetivo == ((3, 3), True)
    assert (((2, 2), True), 7) in p.sucesores(((3, 2), False))  # al entrar al recurso pasa a llevarlo
    assert (((3, 3), False), 1) in p.sucesores(((3, 2), False))  # en la base sin recurso: no es objetivo
