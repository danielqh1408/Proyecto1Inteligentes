"""Regresiones de los contraejemplos encontrados en la revisión previa a sustentar."""

from dataclasses import replace
import importlib

import pytest

from tacticalgrid.adversarial.minimax import alfa_beta, minimax
from tacticalgrid.adversarial.utilidad import distancias, evaluar, utilidad_terminal
from tacticalgrid.busqueda.algoritmos import beam_search
from tacticalgrid.busqueda.ejecutar import crear_problema, ejecutar_busqueda
from tacticalgrid.escenario.cargador import cargar_escenario, EscenarioInvalido
from tacticalgrid.juego.estado import Accion, EstadoJuego, estado_inicial
from tacticalgrid.juego.reglas import acciones_legales, aplicar, costo_accion, validar_estado
from tacticalgrid.verificacion.verificador import verificar_camino, verificar_decision


def test_prefiere_ganar_con_costos_altos(datos_ejemplo):
    for terreno in datos_ejemplo['tipos_terreno'].values():
        if terreno['transitable']:
            terreno['costo'] *= 1000
    datos_ejemplo['juego']['portador_recurso'] = 'B1'
    datos_ejemplo['turno'] = 'B'
    e = cargar_escenario(datos_ejemplo)
    s = estado_inicial(e)
    for algoritmo in (minimax, alfa_beta):
        d = algoritmo(e, s, 1)
        assert d.accion == Accion('MOVER', 'B1', (3, 3))
        assert d.valor > max(evaluar(e, aplicar(e, s, a), 'B')[0] for a in acciones_legales(e, s))


def test_victoria_domina_incluso_con_horizonte_largo(datos_ejemplo):
    datos_ejemplo['juego']['max_turnos'] = 20000
    e = cargar_escenario(datos_ejemplo)
    s = replace(estado_inicial(e), portador='B1', recurso=None,
                posiciones=((0, 1), (1, 0), (3, 3), (2, 3)))
    assert utilidad_terminal(e, s, 'B', 20000) > 9999
    assert utilidad_terminal(e, s, 'A', 20000) < -9999


@pytest.mark.parametrize('campo', ['recurso', 'base_A'])
def test_destino_en_muro_no_rompe_decision(datos_ejemplo, campo):
    if campo == 'recurso':
        datos_ejemplo['recurso'] = {'fila': 1, 'columna': 1}
    else:
        datos_ejemplo['bases']['A'] = {'fila': 1, 'columna': 1}
    e = cargar_escenario(datos_ejemplo)
    s = estado_inicial(e)
    assert alfa_beta(e, s, 2).accion in acciones_legales(e, s)
    assert distancias(e)['recurso_A' if campo == 'recurso' else 'base_A'] == {}


@pytest.mark.parametrize('algoritmo', [minimax, alfa_beta])
def test_raiz_terminal_no_propone_jugada(datos_ejemplo, algoritmo):
    e = cargar_escenario(datos_ejemplo)
    s = replace(estado_inicial(e), portador='B1', recurso=None,
                posiciones=((0, 1), (1, 0), (3, 3), (2, 3)))
    d = algoritmo(e, s, 3)
    assert d.accion is None and d.valores_raiz == []
    assert acciones_legales(e, s) == []
    assert all(ok for _, ok in verificar_decision(e, s, d))
    with pytest.raises(ValueError):
        aplicar(e, s, Accion('MOVER', 'A1', (0, 2)))


@pytest.mark.parametrize('cambio', [dict(recurso=(99, 99)), dict(recurso=(0, 0)),
                                  dict(turnos_jugados=-1), dict(turnos_jugados=True)])
def test_invariantes_faltantes(datos_ejemplo, cambio):
    e = cargar_escenario(datos_ejemplo)
    assert validar_estado(e, replace(estado_inicial(e), **cambio))


def test_mision_no_duplica_recurso(datos_ejemplo):
    datos_ejemplo['juego']['portador_recurso'] = 'B1'
    e = cargar_escenario(datos_ejemplo)
    with pytest.raises(ValueError, match='portador'):
        crear_problema(e, unidad='A1', mision=True)
    assert ejecutar_busqueda(e, 'UCS', unidad='B1', mision=True).exito


