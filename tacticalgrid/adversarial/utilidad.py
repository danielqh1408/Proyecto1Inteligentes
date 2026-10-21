"""Función de utilidad / evaluación (spec 005 §4), siempre desde la perspectiva de ``bando_max``.

Es de suma cero: evaluar(s, "A") == -evaluar(s, "B"). Por eso MIN no está en desventaja:
minimizar la utilidad de A es exactamente lo mismo que maximizar la de B.
"""

from __future__ import annotations

import math
from dataclasses import replace
from functools import lru_cache
from heapq import heappop, heappush

from tacticalgrid.config import DEFECTOS_JUEGO, PESOS_UTILIDAD, VALOR_VICTORIA
from tacticalgrid.juego.reglas import acciones_legales, bando_de, ganador, posicion_de, rival

def _costos_hacia(escenario, destino, prohibida) -> dict:
    """Dijkstra inverso, pagando el costo de entrar a la celda actual.

    Purpose: calcular costos mínimos hacia una base o el recurso.
    Preconditions: escenario validado, costos positivos.
    Postconditions: distancias mínimas; diccionario vacío si el destino es un muro o está prohibido.
    Complexity: O(V log V) tiempo y O(V) espacio en la cuadrícula.
    AI usage: Yes
    AI intervention: Claude implementó Dijkstra; Codex agregó el caso de destino no transitable.
    Student validation: regresiones en test_auditoria.py y test_distancias; revisión humana por realizar.
    """
    if not escenario.transitable(destino) or destino == prohibida:
        return {}
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
        bando nunca pasan por la base rival (R3). También incluye la penalización "inalcanzable". El recurso libre siempre está en su posición inicial (D-14).
    Complexity: 4 Dijkstra, O(V log V) cada uno; luego O(1) por consulta.
    AI usage: Yes
    AI intervention: Claude Code escribió el precálculo.
    Student validation: pruebas test_distancias, en verde.
        Revisado por Daniel Quintero (20 oct: código, pytest y GUI; ver docs/USO_IA.md)
        Revisión humana de las correcciones de Codex por realizar; ver docs/USO_IA.md.
    """
    # Una ruta mínima simple no visita una celda dos veces: esta penalización supera su costo.
    resultado = {"inalcanzable": 1 + sum(escenario.costos[t] for fila in escenario.terreno
                                       for t in fila if escenario.costos[t] is not None)}
    for bando in ("A", "B"):
        prohibida = escenario.bases[rival(bando)]
        resultado[f"base_{bando}"] = _costos_hacia(escenario, escenario.bases[bando], prohibida)
        resultado[f"recurso_{bando}"] = _costos_hacia(escenario, escenario.recurso, prohibida)
    return resultado


def utilidad_terminal(escenario, estado, bando_max: str, profundidad: int) -> float:
    """Victoria y derrota siempre fuera del intervalo de la evaluación no terminal.

    Purpose: priorizar ganar, prefiriendo victorias tempranas y derrotas tardías.
    Preconditions: estado terminal válido; profundidad no negativa.
    Postconditions: victoria >= 10000, derrota <= -10000, empate 0.
    Complexity: O(U) para consultar el ganador; O(1) espacio auxiliar.
    AI usage: Yes
    AI intervention: Claude implementó la utilidad; Codex separó su escala de la evaluación.
    Student validation: test_prefiere_ganar_con_costos_altos y test_preferencia_victoria_rapida; revisión humana por realizar.
    """
    g = ganador(escenario, estado)
    if g is None:
        return 0
    limite = escenario.juego.get("max_turnos", DEFECTOS_JUEGO["max_turnos"])
    valor = VALOR_VICTORIA + max(0, limite - profundidad)
    return valor if g == bando_max else -valor


def restante(escenario, estado, bando: str) -> float:
    """Estimación de lo que le falta a un bando; no es el costo exacto de una partida.

    Si lo lleva el bando: del portador a su base. Si está libre: de su unidad más cercana al recurso
    y del recurso a su base. Si lo lleva el rival: de su unidad más cercana al portador (Manhattan,
    para interceptarlo) y de ahí a su base.

    Purpose: componente de carrera de la evaluación.
    Preconditions: escenario y estado válidos.
    Postconditions: distancia relajada; si persigue mezcla pasos Manhattan con costo a base.
        Esa aproximación ignora el reinicio tras interceptar y no garantiza monotonicidad al recoger.
    Complexity: O(U) por consulta, después del precálculo de distancias.
    AI usage: Yes
    AI intervention: Claude propuso la aproximación; Codex sustituyó la penalización fija por una del mapa.
    Student validation: test_recoger_no_es_garantia_monotona y test_destino_en_muro_no_rompe_decision; revisión humana por realizar.
    """
    dist = distancias(escenario)
    lejos = dist["inalcanzable"]
    propias = [p for u, p in zip(escenario.unidades, estado.posiciones) if u.bando == bando]
    hacia_base = dist[f"base_{bando}"]
    if estado.portador is None:
        llegar = min((dist[f"recurso_{bando}"].get(p, lejos) for p in propias), default=lejos)
        return llegar + hacia_base.get(escenario.recurso, lejos)
    pos = posicion_de(escenario, estado, estado.portador)
    if bando_de(escenario, estado.portador) == bando:
        return hacia_base.get(pos, lejos)
    alcanzar = min((abs(p[0] - pos[0]) + abs(p[1] - pos[1]) for p in propias), default=lejos)
    return alcanzar + hacia_base.get(pos, lejos)


def evaluar(escenario, estado, bando_max: str, pesos=None) -> tuple[float, dict]:
    """Valor de un estado NO terminal para ``bando_max`` y su desglose por componente.

    Purpose: estimar qué tan bueno es un estado cuando Minimax llega a la profundidad máxima.
    Preconditions: ``estado`` válido; ``pesos`` con las claves de config.PESOS_UTILIDAD (o None).
    Postconditions: valor = Σ peso_i · f_i con (positivo = bueno para MAX):
        posesion  +1 si MAX lleva el recurso, -1 si lo lleva MIN, 0 si está libre;
        carrera   restante(MIN) - restante(MAX): quién está más cerca de ganar (ver ``restante``);
        movilidad (# acciones de MAX) - (# acciones de MIN): penaliza quedar bloqueado.
        La suma se recorta a [-9999, 9999]: nunca supera una victoria ni empeora una derrota.
        Cumple evaluar(s, "A") == -evaluar(s, "B").
    Complexity: O(U) con U unidades (distancias precalculadas; movilidad genera acciones de ambos bandos).
    AI usage: Yes
    AI intervention: Claude Code propuso los componentes y escribió la función. Una primera versión con 5
        componentes (posesión, carrera, entrega, presión, movilidad) hacía que una unidad al lado del
        recurso prefiriera NO recogerlo; se simplificó con ``restante``. Codex acotó el valor y
        corrigió la afirmación de monotonicidad: no es una garantía de esta aproximación.
    Student validation: pruebas test_suma_cero, test_recoger_mejora_en_ejemplo, test_pesos_desde_json y el torneo E6 (posesión 10/20/50). Daniel propuso bajar el peso de posesión de 50 a 20.
        Revisado por Daniel Quintero (20 oct: código, pytest y GUI; ver docs/USO_IA.md)
        Revisión humana de las correcciones de Codex por realizar; ver docs/USO_IA.md.
    """
    pesos = pesos or PESOS_UTILIDAD
    bando_min = rival(bando_max)
    f = {"posesion": 0, "carrera": 0, "movilidad": 0}
    if estado.portador is not None:
        f["posesion"] = 1 if bando_de(escenario, estado.portador) == bando_max else -1
    f["carrera"] = restante(escenario, estado, bando_min) - restante(escenario, estado, bando_max)

    def movilidad(bando):
        acciones = acciones_legales(escenario, replace(estado, turno=bando))
        return 0 if not acciones or acciones[0].tipo == "PASAR" else len(acciones)

    f["movilidad"] = movilidad(bando_max) - movilidad(bando_min)
    valor = sum(pesos[k] * f[k] for k in f)
    return max(-VALOR_VICTORIA + 1, min(VALOR_VICTORIA - 1, valor)), f
