"""Hook de rutas prohibidas. Determinista, no negociable con el agente.

Lo innegociable no se pide en lenguaje natural: se hace determinista. Este hook
es lo que convierte la seccion de limites de CLAUDE.md en un control real.
"""
import json
import sys

PROHIBIDAS = ("manifiestos/", ".github/workflows/", "labs/", "evals/dorado",
              "src/aula/legado/")


def main():
    try:
        entrada = json.load(sys.stdin)
    except Exception:
        return 0
    ruta = (entrada.get("tool_input", {}) or {}).get("file_path", "")
    for prohibida in PROHIBIDAS:
        if prohibida in ruta:
            print("bloqueado por hook_rutas: %s esta en la lista de limites de "
                  "CLAUDE.md. Requiere aprobacion humana explicita." % ruta,
                  file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
