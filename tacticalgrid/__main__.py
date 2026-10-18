"""Línea de comandos: python -m tacticalgrid <comando> ..."""

import argparse
import sys

from tacticalgrid.escenario.cargador import EscenarioInvalido, cargar_escenario


def validar(rutas: list[str]) -> int:
    codigo = 0
    for ruta in rutas:
        try:
            e = cargar_escenario(ruta)
            print(f"✔ {ruta}: válido ({e.filas}x{e.columnas}, {len(e.unidades)} unidades)")
        except EscenarioInvalido as error:
            print(f"✘ {ruta}:")
            for mensaje in error.errores:
                print(f"    {mensaje}")
            codigo = 1
    return codigo


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="tacticalgrid")
    comandos = parser.add_subparsers(dest="comando", required=True)
    comandos.add_parser("validar", help="valida uno o varios escenarios JSON").add_argument("rutas", nargs="+")
    args = parser.parse_args(argv)
    if args.comando == "validar":
        return validar(args.rutas)
    return 0


if __name__ == "__main__":
    sys.exit(main())
