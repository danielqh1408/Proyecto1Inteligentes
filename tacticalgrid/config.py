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
PESOS_UTILIDAD = {"posesion": 50, "carrera": 3, "movilidad": 0.1}

# Valor de ganar (mayor que cualquier evaluación de un estado no terminal).
VALOR_VICTORIA = 10_000
