"""Spec 009: los métodos con lógica relevante tienen la documentación de 7 campos que exige el enunciado.

Esta lista audita la estructura documental. No certifica comprensión ni revisión humana.
El registro de pruebas debe distinguirse de la revisión personal por realizar.
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
    "juego.reglas.costo_accion", "juego.reglas.ganador", "juego.reglas.es_terminal",
    "busqueda.heuristicas.manhattan_promedio", "adversarial.utilidad._costos_hacia",
    "adversarial.utilidad.restante", "adversarial.utilidad.utilidad_terminal",
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
def test_validacion_documentada(metodo):
    assert "test_" in docstring(metodo).split("Student validation:")[1], f"{metodo}: falta identificar evidencia de pruebas"
