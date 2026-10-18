"""Modelo del escenario (spec 001): todo lo que NO cambia durante la partida.

Las posiciones son tuplas (fila, columna), igual que en los notebooks de clase.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from tacticalgrid.config import ORDEN_MOVIMIENTOS

DIRECCIONES = {"arriba": (-1, 0), "abajo": (1, 0), "izquierda": (0, -1), "derecha": (0, 1)}


class Unidad(NamedTuple):
    id: str
    bando: str
    tipo: str
    pos: tuple[int, int]


@dataclass(frozen=True, eq=False)
class Escenario:
    filas: int
    columnas: int
    costos: dict[str, float | None]  # nombre de terreno -> costo; None = no transitable
    terreno: tuple[tuple[str, ...], ...]
    bases: dict[str, tuple[int, int]]  # {"A": (f, c), "B": (f, c)}
    recurso: tuple[int, int]
    unidades: tuple[Unidad, ...]
    turno: str
    portador: str | None
    juego: dict
    prueba: dict | None

    def dentro(self, pos: tuple[int, int]) -> bool:
        f, c = pos
        return 0 <= f < self.filas and 0 <= c < self.columnas

    def transitable(self, pos: tuple[int, int]) -> bool:
        return self.dentro(pos) and self.costos[self.terreno[pos[0]][pos[1]]] is not None

    def costo(self, pos: tuple[int, int]) -> float:
        """Costo de ENTRAR a la celda ``pos``, leído de ``tipos_terreno`` del JSON.

        Purpose: única fuente de costos para todos los algoritmos (P3).
        Preconditions: ``pos`` es transitable.
        Postconditions: devuelve el costo del JSON (> 0); si el JSON cambia, cambia sin tocar código.
        Complexity: O(1).
        AI usage: Yes
        AI intervention: Claude Code escribió el método.
        Student validation: PENDIENTE: revisar test_costos_desde_json (pantano 7 -> 15).
        """
        return self.costos[self.terreno[pos[0]][pos[1]]]

    def vecinos(self, pos: tuple[int, int], orden=ORDEN_MOVIMIENTOS) -> list[tuple[int, int]]:
        """Celdas transitables alrededor de ``pos`` (4-vecindad), en el orden pedido.

        Purpose: generación básica de sucesores sobre el terreno (búsqueda y reglas del juego).
        Preconditions: ``orden`` solo tiene nombres de ``DIRECCIONES``.
        Postconditions: cada vecino está dentro del mapa y es transitable; se respeta ``orden``.
        Complexity: O(4).
        AI usage: Yes
        AI intervention: Claude Code adaptó ``sucesores_laberinto`` del notebook de BFS/DFS.
        Student validation: PENDIENTE: revisar test_vecinos_orden.
        """
        f, c = pos
        resultado = []
        for nombre in orden:
            df, dc = DIRECCIONES[nombre]
            nuevo = (f + df, c + dc)
            if self.transitable(nuevo):
                resultado.append(nuevo)
        return resultado

    def costo_minimo(self) -> float:
        """Menor costo entre los terrenos transitables del mapa (c_min, para las heurísticas)."""
        return min((self.costos[t] for fila in self.terreno for t in fila if self.costos[t] is not None), default=0)