@pytest.mark.parametrize('prueba', [[], 'busqueda', {'objetivo': {'fila': 2}},
    {'objetivo': {'fila': 99, 'columna': 0}}, {'k': 0}, {'k': -1}, {'k': True},
    {'profundidad': -1}, {'unidad_inicio': 'inexistente'}, {'unidades_bloquean': 'false'},
    {'orden_movimientos': ['arriba']}, {'modo': 'desconocido'}])
def test_prueba_invalida_se_rechaza_al_cargar(datos_ejemplo, prueba):
    datos_ejemplo['prueba'] = prueba
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(datos_ejemplo)


@pytest.mark.parametrize('juego', [{'profundidad_maxima_minimax': 0}, {'max_turnos': -1},
    {'pesos_utilidad': []}, {'pesos_utilidad': {'posesion': float('inf')}},
    {'orden_acciones': 'desconocido'}])
def test_configuracion_juego_invalida(datos_ejemplo, juego):
    datos_ejemplo['juego'].update(juego)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(datos_ejemplo)


@pytest.mark.parametrize('valor', [0, -1, True, 1.5])
def test_parametros_directos_invalidos(datos_ejemplo, valor):
    e = cargar_escenario(datos_ejemplo)
    with pytest.raises(ValueError):
        alfa_beta(e, estado_inicial(e), valor)
    with pytest.raises(ValueError):
        beam_search(crear_problema(e), lambda s: 0, valor)


def test_metricas_incluyen_trabajo_auxiliar(monkeypatch):
    m = importlib.import_module('tacticalgrid.adversarial.minimax')
    original_evaluar, original_aplicar = m.evaluar, m.aplicar
    llamadas = {'evaluar': 0, 'aplicar': 0}
    def evaluar_contado(*args, **kwargs):
        llamadas['evaluar'] += 1
        return original_evaluar(*args, **kwargs)
    def aplicar_contado(*args, **kwargs):
        llamadas['aplicar'] += 1
        return original_aplicar(*args, **kwargs)
    monkeypatch.setattr(m, 'evaluar', evaluar_contado)
    monkeypatch.setattr(m, 'aplicar', aplicar_contado)
    e = cargar_escenario('escenarios/casos/caso09_orden_acciones.json')
    d = m.alfa_beta(e, estado_inicial(e), 2, 'heuristico').como_dict()
    assert d['evaluaciones_totales'] == llamadas['evaluar']
    assert d['nodos_generados_totales'] == llamadas['aplicar'] + 1
    assert d['evaluaciones_ordenamiento'] > 0


def test_camino_exitoso_vacio_se_rechaza(datos_ejemplo):
    e = cargar_escenario(datos_ejemplo)
    p = crear_problema(e)
    r = ejecutar_busqueda(e, 'UCS', problema=p)
    assert not all(ok for _, ok in verificar_camino(e, p, replace(r, camino=[])))


def test_tiempo_total_incluye_preparacion(datos_ejemplo):
    e = cargar_escenario(datos_ejemplo)
    r = ejecutar_busqueda(e, 'A_ESTRELLA', 'obstaculos')
    assert r.preparacion_ms > 0
    assert r.como_dict()['tiempo_total_ms'] == round(r.tiempo_ms + r.preparacion_ms, 3)


def test_recoger_no_es_garantia_monotona(datos_ejemplo):
    # Documenta el límite de la aproximación; no afirma una propiedad universal inexistente.
    for t in datos_ejemplo['tipos_terreno'].values():
        if t['transitable']:
            t['costo'] = 10
    e = cargar_escenario(datos_ejemplo)
    s = EstadoJuego(((0, 1), (2, 1), (0, 3), (3, 0)), None, (2, 2), 'A')
    nuevo = aplicar(e, s, Accion('MOVER', 'A2', (2, 2)))
    assert evaluar(e, nuevo, 'A')[0] < evaluar(e, s, 'A')[0]


def test_costos_acciones(datos_ejemplo):
    e = cargar_escenario(datos_ejemplo)
    assert costo_accion(e, Accion('MOVER', 'A1', (0, 2))) == e.costo((0, 2))
    assert costo_accion(e, Accion('INTERCEPTAR', 'A1')) == 0
    assert costo_accion(e, Accion('PASAR')) == 0


@pytest.mark.parametrize('opciones', [dict(objetivo=(99, 0)), dict(objetivo=(0,)),
                                     dict(orden=('abajo', 'arriba'))])
def test_opciones_directas_invalidas(datos_ejemplo, opciones):
    with pytest.raises(ValueError):
        crear_problema(cargar_escenario(datos_ejemplo), unidad='A1', **opciones)
