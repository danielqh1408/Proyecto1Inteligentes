"""Modo partida (``prueba.modo = "partida"``): ambos bandos juegan por turnos con el agente elegido."""

from __future__ import annotations

from tacticalgrid.adversarial.minimax import alfa_beta, minimax, voraz
from tacticalgrid.juego.estado import estado_inicial
from tacticalgrid.juego.reglas import aplicar, es_terminal, ganador

AGENTES = ("MINIMAX", "ALFA_BETA", "VORAZ")


def decidir_con(agente: str, escenario, estado, profundidad=None, orden=None):
    """Decisión del ``agente`` ("MINIMAX", "ALFA_BETA" o "VORAZ") en ``estado``."""
    if agente == "MINIMAX":
        return minimax(escenario, estado, profundidad, orden)
    if agente == "ALFA_BETA":
        return alfa_beta(escenario, estado, profundidad, orden)
    if agente == "VORAZ":
        return voraz(escenario, estado)
    raise ValueError(f"Agente desconocido '{agente}'. Válidos: {', '.join(AGENTES)}")


def jugar(escenario, agentes: dict, profundidades: dict | None = None, max_jugadas: int | None = None, estado=None):
    """Juega desde ``estado`` (o el inicial) hasta terminar o hacer ``max_jugadas``.

    ``agentes`` = {"A": "ALFA_BETA", "B": "VORAZ"}; ``profundidades`` = {"A": 3, "B": 2}.
    Devuelve (estado_final, historial) con una línea (turno, bando, acción, valor) por jugada.
    """
    estado = estado or estado_inicial(escenario)
    profundidades = profundidades or {}
    historial = []
    while not es_terminal(escenario, estado) and (max_jugadas is None or len(historial) < max_jugadas):
        bando = estado.turno
        d = decidir_con(agentes[bando], escenario, estado, profundidades.get(bando))
        historial.append((estado.turnos_jugados, bando, str(d.accion), d.valor))
        estado = aplicar(escenario, estado, d.accion)
    return estado, historial


def resumen_final(escenario, estado) -> str:
    g = ganador(escenario, estado)
    if g:
        return f"Gana el bando {g} en {estado.turnos_jugados} turnos"
    return "Empate (límite de turnos)" if es_terminal(escenario, estado) else f"Sin terminar ({estado.turnos_jugados} turnos)"
