"""Minimax y Minimax con poda alfa-beta (spec 005), con profundidad limitada.

Los dos usan la MISMA función recursiva; la única diferencia es la línea de la poda
(``if poda and alfa >= beta: break``). Así, con igual profundidad, utilidad y orden de acciones,
eligen siempre la misma acción y el mismo valor (RF-005-3).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from time import perf_counter

from tacticalgrid.adversarial.utilidad import evaluar, utilidad_terminal
from tacticalgrid.config import DEFECTOS_JUEGO, PESOS_UTILIDAD
from tacticalgrid.juego.reglas import acciones_legales, aplicar, es_terminal


@dataclass
class Decision:
    algoritmo: str
    accion: object = None
    valor: float = 0
    nodos_generados: int = 1          # estados creados con aplicar + la raíz
    nodos_evaluados: int = 0          # llamadas a utilidad terminal o a evaluar
    nodos_podados: int = 0            # acciones hermanas que alfa-beta no exploró
    profundidad_alcanzada: int = 0
    tiempo_ms: float = 0
    valores_raiz: list = field(default_factory=list)  # (acción, valor) de cada acción de la raíz
    extra: dict = field(default_factory=dict)

    def como_dict(self) -> dict:
        return {
            "algoritmo": self.algoritmo,
            "accion": str(self.accion),
            "valor": self.valor,
            "nodos_generados": self.nodos_generados,
            "nodos_evaluados": self.nodos_evaluados,
            "nodos_podados": self.nodos_podados,
            "profundidad_alcanzada": self.profundidad_alcanzada,
            "tiempo_ms": round(self.tiempo_ms, 3),
            "valores_raiz": [[str(a), v] for a, v in self.valores_raiz],
            **self.extra,
        }


def ordenar_acciones(escenario, estado, orden: str, bando_max: str, pesos) -> list:
    """Acciones legales en el orden pedido: "natural" (R10), "inverso" o "heuristico".

    Purpose: permitir el experimento del enunciado "cambiar el orden de generación de acciones".
    Preconditions: ``orden`` es uno de los tres nombres.
    Postconditions: mismas acciones, distinto orden. "heuristico" pone primero las que dejan el mejor
        estado para quien mueve (evaluación estática, descendente para MAX y ascendente para MIN);
        esas evaluaciones de ordenamiento no se cuentan en ``nodos_evaluados``.
    Complexity: O(b) para natural/inverso; O(b · (U + b log b)) para heurístico.
    AI usage: Yes
    AI intervention: Claude Code escribió la función.
    Student validation: PENDIENTE: revisar el caso 9.
    """
    acciones = acciones_legales(escenario, estado)
    if orden == "inverso":
        return acciones[::-1]
    if orden == "heuristico":
        es_max = estado.turno == bando_max
        valor = lambda a: evaluar(escenario, aplicar(escenario, estado, a), bando_max, pesos)[0]
        return sorted(acciones, key=valor, reverse=es_max)
    return acciones


def decidir(escenario, estado, profundidad=None, poda=True, orden=None, pesos=None) -> Decision:
    """Mejor acción para el bando en turno (MAX) mirando ``profundidad`` jugadas hacia adelante.

    Purpose: decisión adversarial: "¿cuál es mi mejor acción teniendo en cuenta las respuestas del rival?".
    Preconditions: ``estado`` no es terminal; profundidad >= 1. Lo que no se pase se toma del JSON
        (prueba.profundidad o juego.profundidad_maxima_minimax, juego.orden_acciones,
        juego.pesos_utilidad) o de config.
    Postconditions: ``accion`` es legal; ``valor`` es el valor Minimax de la raíz; se elige la PRIMERA
        acción con valor estrictamente mayor, así Minimax y alfa-beta coinciden. Con ``poda`` se dejan de
        explorar las acciones restantes de un nodo cuando alfa >= beta (no pueden cambiar la decisión).
    Complexity: Minimax O(b^d); alfa-beta O(b^(d/2)) en el mejor orden y O(b^d) en el peor
        (b = acciones por turno, d = profundidad). Espacio O(b · d) por la recursión.
    AI usage: Yes
    AI intervention: Claude Code adaptó ``minimax_limitado`` y ``alfa_beta`` de los notebooks en una sola
        función con métricas, orden de acciones y la bandera ``poda``.
    Student validation: PENDIENTE: revisar test_minimax_igual_alfabeta y los casos 7 a 10.
    """
    t0 = perf_counter()
    juego = escenario.juego
    prueba = escenario.prueba or {}
    profundidad = (profundidad or prueba.get("profundidad")
                   or juego.get("profundidad_maxima_minimax", DEFECTOS_JUEGO["profundidad_maxima_minimax"]))
    orden = orden or juego.get("orden_acciones", DEFECTOS_JUEGO["orden_acciones"])
    pesos = {**PESOS_UTILIDAD, **juego.get("pesos_utilidad", {}), **(pesos or {})}
    bando_max = estado.turno
    d = Decision("ALFA_BETA" if poda else "MINIMAX", extra={"profundidad": profundidad, "orden": orden})

    def valor(s, nivel, alfa, beta):
        d.profundidad_alcanzada = max(d.profundidad_alcanzada, nivel)
        if es_terminal(escenario, s):
            d.nodos_evaluados += 1
            return utilidad_terminal(escenario, s, bando_max, nivel)
        if nivel == profundidad:
            d.nodos_evaluados += 1
            return evaluar(escenario, s, bando_max, pesos)[0]
        es_max = s.turno == bando_max
        mejor = -math.inf if es_max else math.inf
        acciones = ordenar_acciones(escenario, s, orden, bando_max, pesos)
        for i, accion in enumerate(acciones):
            hijo = aplicar(escenario, s, accion)
            d.nodos_generados += 1
            v = valor(hijo, nivel + 1, alfa, beta)
            if es_max:
                mejor = max(mejor, v)
                alfa = max(alfa, mejor)
            else:
                mejor = min(mejor, v)
                beta = min(beta, mejor)
            if poda and alfa >= beta:
                d.nodos_podados += len(acciones) - i - 1
                break
        return mejor

    d.valor, alfa = -math.inf, -math.inf
    for accion in ordenar_acciones(escenario, estado, orden, bando_max, pesos):
        hijo = aplicar(escenario, estado, accion)
        d.nodos_generados += 1
        v = valor(hijo, 1, alfa, math.inf)
        d.valores_raiz.append((accion, v))
        if v > d.valor:
            d.valor, d.accion = v, accion
            d.extra["desglose"] = evaluar(escenario, hijo, bando_max, pesos)[1]
        if poda:
            alfa = max(alfa, d.valor)
    d.tiempo_ms = (perf_counter() - t0) * 1000
    return d


def minimax(escenario, estado, profundidad=None, orden=None, pesos=None) -> Decision:
    return decidir(escenario, estado, profundidad, poda=False, orden=orden, pesos=pesos)


def alfa_beta(escenario, estado, profundidad=None, orden=None, pesos=None) -> Decision:
    return decidir(escenario, estado, profundidad, poda=True, orden=orden, pesos=pesos)


def voraz(escenario, estado) -> Decision:
    """Agente de contraste: mira solo 1 jugada (no considera la respuesta del rival).
    En la práctica "avanza directamente al recurso o a su base" (caso 7)."""
    d = decidir(escenario, estado, profundidad=1, poda=False, orden="natural")
    d.algoritmo = "VORAZ"
    return d
