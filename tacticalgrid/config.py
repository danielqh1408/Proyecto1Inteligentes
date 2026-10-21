"""Valores por defecto (constitución P3). Nunca contiene costos, posiciones ni mapas."""

# Mismo orden de los notebooks de clase: MOVIMIENTOS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
ORDEN_MOVIMIENTOS = ("abajo", "arriba", "derecha", "izquierda")

# Opciones de "juego" que el JSON puede omitir (D-04).
DEFECTOS_JUEGO = {
    "profundidad_maxima_minimax": 3,
    "max_turnos": 200,
    "orden_acciones": "natural",
}

# Pesos de la función de evaluación (spec 005 §4). Se pueden cambiar con juego.pesos_utilidad.
# posesion bajó de 50 a 20 por comentario de Daniel; con 10, 20 o 50 el torneo E6 da el mismo resultado.
PESOS_UTILIDAD = {"posesion": 20, "carrera": 3, "movilidad": 0.1}

# Umbral de victoria: la evaluación no terminal se limita a ±(VALOR_VICTORIA - 1).
VALOR_VICTORIA = 10_000
