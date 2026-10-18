"""Línea de comandos: python -m tacticalgrid <comando> ...  (ver README)."""

import argparse
import json
import sys

from tacticalgrid.adversarial.partida import AGENTES, decidir_con, jugar, resumen_final
from tacticalgrid.busqueda.ejecutar import ALGORITMOS, crear_problema, ejecutar_busqueda
from tacticalgrid.escenario.cargador import EscenarioInvalido, cargar_escenario
from tacticalgrid.juego.estado import estado_inicial
from tacticalgrid.verificacion import verificador

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
    problema = crear_problema(e, **opciones_problema(args))
    r = ejecutar_busqueda(e, args.algoritmo, args.heuristica, args.k, problema=problema)
    print(json.dumps(r.como_dict(), ensure_ascii=False))
    if args.verificar:
        print("Verificación:\n" + verificador.texto(verificador.verificar_camino(e, problema, r)))
    return 0


def comando_comparar(args) -> int:
    e = cargar_escenario(args.ruta)
    opciones = opciones_problema(args)
    filas = [ejecutar_busqueda(e, a, **opciones).como_dict() for a in ("BFS", "DFS", "UCS")]
    filas += [ejecutar_busqueda(e, "A_ESTRELLA", h, **opciones).como_dict() for h in ("manhattan", "obstaculos")]
    filas += [ejecutar_busqueda(e, "BEAM", args.heuristica, k, **opciones).como_dict() for k in (1, 2, 4, 8)]
    print(tabla(filas))
    return 0


def comando_decidir(args) -> int:
    e = cargar_escenario(args.ruta)
    agente = args.algoritmo or (e.prueba or {}).get("algoritmo", "ALFA_BETA")
    estado = estado_inicial(e)
    d = decidir_con(agente.upper(), e, estado, args.profundidad, args.orden)
    datos = d.como_dict()
    raiz = datos.pop("valores_raiz")
    print(json.dumps(datos, ensure_ascii=False))
    print("Valor Minimax de cada acción de la raíz (en alfa-beta, las no elegidas pueden ser cotas):")
    for accion, valor in raiz:
        print(f"  {accion:24} {valor}")
    if args.verificar:
        chequeos = verificador.verificar_decision(e, estado, d)
        chequeos += verificador.verificar_minimax_vs_alfabeta(e, estado, args.profundidad, args.orden)
        print("Verificación:\n" + verificador.texto(chequeos))
    return 0


def comando_partida(args) -> int:
    e = cargar_escenario(args.ruta)
    final, historial = jugar(e, {"A": args.a, "B": args.b}, {"A": args.profundidad, "B": args.profundidad}, args.max_jugadas)
    for turno, bando, accion, valor in historial:
        print(f"{turno:4} {bando}  {accion:24} valor={valor}")
    print(resumen_final(e, final))
    return 0


def comando_ejecutar(args) -> int:
    """Hace lo que pida prueba.modo del JSON (busqueda, adversarial o partida)."""
    e = cargar_escenario(args.ruta)
    modo = (e.prueba or {}).get("modo", "partida")
    base = argparse.Namespace(ruta=args.ruta, algoritmo=None, heuristica=None, k=None, unidad=None, objetivo=None,
                              orden=None, mision=False, profundidad=None, a="ALFA_BETA", b="ALFA_BETA", max_jugadas=None,
                              verificar=True)
    print(f"prueba.modo = {modo}")
    if modo == "busqueda":
        return comando_buscar(base)
    if modo == "adversarial":
        return comando_decidir(base)
    return comando_partida(base)


def comando_experimentos(args) -> int:
    from pathlib import Path

    from tacticalgrid.experimentos.reporte import generar

    ok = generar(Path(args.salida))
    print(f"Resultados en {args.salida}/ (RESUMEN.md y CSV). Casos mínimos: {'todos ✔' if ok else 'hay casos ✘'}")
    return 0 if ok else 1


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
        p.add_argument("--verificar", action="store_true", help="verifica el camino obtenido (spec 006)")
        p.set_defaults(funcion=funcion)

    p = comandos.add_parser("decidir", help="mejor acción para el bando en turno (Minimax / alfa-beta / voraz)")
    p.add_argument("ruta")
    p.add_argument("--algoritmo", type=str.upper, choices=AGENTES, help="por defecto prueba.algoritmo o ALFA_BETA")
    p.add_argument("--profundidad", type=int, help="por defecto juego.profundidad_maxima_minimax")
    p.add_argument("--orden", choices=("natural", "inverso", "heuristico"), help="orden de generación de acciones")
    p.add_argument("--verificar", action="store_true", help="verifica legalidad y compara Minimax con alfa-beta (spec 006)")
    p.set_defaults(funcion=comando_decidir)

    p = comandos.add_parser("partida", help="juega una partida completa entre dos agentes")
    p.add_argument("ruta")
    p.add_argument("--a", type=str.upper, choices=AGENTES, default="ALFA_BETA", help="agente del bando A")
    p.add_argument("--b", type=str.upper, choices=AGENTES, default="ALFA_BETA", help="agente del bando B")
    p.add_argument("--profundidad", type=int, help="profundidad de Minimax/alfa-beta para ambos")
    p.add_argument("--max-jugadas", type=int, dest="max_jugadas")
    p.set_defaults(funcion=comando_partida)

    p = comandos.add_parser("ejecutar", help="ejecuta lo que pida prueba.modo del JSON")
    p.add_argument("ruta")
    p.set_defaults(funcion=comando_ejecutar)

    p = comandos.add_parser("experimentos", help="ejecuta los 10 casos y los experimentos E1-E6 (resultados/)")
    p.add_argument("--salida", default="resultados")
    p.set_defaults(funcion=comando_experimentos)

    args = parser.parse_args(argv)
    try:
        return args.funcion(args)
    except EscenarioInvalido as error:
        print(error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
