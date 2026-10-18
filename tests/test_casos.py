"""Spec 008: los casos mínimos del enunciado cumplen lo esperado."""

import pytest

from tacticalgrid.experimentos.casos import CASOS


@pytest.mark.parametrize("nombre", CASOS)
def test_caso(nombre):
    ok, filas = CASOS[nombre]()
    assert ok, filas
