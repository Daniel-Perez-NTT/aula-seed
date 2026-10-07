from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def metadatos(cuerpo: str) -> tuple[str, list[str]]:
    spec = re.search(r"^AULA_SPEC_ID:\s*(SPEC-\d+)$", cuerpo, re.M)
    criterios = re.search(r"^AULA_CRITERIOS:\s*(.+)$", cuerpo, re.M)
    if not spec or not criterios:
        raise ValueError("el cuerpo del PR debe incluir AULA_SPEC_ID y AULA_CRITERIOS")
    valores = re.findall(r"(?:CA|INV)-\d{2}", criterios.group(1))
    if not valores:
        raise ValueError("AULA_CRITERIOS debe declarar al menos un criterio")
    return spec.group(1), valores


def archivos(base: str) -> list[dict]:
    rutas = subprocess.check_output(
        ["git", "diff", "--name-only", f"{base}...HEAD"], cwd=RAIZ, text=True
    ).splitlines()
    salida = []
    for ruta in rutas:
        fichero = RAIZ / ruta
        if fichero.is_file() and fichero.suffix in {".py", ".md"}:
            salida.append({"ruta": ruta, "contenido": fichero.read_text(encoding="utf-8")})
    return salida


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--cuerpo", required=True)
    parser.add_argument("--salida", default=".conformidad-pr.json")
    args = parser.parse_args(argv)
    try:
        spec, criterios = metadatos(Path(args.cuerpo).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    entrada = {"id": "pr", "ficheros": archivos(args.base), "criterios_declarados": criterios}
    Path(args.salida).write_text(json.dumps(entrada, ensure_ascii=False), encoding="utf-8")
    from agentes.conformidad.agente import principal

    return principal(["--pr", args.salida, "--spec", spec, "--json"])


if __name__ == "__main__":
    raise SystemExit(main())
