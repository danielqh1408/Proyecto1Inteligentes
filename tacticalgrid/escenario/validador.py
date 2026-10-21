"""Validación del JSON común de escenarios (spec 001). Reglas del enunciado (p. 7):

R1 filas/columnas positivas y consistentes con la matriz · R2 terrenos existen en tipos_terreno ·
R3 terrenos transitables con costo > 0 · R4 bases, recurso y unidades dentro del mapa ·
R5 ninguna unidad sobre celda no transitable · R6 ids únicos · R7 unidades de A o B ·
R8 turno A o B · R9 portador_recurso null o unidad existente.
Extras: E00 campo ausente o de tipo incorrecto · R10 dos unidades en la misma celda.
"""

from __future__ import annotations

import math

from tacticalgrid.config import ORDEN_MOVIMIENTOS, PESOS_UTILIDAD

OBLIGATORIOS = ("version", "mapa", "tipos_terreno", "terreno", "bases", "recurso", "unidades", "turno", "juego")
BANDOS = ("A", "B")


def _entero(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)  # True no debe valer como 1


def _pos(obj) -> tuple[int, int] | None:
    """(fila, columna) si ``obj`` es {"fila": entero, "columna": entero}; si no, None."""
    if isinstance(obj, dict) and _entero(obj.get("fila")) and _entero(obj.get("columna")):
        return (obj["fila"], obj["columna"])
    return None


