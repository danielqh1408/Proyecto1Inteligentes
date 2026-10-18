"""Spec 009: los métodos con lógica relevante tienen la documentación de 7 campos que exige el enunciado.

Esta lista es la fuente de verdad de qué métodos se auditan. `pytest -m entrega` además exige que
"Student validation" ya no diga PENDIENTE (hay que llenarlo a mano antes de entregar).
"""

import importlib

import pytest

CAMPOS = ("Purpose", "Preconditions", "Postconditions", "Complexity", "AI usage", "AI intervention", "Student validation")
METODOS = [
    "escenario.validador.validar", "escenario.cargador.cargar_escenario",
    "escenario.modelo.Escenario.costo", "escenario.modelo.Escenario.vecinos",
    "juego.estado.estado_inicial", "juego.reglas.acciones_legales", "juego.reglas.aplicar", "juego.reglas.validar_estado",
    "busqueda.problema.ProblemaNavegacion.sucesores", "busqueda.problema.ProblemaMision.sucesores",
    "busqueda.algoritmos.bfs", "busqueda.algoritmos.dfs", "busqueda.algoritmos.costo_uniforme",
    "busqueda.algoritmos.a_estrella", "busqueda.algoritmos.beam_search",
    "busqueda.heuristicas.manhattan", "busqueda.heuristicas.obstaculos", "busqueda.heuristicas.crear_heuristica",
    "adversarial.utilidad.distancias", "adversarial.utilidad.evaluar",
    "adversarial.minimax.decidir", "adversarial.minimax.ordenar_acciones",
    "verificacion.verificador.verificar_camino", "verificacion.verificador.verificar_decision",
]


def docstring(ruta: str) -> str:
    partes = ruta.split(".")
    for i in range(len(partes), 0, -1):
        try:
            objeto = importlib.import_module("tacticalgrid." + ".".join(partes[:i]))
        except ModuleNotFoundError:
            continue
        for nombre in partes[i:]:
            objeto = getattr(objeto, nombre)
        return getattr(objeto, "__wrapped__", objeto).__doc__ or ""
    raise ImportError(ruta)


@pytest.mark.parametrize("metodo", METODOS)
def test_siete_campos(metodo):
    doc = docstring(metodo)
    faltan = [c for c in CAMPOS if f"{c}:" not in doc]
    assert not faltan, f"{metodo}: faltan {faltan}"
    assert "AI usage: Yes" in doc or "AI usage: No" in doc


@pytest.mark.entrega
@pytest.mark.parametrize("metodo", METODOS)
def test_validacion_del_estudiante_completa(metodo):
    assert "PENDIENTE" not in docstring(metodo).split("Student validation:")[1], f"{metodo}: falta la validación del estudiante"
