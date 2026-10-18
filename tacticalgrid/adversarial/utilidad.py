"""Función de utilidad / evaluación (spec 005 §4), siempre desde la perspectiva de ``bando_max``.

Es de suma cero: evaluar(s, "A") == -evaluar(s, "B"). Por eso MIN no está en desventaja:
minimizar la utilidad de A es exactamente lo mismo que maximizar la de B.
"""

from __future__ import annotations

import math
from dataclasses import replace
from functools import lru_cache
from heapq import heappop, heappush

from tacticalgrid.config import PESOS_UTILIDAD, VALOR_VICTORIA
from tacticalgrid.juego.reglas import acciones_legales, bando_de, ganador, posicion_de, rival

LEJOS = 1000  # distancia usada cuando un destino es inalcanzable (evita restar infinitos)


def _costos_hacia(escenario, destino, prohibida) -> dict:
    """Dijkstra inverso: costo mínimo desde cada celda hasta ``destino`` sin pasar por ``prohibida``."""
    distancia = {destino: 0}
    frontera = [(0, destino)]
    while frontera:
        d, u = heappop(frontera)
        if d > distancia[u]:
            continue
        for v in escenario.vecinos(u):
            nueva = d + escenario.costo(u)  # ir de v a u cuesta entrar a u
            if v != prohibida and nueva < distancia.get(v, math.inf):
                distancia[v] = nueva
                heappush(frontera, (nueva, v))
    return distancia


@lru_cache(maxsize=16)
def distancias(escenario) -> dict:
    """Costos reales precalculados una vez por escenario: hacia cada base y hacia el recurso, por bando.

    Purpose: que la evaluación use distancias con costos de terreno y muros (coherente con UCS).
    Preconditions: escenario validado (se usa como clave de caché por identidad).
    Postconditions: {"base_A", "base_B", "recurso_A", "recurso_B"} -> {celda: costo}; las unidades de un
        bando nunca pasan por la base rival (R3). El recurso libre siempre está en su posición inicial (D-14).
    Complexity: 4 Dijkstra, O(V log V) cada uno; luego O(1) por consulta.
    AI usage: Yes
    AI intervention: Claude Code escribió el precálculo.
    Student validation: PENDIENTE: revisar test_distancias.
    """
    resultado = {}
    for bando in ("A", "B"):
        prohibida = escenario.bases[rival(bando)]
        resultado[f"base_{bando}"] = _costos_hacia(escenario, escenario.bases[bando], prohibida)
        resultado[f"recurso_{bando}"] = _costos_hacia(escenario, escenario.recurso, prohibida)
    return resultado


def utilidad_terminal(escenario, estado, bando_max: str, profundidad: int) -> float:
    """+V si gana MAX (antes es mejor), -V si gana MIN (después es menos malo), 0 si es empate."""
    g = ganador(escenario, estado)
    if g is None:
        return 0
    return VALOR_VICTORIA - profundidad if g == bando_max else -VALOR_VICTORIA + profundidad


def restante(escenario, estado, bando: str) -> float:
    """Costo que le falta a ``bando`` para ganar si nadie lo estorbara (con distancias reales).

    Si lo lleva el bando: del portador a su base. Si está libre: de su unidad más cercana al recurso
    y del recurso a su base. Si lo lleva el rival: de su unidad más cercana al portador (Manhattan,
    para interceptarlo) y de ahí a su base.
    """
    dist = distancias(escenario)
    propias = [p for u, p in zip(escenario.unidades, estado.posiciones) if u.bando == bando]
    hacia_base = dist[f"base_{bando}"]
    if estado.portador is None:
        llegar = min((dist[f"recurso_{bando}"].get(p, LEJOS) for p in propias), default=LEJOS)
        return llegar + hacia_base.get(escenario.recurso, LEJOS)
    pos = posicion_de(escenario, estado, estado.portador)
    if bando_de(escenario, estado.portador) == bando:
        return hacia_base.get(pos, LEJOS)
    alcanzar = min((abs(p[0] - pos[0]) + abs(p[1] - pos[1]) for p in propias), default=LEJOS)
    return alcanzar + hacia_base.get(pos, LEJOS)


def evaluar(escenario, estado, bando_max: str, pesos=None) -> tuple[float, dict]:
    """Valor de un estado NO terminal para ``bando_max`` y su desglose por componente.

    Purpose: estimar qué tan bueno es un estado cuando Minimax llega a la profundidad máxima.
    Preconditions: ``estado`` válido; ``pesos`` con las claves de config.PESOS_UTILIDAD (o None).
    Postconditions: valor = Σ peso_i · f_i con (positivo = bueno para MAX):
        posesion  +1 si MAX lleva el recurso, -1 si lo lleva MIN, 0 si está libre;
        carrera   restante(MIN) - restante(MAX): quién está más cerca de ganar (ver ``restante``);
        movilidad (# acciones de MAX) - (# acciones de MIN): penaliza quedar bloqueado.
        Recoger el recurso nunca empeora el valor (posesion sube y carrera no baja).
        Cumple evaluar(s, "A") == -evaluar(s, "B").
    Complexity: O(U) con U unidades (distancias precalculadas; movilidad genera acciones de ambos bandos).
    AI usage: Yes
    AI intervention: Claude Code propuso los componentes y escribió la función. Una primera versión con 5
        componentes (posesión, carrera, entrega, presión, movilidad) hacía que una unidad al lado del
        recurso prefiriera NO recogerlo; se unificó todo en ``restante`` para que fuera monótona.
    Student validation: PENDIENTE: revisar test_suma_cero, test_recoger_siempre_mejora y test_pesos_desde_json.
    """
    pesos = pesos or PESOS_UTILIDAD
    bando_min = rival(bando_max)
    f = {"posesion": 0, "carrera": 0, "movilidad": 0}
    if estado.portador is not None:
        f["posesion"] = 1 if bando_de(escenario, estado.portador) == bando_max else -1
    f["carrera"] = restante(escenario, estado, bando_min) - restante(escenario, estado, bando_max)

    def movilidad(bando):
        acciones = acciones_legales(escenario, replace(estado, turno=bando))
        return 0 if acciones[0].tipo == "PASAR" else len(acciones)

    f["movilidad"] = movilidad(bando_max) - movilidad(bando_min)
    return sum(pesos[k] * f[k] for k in f), f
