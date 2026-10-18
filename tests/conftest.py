"""Utilidades compartidas por las pruebas."""

import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture
def datos_ejemplo() -> dict:
    """JSON del enunciado como dict (una copia nueva por prueba)."""
    return json.loads((RAIZ / "escenarios" / "ejemplo_enunciado.json").read_text(encoding="utf-8"))
