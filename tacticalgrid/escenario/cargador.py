"""Carga atómica de escenarios (spec 001): primero se valida todo, después se construye."""

from __future__ import annotations

import json

from tacticalgrid.escenario.modelo import Escenario, Unidad
from tacticalgrid.escenario.validador import validar


class EscenarioInvalido(Exception):
    def __init__(self, errores: list[str]):
        super().__init__("Escenario inválido:\n" + "\n".join(errores))
        self.errores = errores


def cargar_escenario(fuente) -> Escenario:
    """Lee un escenario JSON (ruta o dict ya leído) y devuelve un ``Escenario``.

    Purpose: punto único de entrada de escenarios; garantiza carga completa o nada (P8).
    Preconditions: ``fuente`` es una ruta a un archivo JSON o un dict.
    Postconditions: si el escenario es válido devuelve un ``Escenario`` nuevo; si no, lanza
        ``EscenarioInvalido`` con todos los errores. Como la excepción ocurre antes de devolver,
        ``escenario = cargar_escenario(ruta)`` deja intacto el escenario anterior.
        Los bandos se normalizan a mayúscula (D-01).
    Complexity: O(F·C + U), dominado por la validación.
    AI usage: Yes
    AI intervention: Claude Code escribió la función.
    Student validation: pruebas test_carga_atomica, test_json_mal_formado y la carga de escenarios/invalidos/ en la GUI (captura 02), en verde.
        Revisado por Daniel Quintero (20 oct: código, pytest y GUI; ver docs/USO_IA.md)
        Revisión humana de las correcciones de Codex por realizar; ver docs/USO_IA.md.
    """
    if isinstance(fuente, dict):
        datos = fuente
    else:
        with open(fuente, encoding="utf-8") as archivo:
            try:
                datos = json.load(archivo)
            except json.JSONDecodeError as e:
                raise EscenarioInvalido([f"[E00] JSON mal formado: {e}"]) from None

    errores = validar(datos)
    if errores:
        raise EscenarioInvalido(errores)

    tipos = datos["tipos_terreno"]
    return Escenario(
        filas=datos["mapa"]["filas"],
        columnas=datos["mapa"]["columnas"],
        costos={nombre: (t["costo"] if t["transitable"] else None) for nombre, t in tipos.items()},
        terreno=tuple(tuple(fila) for fila in datos["terreno"]),
        bases={b: (datos["bases"][b]["fila"], datos["bases"][b]["columna"]) for b in ("A", "B")},
        recurso=(datos["recurso"]["fila"], datos["recurso"]["columna"]),
        unidades=tuple(
            Unidad(u["id"], u["bando"].upper(), u.get("tipo", "estandar"), (u["fila"], u["columna"]))
            for u in datos["unidades"]
        ),
        turno=datos["turno"].upper(),
        portador=datos["juego"]["portador_recurso"],
        juego=dict(datos["juego"]),
        prueba=datos.get("prueba"),
    )
