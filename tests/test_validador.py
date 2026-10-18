"""Spec 001: validación (CA-001-2, CA-001-3). Cada archivo de escenarios/invalidos/ declara sus errores esperados."""

import json
from pathlib import Path

import pytest

from tacticalgrid.escenario.validador import validar

RAIZ = Path(__file__).resolve().parent.parent
INVALIDOS = sorted((RAIZ / "escenarios" / "invalidos").glob("*.json"))


def test_ejemplo_es_valido():
    datos = json.loads((RAIZ / "escenarios" / "ejemplo_enunciado.json").read_text(encoding="utf-8"))
    assert validar(datos) == []


@pytest.mark.parametrize("ruta", INVALIDOS, ids=lambda r: r.stem)
def test_cada_regla(ruta):  # CA-001-2 y CA-001-3 (varios_errores.json)
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    errores = validar(datos)
    codigos = [mensaje.split("]")[0].strip("[") for mensaje in errores]
    assert sorted(codigos) == sorted(datos["errores_esperados"]), errores


@pytest.mark.parametrize("datos", [None, [], "texto", 42])
def test_raiz_no_es_objeto(datos):
    assert validar(datos)[0].startswith("[E00]")


def test_campos_faltantes():
    errores = validar({"version": "1.0"})
    assert len(errores) == 8 and all(e.startswith("[E00]") for e in errores)


def test_tipos_incorrectos_no_lanzan_excepcion():
    datos = {
        "version": "1.0",
        "mapa": {"filas": 2, "columnas": 2},
        "tipos_terreno": {"camino": {"costo": True, "transitable": "si"}},
        "terreno": [["camino", ["x"]], [None, "camino"]],
        "bases": "A",
        "recurso": [0, 0],
        "unidades": [7, {"id": ["A1"], "bando": None, "fila": "0", "columna": 0}],
        "turno": None,
        "juego": {"portador_recurso": ["A1"]},
    }
    assert validar(datos)  # reporta errores sin romperse
