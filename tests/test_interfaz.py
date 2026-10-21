"""Regresiones de GUI. Se ejecutan con un Python que incluya Tk; no abren diálogos."""

import json
import pytest

tk = pytest.importorskip('tkinter', reason='Este Python no incluye Tk; usar .venv-gui')
from tacticalgrid.interfaz.app import App


@pytest.fixture
def app(monkeypatch):
    raiz = tk.Tk()
    raiz.withdraw()
    monkeypatch.setattr('tkinter.messagebox.showerror', lambda *a, **k: None)
    instancia = App(raiz, 'escenarios/ejemplo_enunciado.json')
    yield instancia
    raiz.destroy()


def test_carga_opciones_y_restablece_defectos(app, datos_ejemplo, tmp_path):
    datos_ejemplo['prueba'].update(algoritmo='BEAM', k=8, heuristica='obstaculos',
        unidades_bloquean=True, orden_movimientos=['izquierda', 'derecha', 'arriba', 'abajo'])
    ruta = tmp_path / 'config.json'
    ruta.write_text(json.dumps(datos_ejemplo))
    app.cargar(str(ruta))
    assert app.v_k.get() == 8 and app.v_heuristica.get() == 'obstaculos'
    assert app.v_bloquean.get()
    assert app.crear_problema().orden == ('izquierda', 'derecha', 'arriba', 'abajo')
    app.buscar()
    assert app.resultado.extra['k'] == 8
    app.cargar('escenarios/ejemplo_enunciado.json')
    assert app.v_k.get() == 2 and app.v_heuristica.get() == 'manhattan'
    assert not app.v_bloquean.get() and not app.tabla.get_children()


def test_objetivo_incompleto_no_cambia_nada(app, datos_ejemplo, tmp_path):
    anterior, estado = app.escenario, app.estado
    datos_ejemplo['prueba']['objetivo'] = {'fila': 2}
    ruta = tmp_path / 'malo.json'
    ruta.write_text(json.dumps(datos_ejemplo))
    app.cargar(str(ruta))
    assert app.escenario is anterior and app.estado is estado


def test_verificar_despues_de_jugar(app):
    app.v_prof.set(2)
    app.decidir()
    app.aplicar_y_dibujar(app.decision.accion)
    assert app.decision is None
    app.verificar()
    texto = app.texto.get('1.0', 'end')
    assert '✔' in texto and '✘' not in texto


def test_control_invalido_no_rompe_callback(app):
    app.v_prof.set(-1)
    app.decidir()
    assert app.decision is None
    app.v_k.set(-1)
    app.v_algoritmo.set('BEAM')
    app.buscar()
    assert app.resultado is None
