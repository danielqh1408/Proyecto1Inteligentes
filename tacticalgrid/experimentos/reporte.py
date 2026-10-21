"""Experimentos reproducibles (spec 008): ``python -m tacticalgrid experimentos`` regenera resultados/.

Todo es determinista salvo las columnas de tiempo (dependen del computador).
"""

from __future__ import annotations

import csv
import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from time import perf_counter

from tacticalgrid.adversarial.minimax import alfa_beta, minimax
from tacticalgrid.adversarial.partida import jugar, resumen_final
from tacticalgrid.busqueda.algoritmos import beam_search
from tacticalgrid.busqueda.ejecutar import crear_problema, ejecutar_busqueda
from tacticalgrid.busqueda.heuristicas import crear_heuristica
from tacticalgrid.escenario.cargador import cargar_escenario
from tacticalgrid.experimentos.casos import CARPETA, CASOS, cargar
from tacticalgrid.juego.estado import estado_inicial

CASOS_BUSQUEDA = ["caso01_bfs_vs_dfs", "caso02_ruta_corta_vs_economica", "caso03_obstaculo_heuristica",
                  "caso04_comparacion_heuristicas", "caso05_beam", "caso06_estado_compuesto"]
METRICAS = ["exito", "longitud", "costo", "estados_generados", "estados_expandidos", "maximo_frontera", "tiempo_ms", "preparacion_ms", "tiempo_total_ms"]
METRICAS_ADV = ["accion", "valor", "nodos_generados", "nodos_evaluados", "nodos_podados", "evaluaciones_ordenamiento", "evaluaciones_desglose", "evaluaciones_totales", "nodos_generados_totales", "profundidad_alcanzada", "tiempo_ms"]


def _fila(base: dict, datos: dict, columnas: list) -> dict:
    return {**base, **{c: datos.get(c, "") for c in columnas}}


def e1_busqueda():
    """E1: los 5 algoritmos (A* y Beam con las dos heurísticas) en los casos 1 a 6."""
    filas = []
    for caso in CASOS_BUSQUEDA:
        e = cargar(caso)
        for algoritmo, heuristica in [("BFS", ""), ("DFS", ""), ("UCS", ""), ("A_ESTRELLA", "manhattan"),
                                      ("A_ESTRELLA", "obstaculos"), ("BEAM", "manhattan"), ("BEAM", "obstaculos")]:
            r = ejecutar_busqueda(e, algoritmo, heuristica or None, k=2).como_dict()
            filas.append(_fila({"caso": caso, "algoritmo": algoritmo, "heuristica": heuristica,
                                "k": r.get("k", "")}, r, METRICAS))
    return filas


def e2_beam():
    """E2: Beam Search con k = 1, 2, 4, 8, 16 y criterio h o f (casos 3 y 5)."""
    filas = []
    for caso in ("caso03_obstaculo_heuristica", "caso05_beam"):
        e = cargar(caso)
        problema = crear_problema(e)
        for criterio in ("h", "f"):
            for k in (1, 2, 4, 8, 16):
                t0 = perf_counter()
                h = crear_heuristica("manhattan", problema)
                preparacion_ms = (perf_counter() - t0) * 1000
                resultado = beam_search(problema, h, k, criterio)
                resultado.preparacion_ms = preparacion_ms
                r = resultado.como_dict()
                filas.append(_fila({"caso": caso, "k": k, "criterio": criterio, "descartados": r["descartados"]}, r, METRICAS))
    return filas


def e3_sensibilidad():
    """E3: costo del pantano de 1 a 20 en el caso 2 (el ejemplo del profesor: 7 -> 15)."""
    datos = json.loads((CARPETA / "caso02_ruta_corta_vs_economica.json").read_text(encoding="utf-8"))
    filas = []
    for costo in (1, 2, 3, 5, 7, 10, 15, 20):
        datos["tipos_terreno"]["pantano"]["costo"] = costo
        e = cargar_escenario(datos)
        for algoritmo, heuristica in [("BFS", None), ("UCS", None), ("A_ESTRELLA", "obstaculos")]:
            r = ejecutar_busqueda(e, algoritmo, heuristica).como_dict()
            filas.append(_fila({"costo_pantano": costo, "algoritmo": algoritmo}, r, METRICAS))
    return filas


