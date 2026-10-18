"""Línea de comandos: python -m tacticalgrid <comando> ...  (ver README)."""

import argparse
import json
import sys

from tacticalgrid.busqueda.ejecutar import ALGORITMOS, ejecutar_busqueda
from tacticalgrid.escenario.cargador import EscenarioInvalido, cargar_escenario

COLUMNAS = ("algoritmo", "heuristica", "k", "exito", "longitud", "costo",
            "estados_generados", "estados_expandidos", "maximo_frontera", "tiempo_ms")


def tabla(filas: list[dict]) -> str:
    """Tabla de texto con las métricas de varias ejecuciones (para comparar algoritmos)."""
    datos = [[str(f.get(c, "")) for c in COLUMNAS] for f in filas]
    anchos = [max(len(c), *(len(d[i]) for d in datos)) for i, c in enumerate(COLUMNAS)]
    linea = lambda valores: "  ".join(v.ljust(a) for v, a in zip(valores, anchos))
    return "\n".join([linea(COLUMNAS), linea(["-" * a for a in anchos])] + [linea(d) for d in datos])


def comando_validar(args) -> int:
    codigo = 0
    for ruta in args.rutas:
        try:
            e = cargar_escenario(ruta)
            print(f"✔ {ruta}: válido ({e.filas}x{e.columnas}, {len(e.unidades)} unidades)")
        except EscenarioInvalido as error:
            print(f"✘ {ruta}:")
            for mensaje in error.errores:
                print(f"    {mensaje}")
            codigo = 1
    return codigo


def opciones_problema(args) -> dict:
    opciones = {"unidad": args.unidad, "mision": True if args.mision else None}
    if args.objetivo:
        opciones["objetivo"] = tuple(int(x) for x in args.objetivo.split(","))
    if args.orden:
        opciones["orden"] = tuple(args.orden.split(","))
    return opciones


def comando_buscar(args) -> int:
    e = cargar_escenario(args.ruta)
    r = ejecutar_busqueda(e, args.algoritmo, args.heuristica, args.k, **opciones_problema(args))
    print(json.dumps(r.como_dict(), ensure_ascii=False))
    return 0


def comando_comparar(args) -> int:
    e = cargar_escenario(args.ruta)
    opciones = opciones_problema(args)
    filas = [ejecutar_busqueda(e, a, **opciones).como_dict() for a in ("BFS", "DFS", "UCS")]
    filas += [ejecutar_busqueda(e, "A_ESTRELLA", h, **opciones).como_dict() for h in ("manhattan", "obstaculos")]
    filas += [ejecutar_busqueda(e, "BEAM", args.heuristica, k, **opciones).como_dict() for k in (1, 2, 4, 8)]
    print(tabla(filas))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="tacticalgrid", description="TacticalGrid — Sistemas Inteligentes I")
    comandos = parser.add_subparsers(dest="comando", required=True)

    p = comandos.add_parser("validar", help="valida uno o varios escenarios JSON")
    p.add_argument("rutas", nargs="+")
    p.set_defaults(funcion=comando_validar)

    for nombre, funcion, ayuda in (("buscar", comando_buscar, "ejecuta un algoritmo de búsqueda (resultado en JSON)"),
                                   ("comparar", comando_comparar, "tabla con BFS, DFS, UCS, A* (2 heurísticas) y Beam k=1,2,4,8")):
        p = comandos.add_parser(nombre, help=ayuda)
        p.add_argument("ruta")
        p.add_argument("--algoritmo", choices=ALGORITMOS, help="por defecto: prueba.algoritmo del JSON o BFS")
        p.add_argument("--heuristica", choices=("manhattan", "obstaculos", "manhattan_promedio", "cero"))
        p.add_argument("--k", type=int, help="ancho del haz de Beam Search")
        p.add_argument("--unidad", help="unidad que se mueve (por defecto prueba.unidad_inicio)")
        p.add_argument("--objetivo", help="celda objetivo 'fila,columna' (por defecto prueba.objetivo)")
        p.add_argument("--orden", help="orden de movimientos, p. ej. 'arriba,abajo,izquierda,derecha'")
        p.add_argument("--mision", action="store_true", help="recoger el recurso y llevarlo a la base (estado compuesto)")
        p.set_defaults(funcion=funcion)

    args = parser.parse_args(argv)
    try:
        return args.funcion(args)
    except EscenarioInvalido as error:
        print(error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
