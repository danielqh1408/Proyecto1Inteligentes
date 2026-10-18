"""Estado de la partida y acciones (spec 002).

Lo que no cambia (mapa, costos, bases, identidad de las unidades) vive en el Escenario.
Aquí solo está lo que cambia turno a turno.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from tacticalgrid.escenario.modelo import Escenario


@dataclass(frozen=True)
class EstadoJuego:
    posiciones: tuple[tuple[int, int], ...]  # misma posición i que escenario.unidades[i]
    portador: str | None                      # id de la unidad que lleva el recurso, o None
    recurso: tuple[int, int] | None           # dónde está el recurso si está libre; None si alguien lo lleva
    turno: str                                # "A" o "B": bando que debe actuar
    turnos_jugados: int = 0                   # para el empate por límite de turnos


class Accion(NamedTuple):
    tipo: str                               # "MOVER", "INTERCEPTAR" o "PASAR"
    unidad: str | None = None               # quién actúa (None en PASAR)
    destino: tuple[int, int] | None = None  # solo en MOVER

    def __str__(self) -> str:
        if self.tipo == "MOVER":
            return f"{self.unidad} → {self.destino}"
        if self.tipo == "INTERCEPTAR":
            return f"{self.unidad} intercepta"
        return "PASAR"


def estado_inicial(escenario: Escenario) -> EstadoJuego:
    """Construye el estado de la partida a partir del escenario cargado.

    Purpose: definir sin ambigüedad el estado inicial (requisito de modelado del PDF).
    Preconditions: ``escenario`` fue validado (spec 001).
    Postconditions: posiciones = las del JSON; si hay ``portador_recurso`` el recurso va con él
        (D-03); si una unidad empieza sobre el recurso libre, lo lleva (R4); turnos_jugados = 0.
    Complexity: O(U) con U unidades.
    AI usage: Yes
    AI intervention: Claude Code escribió la función.
    Student validation: PENDIENTE: revisar test_estado_inicial.
    """
    posiciones = tuple(u.pos for u in escenario.unidades)
    portador = escenario.portador
    if portador is None:
        for u in escenario.unidades:
            if u.pos == escenario.recurso:
                portador = u.id
    recurso = None if portador else escenario.recurso
    return EstadoJuego(posiciones, portador, recurso, escenario.turno)
