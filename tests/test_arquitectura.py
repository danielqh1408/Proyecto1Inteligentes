"""Constitución P2 / CA-007-5: cada capa solo importa capas inferiores (nunca la interfaz)."""

import ast
from pathlib import Path

import pytest

PAQUETE = Path(__file__).resolve().parent.parent / "tacticalgrid"
# Orden de las capas: un módulo solo puede importar módulos de su misma capa o de capas anteriores.
CAPAS = ["config", "escenario", "juego", "busqueda", "adversarial", "verificacion", "experimentos", "interfaz", "__main__"]


def capa(nombre: str) -> int:
    partes = nombre.split(".")
    return CAPAS.index(partes[1]) if len(partes) > 1 and partes[1] in CAPAS else -1


@pytest.mark.parametrize("archivo", sorted(PAQUETE.rglob("*.py")), ids=lambda p: str(p.relative_to(PAQUETE)))
def test_dependencias_hacia_abajo(archivo):
    modulo = "tacticalgrid." + ".".join(archivo.relative_to(PAQUETE).with_suffix("").parts).replace(".__init__", "")
    propia = capa(modulo)
    if propia == -1:
        return  # tacticalgrid/__init__.py
    for nodo in ast.walk(ast.parse(archivo.read_text(encoding="utf-8"))):
        if isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.module.startswith("tacticalgrid."):
            assert capa(nodo.module) <= propia, f"{modulo} no debe importar {nodo.module} (capa superior)"
