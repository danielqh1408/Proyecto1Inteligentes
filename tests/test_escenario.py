"""Spec 001: carga del escenario (CA-001-1, 4, 5, 6, 7, 8)."""

import copy
import json
from pathlib import Path

import pytest

from tacticalgrid.escenario.cargador import EscenarioInvalido, cargar_escenario

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLO = RAIZ / "escenarios" / "ejemplo_enunciado.json"


def ejemplo() -> dict:
    return json.loads(EJEMPLO.read_text(encoding="utf-8"))


def test_carga_ejemplo_enunciado():  # CA-001-1
    e = cargar_escenario(EJEMPLO)
    assert (e.filas, e.columnas) == (4, 4)
    assert e.costo((2, 2)) == 7  # pantano
    assert not e.transitable((1, 1))  # muro
    assert [u.id for u in e.unidades] == ["A1", "A2", "B1", "B2"]
    assert e.bases == {"A": (0, 0), "B": (3, 3)}
    assert e.recurso == (2, 2) and e.portador is None and e.turno == "A"
    assert e.prueba["modo"] == "busqueda"


def test_carga_atomica():  # CA-001-4
    activo = cargar_escenario(EJEMPLO)
    datos = ejemplo()
    datos["turno"] = "X"
    with pytest.raises(EscenarioInvalido):
        activo = cargar_escenario(datos)
    assert activo.turno == "A"  # la asignación nunca ocurrió: el escenario anterior sigue intacto


def test_costos_desde_json():  # CA-001-5
    datos = ejemplo()
    datos["tipos_terreno"]["pantano"]["costo"] = 15
    assert cargar_escenario(datos).costo((2, 2)) == 15


def test_campos_extra():  # CA-001-6
    datos = ejemplo()
    datos["autor"] = "profesor"
    datos["juego"]["max_turnos"] = 50
    datos["prueba"]["algoritmo"] = "UCS"
    e = cargar_escenario(datos)
    assert e.juego["max_turnos"] == 50 and e.prueba["algoritmo"] == "UCS"


def test_bando_minuscula():  # CA-001-7 (D-01)
    datos = ejemplo()
    datos["unidades"][0]["bando"] = "a"
    datos["turno"] = "b"
    e = cargar_escenario(datos)
    assert e.unidades[0].bando == "A" and e.turno == "B"


def test_no_cuadrado():  # CA-001-8
    datos = ejemplo()
    datos["mapa"] = {"filas": 4, "columnas": 6}
    for fila in datos["terreno"]:
        fila += ["camino", "camino"]
    e = cargar_escenario(datos)
    assert e.dentro((3, 5)) and not e.dentro((5, 3))


def test_vecinos_orden():
    e = cargar_escenario(EJEMPLO)
    assert e.vecinos((0, 1)) == [(0, 2), (0, 0)]  # abajo es muro; orden abajo, arriba, derecha, izquierda
    assert e.vecinos((0, 1), orden=("izquierda", "derecha")) == [(0, 0), (0, 2)]


def test_costo_minimo():
    datos = copy.deepcopy(ejemplo())
    datos["tipos_terreno"]["hielo"] = {"costo": 0.5, "transitable": True}  # en el catálogo, pero no en el mapa
    assert cargar_escenario(datos).costo_minimo() == 1


def test_json_mal_formado(tmp_path):
    ruta = tmp_path / "roto.json"
    ruta.write_text('{"version": "1.0", ', encoding="utf-8")
    with pytest.raises(EscenarioInvalido, match="JSON mal formado"):
        cargar_escenario(ruta)