def e4_profundidad():
    """E4: Minimax vs alfa-beta con profundidad 1 a 5 en el estado del caso 8 (Minimax hasta 4)."""
    e = cargar("caso08_minimax_vs_alfabeta")
    s = estado_inicial(e)
    filas = []
    for p in (1, 2, 3, 4, 5):
        for funcion in ((minimax, alfa_beta) if p <= 4 else (alfa_beta,)):
            d = funcion(e, s, p)
            filas.append(_fila({"profundidad": p, "algoritmo": d.algoritmo}, d.como_dict(), METRICAS_ADV))
    return filas


def e5_orden():
    """E5: efecto del orden de generación de acciones en la poda (caso 9)."""
    e = cargar("caso09_orden_acciones")
    s = estado_inicial(e)
    filas = []
    for p in (2, 3, 4):
        for orden in ("natural", "inverso", "heuristico"):
            d = alfa_beta(e, s, p, orden)
            filas.append(_fila({"profundidad": p, "orden": orden}, d.como_dict(), METRICAS_ADV))
    return filas


def e6_torneo():
    """E6: partidas completas en un mapa simétrico entre agentes con distinta profundidad."""
    e = cargar_escenario(CARPETA.parent / "partida_simetrica.json")
    enfrentamientos = [("VORAZ", 1, "VORAZ", 1), ("ALFA_BETA", 3, "VORAZ", 1), ("VORAZ", 1, "ALFA_BETA", 3),
                       ("ALFA_BETA", 1, "ALFA_BETA", 3), ("ALFA_BETA", 3, "ALFA_BETA", 1), ("ALFA_BETA", 3, "ALFA_BETA", 3)]
    filas = []
    for agente_a, prof_a, agente_b, prof_b in enfrentamientos:
        final, historial = jugar(e, {"A": agente_a, "B": agente_b}, {"A": prof_a, "B": prof_b})
        filas.append({"agente_A": f"{agente_a}({prof_a})", "agente_B": f"{agente_b}({prof_b})",
                      "resultado": resumen_final(e, final), "jugadas": len(historial),
                      "intercepciones": sum("intercepta" in accion for _, _, accion, _ in historial)})
    return filas


EXPERIMENTOS = {"E1_busqueda": e1_busqueda, "E2_beam": e2_beam, "E3_sensibilidad": e3_sensibilidad,
                "E4_profundidad": e4_profundidad, "E5_orden": e5_orden, "E6_torneo": e6_torneo}


def _markdown(filas: list[dict]) -> str:
    if not filas:
        return ""
    columnas = list(dict.fromkeys(c for f in filas for c in f))  # todas las columnas, en orden de aparición
    lineas = ["| " + " | ".join(columnas) + " |", "|" + "---|" * len(columnas)]
    lineas += ["| " + " | ".join(str(f.get(c, "")) for c in columnas) + " |" for f in filas]
    return "\n".join(lineas)


def generar(salida: Path) -> bool:
    """Ejecuta los 10 casos y los experimentos E1-E6; escribe CSV y RESUMEN.md en ``salida``.
    Devuelve True si los 10 casos cumplen lo esperado."""
    salida.mkdir(parents=True, exist_ok=True)
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        if subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip():
            commit += " + cambios locales"
    except OSError:
        commit = "?"
    partes = [
        "# Resultados de los experimentos",
        f"Generado: {datetime.now():%Y-%m-%d %H:%M} · commit `{commit or '?'}` · Python {platform.python_version()}",
        "Regenerar con: `python -m tacticalgrid experimentos`. Todo es determinista salvo las columnas de tiempo. tiempo_total_ms = tiempo_ms + preparacion_ms; incluye preparar la heurística, no cargar el JSON. Las evaluaciones totales incluyen hojas, ordenamiento y desglose del hijo elegido.",
        "## Casos mínimos del enunciado (esperado vs obtenido)",
    ]
    todos_ok = True
    for nombre, funcion in CASOS.items():
        ok, filas = funcion()
        todos_ok &= ok
        datos = json.loads(next(CARPETA.glob(f"{nombre}_*.json")).read_text(encoding="utf-8"))
        filas = [{k: v for k, v in f.items() if k != "camino"} for f in filas]
        partes += [f"### {'✔' if ok else '✘'} {datos['descripcion']}", f"**Esperado:** {datos['esperado']}", _markdown(filas)]
    for nombre, funcion in EXPERIMENTOS.items():
        filas = funcion()
        with open(salida / f"{nombre}.csv", "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]), lineterminator="\n")
            escritor.writeheader()
            escritor.writerows(filas)
        partes += [f"## {nombre} — {funcion.__doc__.strip()}", f"Archivo: `{nombre}.csv`", _markdown(filas)]
    (salida / "RESUMEN.md").write_text("\n\n".join(partes) + "\n", encoding="utf-8")
    return todos_ok
