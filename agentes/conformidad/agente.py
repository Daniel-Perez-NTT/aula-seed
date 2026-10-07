"""Agente v0: punto de partida deliberadamente ingenuo para S4a."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

CONFORME = "conforme"
NO_CONFORME = "no_conforme"


@dataclass
class Veredicto:
    pr: str
    spec: str
    veredicto: str
    criterios_declarados: list = field(default_factory=list)
    criterios_cubiertos: list = field(default_factory=list)
    criterios_sin_cubrir: list = field(default_factory=list)
    fuera_de_alcance: list = field(default_factory=list)
    hallazgos: list = field(default_factory=list)
    explicacion: str = ""

    def a_dict(self):
        return asdict(self)


def evaluar(pr: dict, spec_id: str, juez=None) -> Veredicto:
    tests = [fichero for fichero in pr["ficheros"]
             if fichero["ruta"].startswith("tests/")]
    menciona = any(re.search(re.escape(spec_id), fichero["contenido"])
                   for fichero in tests)
    resultado = CONFORME if tests and menciona else NO_CONFORME
    return Veredicto(
        pr=pr.get("id", "sin-id"), spec=spec_id, veredicto=resultado,
        criterios_declarados=pr.get("criterios_declarados", []),
        explicacion="hay tests que mencionan la spec" if resultado == CONFORME
        else "no hay tests que mencionen la spec")


def principal(argv=None):
    parser = argparse.ArgumentParser(description="Agente de conformidad v0")
    parser.add_argument("--pr", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    entrada = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    veredicto = evaluar(entrada, args.spec)
    if args.json:
        print(json.dumps(veredicto.a_dict(), ensure_ascii=False, indent=2))
    else:
        print(veredicto.veredicto + ": " + veredicto.explicacion)
    return 1 if veredicto.veredicto == NO_CONFORME else 0


if __name__ == "__main__":
    raise SystemExit(principal())