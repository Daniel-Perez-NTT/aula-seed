"""Verificador de S2: Spec-Driven Development."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from aula_cli.verificacion import (contiene, criterio, existe,
                                   mutar_y_exigir_fallo, pytest_verde)
from agentes.mcp_aula.servidor import listar_specs, trazabilidad


def verificar():
    c = []
    specs = listar_specs()["specs"]
    activas = [s for s in specs if s["estado"] == "activa"]

    c.append(criterio("S2-01", "existen specs activas en specs/", bool(activas),
                      "no se encuentra ninguna spec en estado activa"))

    for s in activas:
        t = trazabilidad({"spec_id": s["id"]})
        c.append(criterio(
            "S2-02:%s" % s["id"],
            "%s: todos los criterios tienen test que los referencia" % s["id"],
            t["cobertura_pct"] == 100.0,
            "sin cubrir: %s" % ", ".join(t["sin_cubrir"])))

    obligatorios = ["## Invariantes", "## Criterios de aceptación", "## Casos límite",
                    "## Fuera de alcance", "## Ambigüedades detectadas"]
    for s in activas:
        faltan = [o for o in obligatorios if not contiene(s["ruta"], o)]
        c.append(criterio("S2-03:%s" % s["id"],
                          "%s tiene los apartados obligatorios de la plantilla" % s["id"],
                          not faltan, "faltan: %s" % ", ".join(faltan)))

    # La ambiguedad plantada tiene que estar registrada y resuelta, no solo detectada.
    resuelta = contiene("specs/SPEC-002-expediente.md", r"A-0[12].*?convalidada")
    c.append(criterio("S2-04",
                      "la ambiguedad de la spec de partida esta registrada y resuelta",
                      resuelta,
                      "el apartado de ambiguedades no documenta el tratamiento de "
                      "repetidas y convalidadas", nivel="V1"))

    verde, resumen = pytest_verde()
    c.append(criterio("S2-05", "la suite completa esta en verde", verde, resumen))

    ok, detalle = mutar_y_exigir_fallo("src/aula/reglas/media.py",
                                       "tests/test_media_expediente.py")
    c.append(criterio("S2-06",
                      "los tests fallan al mutar la implementacion (no son decorativos)",
                      ok, detalle))
    return c


if __name__ == "__main__":
    for x in verificar():
        print(("OK   " if x["ok"] else "FALLA"), x["id"], x["descripcion"], x["detalle"])
