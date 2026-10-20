"""Problemas de búsqueda (spec 002 §3.4). Los algoritmos solo usan estos tres métodos:

    inicio            estado inicial
    es_objetivo(s)    prueba de objetivo
    sucesores(s)      lista de (estado_siguiente, costo) en orden determinista

En modo búsqueda las demás unidades se ignoran salvo que se pasen como ``bloqueadas`` (D-05).
"""

from __future__ import annotations

from tacticalgrid.config import ORDEN_MOVIMIENTOS
from tacticalgrid.escenario.modelo import Escenario


class ProblemaNavegacion:
    """Ir de ``inicio`` a ``objetivo``. Estado = (fila, columna)."""

    def __init__(self, escenario: Escenario, inicio, objetivo, orden=ORDEN_MOVIMIENTOS, bloqueadas=()):
        self.escenario, self.inicio, self.objetivo = escenario, inicio, objetivo
        self.orden, self.bloqueadas = orden, set(bloqueadas)

    def es_objetivo(self, s) -> bool:
        return s == self.objetivo

    def sucesores(self, s) -> list:
        """Celdas vecinas transitables y no bloqueadas, con el costo de entrar a cada una.

        Purpose: función sucesor y costo de la navegación (la usan BFS, DFS, UCS, A* y Beam).
        Preconditions: ``s`` es una celda del mapa.
        Postconditions: pares (vecino, escenario.costo(vecino)) en el orden ``self.orden``.
        Complexity: O(4).
        AI usage: Yes
        AI intervention: Claude Code escribió el método.
        Student validation: pruebas test_navegacion_sucesores, en verde.
            Revisado por Daniel Quintero (20 oct: código, pytest y GUI; ver docs/USO_IA.md)
            y por Juan Ocampo antes de la sustentación.
        """
        return [(v, self.escenario.costo(v)) for v in self.escenario.vecinos(s, self.orden) if v not in self.bloqueadas]


class ProblemaMision:
    """Recoger el recurso y llevarlo a la base propia. Estado = ((fila, columna), lleva_recurso).

    Es el "estado compuesto" del caso 6: la misma celda con y sin recurso son estados distintos.
    """

    def __init__(self, escenario: Escenario, id_unidad: str, orden=ORDEN_MOVIMIENTOS, bloqueadas=()):
        unidad = next(u for u in escenario.unidades if u.id == id_unidad)
        self.escenario, self.orden, self.bloqueadas = escenario, orden, set(bloqueadas)
        self.inicio = (unidad.pos, escenario.portador == id_unidad or unidad.pos == escenario.recurso)
        self.objetivo = (escenario.bases[unidad.bando], True)

    def es_objetivo(self, s) -> bool:
        return s == self.objetivo

    def sucesores(self, s) -> list:
        """Como en la navegación, pero ``lleva`` pasa a True al entrar a la celda del recurso.

        Purpose: función sucesor del problema con estado compuesto (caso 6).
        Preconditions: ``s`` = (celda del mapa, bool).
        Postconditions: pares ((vecino, lleva or vecino == recurso), costo de entrar al vecino).
        Complexity: O(4).
        AI usage: Yes
        AI intervention: Claude Code escribió el método.
        Student validation: pruebas test_mision_estado_compuesto y caso 6, en verde.
            Revisado por Daniel Quintero (20 oct: código, pytest y GUI; ver docs/USO_IA.md)
            y por Juan Ocampo antes de la sustentación.
        """
        pos, lleva = s
        recurso = self.escenario.recurso
        return [
            ((v, lleva or v == recurso), self.escenario.costo(v))
            for v in self.escenario.vecinos(pos, self.orden)
            if v not in self.bloqueadas
        ]
