"""Reglas del juego (spec 002, R1–R10). Ambos bandos usan exactamente las mismas reglas."""

from __future__ import annotations

from tacticalgrid.config import DEFECTOS_JUEGO, ORDEN_MOVIMIENTOS
from tacticalgrid.escenario.modelo import Escenario
from tacticalgrid.juego.estado import Accion, EstadoJuego


def rival(bando: str) -> str:
    return "B" if bando == "A" else "A"


def posicion_de(escenario: Escenario, estado: EstadoJuego, id_unidad: str) -> tuple[int, int]:
    for i, u in enumerate(escenario.unidades):
        if u.id == id_unidad:
            return estado.posiciones[i]
    raise KeyError(id_unidad)


def bando_de(escenario: Escenario, id_unidad: str) -> str:
    return next(u.bando for u in escenario.unidades if u.id == id_unidad)


def acciones_legales(escenario: Escenario, estado: EstadoJuego, orden=ORDEN_MOVIMIENTOS) -> list[Accion]:
    """Acciones que puede hacer el bando en turno, en orden determinista.

    Purpose: función sucesor del juego (la usan Minimax, alfa-beta, la partida y el verificador).
    Preconditions: ``estado`` es válido para ``escenario`` y no es terminal.
    Postconditions: por cada unidad del bando (orden del JSON): primero INTERCEPTAR si está al lado
        del portador enemigo (R5), luego MOVER a cada vecino transitable, libre y que no sea la
        base enemiga (R2, R3) en el orden ``orden``. Si no hay ninguna, solo [PASAR] (R7).
    Complexity: O(U) con U unidades (4 vecinos por unidad; ``ocupadas`` es un set).
    AI usage: Yes
    AI intervention: Claude Code escribió la función siguiendo las reglas R2, R3, R5, R7 y R10.
    Student validation: PENDIENTE: revisar test_mover_restricciones, test_interceptar y test_bloqueo_y_empate.
    """
    bando = estado.turno
    ocupadas = set(estado.posiciones)
    base_rival = escenario.bases[rival(bando)]
    pos_portador_rival = None
    if estado.portador and bando_de(escenario, estado.portador) != bando:
        pos_portador_rival = posicion_de(escenario, estado, estado.portador)

    acciones = []
    for u, (f, c) in zip(escenario.unidades, estado.posiciones):
        if u.bando != bando:
            continue
        if pos_portador_rival and abs(f - pos_portador_rival[0]) + abs(c - pos_portador_rival[1]) == 1:
            acciones.append(Accion("INTERCEPTAR", u.id))
        for destino in escenario.vecinos((f, c), orden):
            if destino not in ocupadas and destino != base_rival:
                acciones.append(Accion("MOVER", u.id, destino))
    return acciones or [Accion("PASAR")]


def aplicar(escenario: Escenario, estado: EstadoJuego, accion: Accion) -> EstadoJuego:
    """Devuelve el estado que resulta de ejecutar ``accion`` (el estado original no cambia).

    Purpose: función de transición del juego.
    Preconditions: ``accion`` está en ``acciones_legales(escenario, estado)``; si no, lanza ValueError.
    Postconditions: MOVER cambia la posición de la unidad y recoge el recurso si entra a su celda (R4);
        INTERCEPTAR pasa el recurso al interceptor y devuelve al antiguo portador a su posición inicial
        si está libre (R5, evita que dos unidades se lo quiten para siempre); siempre cambia el turno
        y suma 1 a turnos_jugados (R1).
    Complexity: O(U), dominado por comprobar la legalidad.
    AI usage: Yes
    AI intervention: Claude Code escribió la función.
    Student validation: PENDIENTE: revisar test_recoger_y_entregar y test_interceptar.
    """
    if accion not in acciones_legales(escenario, estado):
        raise ValueError(f"Acción ilegal para el bando {estado.turno}: {accion}")
    posiciones = list(estado.posiciones)
    portador, recurso = estado.portador, estado.recurso
    if accion.tipo == "MOVER":
        i = next(i for i, u in enumerate(escenario.unidades) if u.id == accion.unidad)
        posiciones[i] = accion.destino
        if accion.destino == recurso:
            portador, recurso = accion.unidad, None
    elif accion.tipo == "INTERCEPTAR":
        j = next(j for j, u in enumerate(escenario.unidades) if u.id == estado.portador)
        if escenario.unidades[j].pos not in posiciones:
            posiciones[j] = escenario.unidades[j].pos  # el antiguo portador vuelve a su posición inicial
        portador = accion.unidad
    return EstadoJuego(tuple(posiciones), portador, recurso, rival(estado.turno), estado.turnos_jugados + 1)


def costo_accion(escenario: Escenario, accion: Accion) -> float:
    """Costo de una acción: costo del terreno de destino al MOVER; 0 al INTERCEPTAR o PASAR."""
    return escenario.costo(accion.destino) if accion.tipo == "MOVER" else 0


def ganador(escenario: Escenario, estado: EstadoJuego) -> str | None:
    """Bando ganador si el portador está en su propia base (R6); si no, None."""
    if estado.portador is None:
        return None
    bando = bando_de(escenario, estado.portador)
    if posicion_de(escenario, estado, estado.portador) == escenario.bases[bando]:
        return bando
    return None


def es_terminal(escenario: Escenario, estado: EstadoJuego) -> bool:
    """La partida termina si alguien ganó (R6) o se llegó al límite de turnos: empate (R8)."""
    max_turnos = escenario.juego.get("max_turnos", DEFECTOS_JUEGO["max_turnos"])
    return ganador(escenario, estado) is not None or estado.turnos_jugados >= max_turnos


def validar_estado(escenario: Escenario, estado: EstadoJuego) -> list[str]:
    """Lista de invariantes que el estado incumple (vacía si es válido).

    Purpose: detectar estados inválidos (lo exige la verificación del PDF, spec 006).
    Preconditions: ninguna.
    Postconditions: revisa que haya una posición por unidad, todas dentro del mapa y transitables,
        sin dos unidades en la misma celda, que el recurso esté libre XOR tenga portador existente,
        y que el turno sea A o B.
    Complexity: O(U).
    AI usage: Yes
    AI intervention: Claude Code escribió la función.
    Student validation: PENDIENTE: revisar test_invariantes_alcanzables.
    """
    errores = []
    if len(estado.posiciones) != len(escenario.unidades):
        return [f"hay {len(estado.posiciones)} posiciones para {len(escenario.unidades)} unidades"]
    for u, pos in zip(escenario.unidades, estado.posiciones):
        if not escenario.transitable(pos):
            errores.append(f"{u.id} está en {pos}, fuera del mapa o en celda no transitable")
    if len(set(estado.posiciones)) != len(estado.posiciones):
        errores.append("dos unidades ocupan la misma celda")
    if (estado.portador is None) == (estado.recurso is None):
        errores.append("el recurso debe estar libre o tener portador, no ambas cosas ni ninguna")
    if estado.portador is not None and estado.portador not in [u.id for u in escenario.unidades]:
        errores.append(f"el portador {estado.portador} no existe")
    if estado.turno not in ("A", "B"):
        errores.append(f"turno inválido {estado.turno!r}")
    return errores