def validar(datos) -> list[str]:
    """Devuelve la lista de errores del escenario (vacía si es válido).

    Purpose: rechazar escenarios que violen el contrato antes de usarlos, explicando cada error.
    Preconditions: ``datos`` es lo que devolvió ``json.load`` (de cualquier tipo).
    Postconditions: un mensaje "[código] campo: explicación" por cada violación encontrada;
        nunca lanza excepción ni modifica ``datos``. Si faltan campos o las dimensiones son
        inválidas se detiene ahí, porque el resto de reglas no se puede comprobar.
    Complexity: O(F·C + U) con F·C celdas y U unidades.
    AI usage: Yes
    AI intervention: Claude Code escribió la función siguiendo la lista de reglas del PDF.
    Student validation: pruebas tests/test_validador.py (14 JSON inválidos, uno por regla de la p. 7 del PDF), en verde.
        Revisado por Daniel Quintero (20 oct: código, pytest y GUI; ver docs/USO_IA.md)
        Revisión humana de las correcciones de Codex por realizar; ver docs/USO_IA.md.
    """
    if not isinstance(datos, dict):
        return ["[E00] el escenario debe ser un objeto JSON {...}"]
    errores = [f"[E00] {campo}: campo obligatorio ausente" for campo in OBLIGATORIOS if campo not in datos]
    if errores:
        return errores

    # R1: dimensiones y forma de la matriz
    mapa = datos["mapa"] if isinstance(datos["mapa"], dict) else {}
    filas, columnas = mapa.get("filas"), mapa.get("columnas")
    if not (_entero(filas) and filas > 0 and _entero(columnas) and columnas > 0):
        return [f"[R1] mapa: filas y columnas deben ser enteros positivos (recibido {filas!r} x {columnas!r})"]
    terreno = datos["terreno"]
    if not (isinstance(terreno, list) and len(terreno) == filas
            and all(isinstance(fila, list) and len(fila) == columnas for fila in terreno)):
        return [f"[R1] terreno: la matriz debe tener {filas} filas de {columnas} columnas"]

    # R3: catálogo de terrenos
    tipos = datos["tipos_terreno"] if isinstance(datos["tipos_terreno"], dict) else {}
    costos = {}
    for nombre, t in tipos.items():
        if not isinstance(t, dict) or not isinstance(t.get("transitable"), bool):
            errores.append(f"[E00] tipos_terreno.{nombre}: 'transitable' debe ser true o false")
            continue
        costo = t.get("costo")
        if t["transitable"] and not (isinstance(costo, (int, float)) and not isinstance(costo, bool)
                                     and math.isfinite(costo) and costo > 0):
            errores.append(f"[R3] tipos_terreno.{nombre}: es transitable y su costo {costo!r} no es > 0")
            continue
        costos[nombre] = costo if t["transitable"] else None

    # R2: cada celda usa un terreno del catálogo
    for f, fila in enumerate(terreno):
        for c, nombre in enumerate(fila):
            if not (isinstance(nombre, str) and nombre in tipos):
                errores.append(f"[R2] terreno[{f}][{c}]: {nombre!r} no existe en tipos_terreno")

    def revisar_pos(obj, campo):
        pos = _pos(obj)
        if pos is None:
            errores.append(f'[E00] {campo}: debe ser {{"fila": entero, "columna": entero}}')
        elif not (0 <= pos[0] < filas and 0 <= pos[1] < columnas):
            errores.append(f"[R4] {campo}: {pos} está fuera del mapa {filas}x{columnas}")
            pos = None
        return pos

    # R4: bases y recurso
    bases = datos["bases"] if isinstance(datos["bases"], dict) else {}
    for bando in BANDOS:
        revisar_pos(bases.get(bando), f"bases.{bando}")
    revisar_pos(datos["recurso"], "recurso")

    # R4-R7 y R10: unidades
    if not isinstance(datos["unidades"], list):
        errores.append("[E00] unidades: debe ser una lista")
    ids, ocupadas = set(), {}
    for i, u in enumerate(datos["unidades"] if isinstance(datos["unidades"], list) else []):
        if not isinstance(u, dict):
            errores.append(f"[E00] unidades[{i}]: debe ser un objeto")
            continue
        uid = u.get("id")
        if not (isinstance(uid, str) and uid):
            errores.append(f"[E00] unidades[{i}].id: debe ser un texto no vacío")
        elif uid in ids:
            errores.append(f"[R6] unidades[{i}].id: '{uid}' está repetido")
        else:
            ids.add(uid)
        if str(u.get("bando")).upper() not in BANDOS:
            errores.append(f"[R7] unidades[{i}].bando: {u.get('bando')!r} no es A ni B")
        pos = revisar_pos(u, f"unidades[{i}]")
        if pos is None:
            continue
        nombre = terreno[pos[0]][pos[1]]
        if isinstance(nombre, str) and nombre in costos and costos[nombre] is None:
            errores.append(f"[R5] unidades[{i}]: '{uid}' está sobre '{nombre}', que no es transitable")
        if pos in ocupadas:
            errores.append(f"[R10] unidades[{i}]: '{uid}' comparte la celda {pos} con '{ocupadas[pos]}'")
        ocupadas[pos] = uid

    # R8: turno
    if str(datos["turno"]).upper() not in BANDOS:
        errores.append(f"[R8] turno: {datos['turno']!r} no es A ni B")

    # R9: portador del recurso
    juego = datos["juego"] if isinstance(datos["juego"], dict) else {}
    if "portador_recurso" not in juego:
        errores.append("[E00] juego.portador_recurso: campo obligatorio ausente (use null si nadie lo porta)")
    else:
        portador = juego["portador_recurso"]
        if portador is not None and not (isinstance(portador, str) and portador in ids):
            errores.append(f"[R9] juego.portador_recurso: {portador!r} no es una unidad existente")

    # Opciones que la aplicación consume: validar antes de cambiar el escenario activo.
    prueba = datos.get("prueba")
    if prueba is not None and not isinstance(prueba, dict):
        errores.append("[E00] prueba: debe ser un objeto JSON o null")
    prueba = prueba if isinstance(prueba, dict) else {}
    for bloque, nombre, campos in ((juego, "juego", ("profundidad_maxima_minimax", "max_turnos")),
                                    (prueba, "prueba", ("profundidad", "k"))):
        for campo in campos:
            if campo in bloque and not (_entero(bloque[campo]) and bloque[campo] > 0):
                errores.append(f"[E00] {nombre}.{campo}: debe ser un entero positivo")
    if "objetivo" in prueba:
        revisar_pos(prueba["objetivo"], "prueba.objetivo")
    if "unidad_inicio" in prueba and prueba["unidad_inicio"] not in list(ids):
        errores.append("[E00] prueba.unidad_inicio: debe identificar una unidad existente")
    for campo in ("mision", "unidades_bloquean"):
        if campo in prueba and not isinstance(prueba[campo], bool):
            errores.append(f"[E00] prueba.{campo}: debe ser true o false")
    if "orden_movimientos" in prueba:
        orden = prueba["orden_movimientos"]
        if not (isinstance(orden, list) and len(orden) == 4
                and all(isinstance(x, str) for x in orden) and set(orden) == set(ORDEN_MOVIMIENTOS)):
            errores.append("[E00] prueba.orden_movimientos: debe ordenar las cuatro direcciones sin repetir")
    for bloque, campo, permitidos in (
        (prueba, "modo", ("busqueda", "partida", "adversarial")),
        (prueba, "heuristica", ("manhattan", "obstaculos", "manhattan_promedio", "cero")),
        (juego, "orden_acciones", ("natural", "inverso", "heuristico")),
    ):
        if campo in bloque and bloque[campo] not in permitidos:
            errores.append(f"[E00] {campo}: use uno de {', '.join(permitidos)}")
    if "algoritmo" in prueba and not isinstance(prueba["algoritmo"], str):
        errores.append("[E00] prueba.algoritmo: debe ser un texto")
    pesos = juego.get("pesos_utilidad", {})
    if not isinstance(pesos, dict):
        errores.append("[E00] juego.pesos_utilidad: debe ser un objeto JSON")
    else:
        for nombre, peso in pesos.items():
            if nombre in PESOS_UTILIDAD and not (isinstance(peso, (int, float))
                    and not isinstance(peso, bool) and math.isfinite(peso)):
                errores.append(f"[E00] juego.pesos_utilidad.{nombre}: debe ser un número finito")
    return errores
