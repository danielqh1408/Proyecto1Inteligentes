"""Verificación de soluciones (spec 006). Recalcula todo desde el escenario y las reglas:
no confía en lo que reporta el algoritmo. Cada función devuelve [(chequeo, ok), ...]."""

from __future__ import annotations

from tacticalgrid.adversarial.minimax import alfa_beta, minimax
from tacticalgrid.busqueda.algoritmos import bfs
from tacticalgrid.busqueda.resultado import posicion
from tacticalgrid.juego.reglas import acciones_legales, aplicar, validar_estado


def verificar_camino(escenario, problema, resultado) -> list[tuple[str, bool]]:
    """Comprueba el camino de una búsqueda contra el escenario.

    Purpose: verificación exigida por el PDF: movimientos válidos, sin obstáculos, costo correcto,
        objetivo alcanzado y estados válidos.
    Preconditions: ``resultado`` se obtuvo con ``problema`` sobre ``escenario``.
    Postconditions: lista de (chequeo, ok). Si no hubo éxito se comprueba que el camino esté vacío y, salvo
        en Beam (que no es completo y puede fallar aunque exista camino), que BFS confirme que es inalcanzable.
    Complexity: O(L) con L = longitud del camino (+ O(V) si hay que confirmar con BFS).
    AI usage: Yes
    AI intervention: Claude Code escribió la función.
    Student validation: pruebas test_detecta_manipulaciones y test_todos_los_resultados, en verde.
        Revisado por Daniel Quintero (20 oct: código, pytest y GUI; ver docs/USO_IA.md)
        y por Juan Ocampo antes de la sustentación.
    """
    camino = resultado.camino
    if not resultado.exito:
        chequeos = [("sin solución: el camino está vacío", camino == [])]
        if resultado.algoritmo != "BEAM":
            chequeos.append(("BFS confirma que el objetivo es inalcanzable", not bfs(problema).exito))
        return chequeos
    celdas = [posicion(s) for s in camino]
    pasos = list(zip(camino, camino[1:]))
    sin_obstaculos = all(escenario.transitable(c) for c in celdas)
    return [
        ("empieza en el estado inicial", camino[0] == problema.inicio),
        ("cada movimiento va a una celda vecina dentro del mapa",
         all(escenario.dentro(b) and abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(celdas, celdas[1:]))),
        ("ninguna celda es un obstáculo", sin_obstaculos),
        ("cada paso es un sucesor válido del anterior", all(b in [s for s, _ in problema.sucesores(a)] for a, b in pasos)),
        ("el costo reportado coincide con las transiciones",
         sin_obstaculos and abs(sum(escenario.costo(c) for c in celdas[1:]) - resultado.costo) < 1e-9),
        ("la longitud reportada coincide", resultado.longitud == len(camino) - 1),
        ("el estado final cumple la condición objetivo", problema.es_objetivo(camino[-1])),
    ]


def verificar_decision(escenario, estado, decision) -> list[tuple[str, bool]]:
    """Comprueba que la decisión de Minimax/alfa-beta respete las reglas del juego.

    Purpose: "las acciones consideradas por minimax son legales dentro de las reglas del juego".
    Preconditions: ``decision`` se calculó para ``estado``.
    Postconditions: lista de (chequeo, ok) sobre la acción elegida, las acciones de la raíz y los
        estados que producen.
    Complexity: O(b · U) con b acciones de la raíz y U unidades.
    AI usage: Yes
    AI intervention: Claude Code escribió la función.
    Student validation: pruebas test_decision_ilegal y test_decision_legal_y_minimax_igual_alfabeta, en verde.
        Revisado por Daniel Quintero (20 oct: código, pytest y GUI; ver docs/USO_IA.md)
        y por Juan Ocampo antes de la sustentación.
    """
    legales = acciones_legales(escenario, estado)
    consideradas = [a for a, _ in decision.valores_raiz]
    return [
        ("la acción elegida es legal", decision.accion in legales),
        ("todas las acciones evaluadas en la raíz son legales", all(a in legales for a in consideradas)),
        ("se evaluaron todas las acciones legales de la raíz", sorted(map(str, consideradas)) == sorted(map(str, legales))),
        ("los estados resultantes son válidos",
         all(validar_estado(escenario, aplicar(escenario, estado, a)) == [] for a in legales)),
    ]


def verificar_minimax_vs_alfabeta(escenario, estado, profundidad=None, orden=None) -> list[tuple[str, bool]]:
    """Con igual profundidad, utilidad y orden, Minimax y alfa-beta deben decidir lo mismo."""
    mm = minimax(escenario, estado, profundidad, orden)
    ab = alfa_beta(escenario, estado, profundidad, orden)
    return [
        (f"misma acción ({mm.accion} / {ab.accion})", mm.accion == ab.accion),
        (f"mismo valor ({mm.valor} / {ab.valor})", mm.valor == ab.valor),
        (f"alfa-beta evalúa menos o igual ({ab.nodos_evaluados} <= {mm.nodos_evaluados})",
         ab.nodos_evaluados <= mm.nodos_evaluados),
    ]


def texto(chequeos: list[tuple[str, bool]]) -> str:
    return "\n".join(f"  {'✔' if ok else '✘'} {nombre}" for nombre, ok in chequeos)
