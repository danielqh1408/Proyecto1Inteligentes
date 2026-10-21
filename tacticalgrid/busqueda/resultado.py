"""Resultado de una búsqueda con las métricas del enunciado (definiciones en spec 003 §3)."""

from __future__ import annotations

from dataclasses import dataclass, field


def posicion(s) -> tuple[int, int]:
    """Celda de un estado: el propio estado en navegación, s[0] en la misión ((f, c), lleva)."""
    return s if isinstance(s[0], int) else s[0]


@dataclass
class Resultado:
    algoritmo: str
    exito: bool = False
    camino: list = field(default_factory=list)          # estados desde el inicio hasta el objetivo
    costo: float = 0
    estados_generados: int = 0                          # inserciones en la frontera (incluye el inicio)
    estados_expandidos: int = 0                         # estados sacados cuyos sucesores se calcularon
    maximo_frontera: int = 0                            # mayor tamaño de la frontera
    tiempo_ms: float = 0
    preparacion_ms: float = 0                          # construcción de la heurística
    orden_expansion: list = field(default_factory=list) # para dibujar los explorados en la GUI
    extra: dict = field(default_factory=dict)           # heuristica, k, descartados...

    @property
    def longitud(self) -> int:
        return max(len(self.camino) - 1, 0)

    def como_dict(self) -> dict:
        """Formato del enunciado (p. 7) + longitud, tiempo y extras."""
        return {
            "algoritmo": self.algoritmo,
            "exito": self.exito,
            "camino": [list(posicion(s)) for s in self.camino],
            "costo": self.costo,
            "longitud": self.longitud,
            "estados_generados": self.estados_generados,
            "estados_expandidos": self.estados_expandidos,
            "maximo_frontera": self.maximo_frontera,
            "tiempo_ms": round(self.tiempo_ms, 3),
            "preparacion_ms": round(self.preparacion_ms, 3),
            "tiempo_total_ms": round(self.tiempo_ms + self.preparacion_ms, 3),
            **self.extra,
        }


def reconstruir(padres: dict, s) -> tuple[list, float]:
    """Camino y costo desde el inicio hasta ``s``. ``padres[x] = (padre, costo de entrar a x)``."""
    camino, costo = [s], 0
    while padres[s] is not None:
        s, c = padres[s][0], padres[s][1]
        costo += c
        camino.append(s)
    camino.reverse()
    return camino, costo
