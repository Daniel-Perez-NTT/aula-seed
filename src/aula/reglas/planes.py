"""Carga de planes de estudio versionados."""
from __future__ import annotations

import json
from pathlib import Path

from ..dominio.modelos import Asignatura, Plan

RUTA_PLANES = Path(__file__).resolve().parents[3] / "datos" / "planes"


def cargar_plan(codigo: str, ruta: Path = None) -> Plan:
    base = ruta or RUTA_PLANES
    datos = json.loads((base / ("%s.json" % codigo)).read_text(encoding="utf-8"))
    asignaturas = {
        a["codigo"]: Asignatura(
            codigo=a["codigo"], nombre=a["nombre"], creditos=a["creditos"],
            curso=a["curso"], prerrequisitos=tuple(a.get("prerrequisitos", [])),
        )
        for a in datos["asignaturas"]
    }
    return Plan(
        codigo=datos["codigo"], version=datos["version"],
        creditos_titulo=datos["creditos_titulo"],
        limite_creditos_curso=datos["limite_creditos_curso"],
        max_convocatorias=datos["max_convocatorias"],
        umbral_final_carrera=datos["umbral_final_carrera"],
        asignaturas=asignaturas,
    )
