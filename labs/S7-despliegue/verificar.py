"""Verificador de S7: Despliegue, fallo inducido y MTTR."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from aula_cli.verificacion import (contiene, criterio, ejecutar, existe,
                                   orden_en_historial, prueba_negativa,
                                   pytest_verde)


def verificar():
    c = []
    c.append(criterio("S7-01", "el pipeline tiene etapa de despliegue",
                      contiene(".github/workflows/ci.yml", r"deploy|despliegue"),
                      "no hay etapa de despliegue"))
    c.append(criterio("S7-02", "existe procedimiento de reversion documentado",
                      existe("labs/S7-despliegue/reversion.md"),
                      "un despliegue sin reversion probada no es un despliegue"))
    c.append(criterio("S7-03", "hay registro de MTTR de las dos rondas",
                      existe("labs/S7-despliegue/mttr.md")
                      and contiene("labs/S7-despliegue/mttr.md", r"ronda 2|Ronda 2"),
                      "faltan las dos rondas, sin agente y con agente"))
    c.append(criterio("S7-04", "la retrospectiva incluye la hipotesis inicial y la causa real",
                      contiene("labs/S7-despliegue/mttr.md", r"hip[oó]tesis"),
                      "comparar hipotesis y causa real es lo que ensena a diagnosticar"))
    c.append(criterio("S7-05", "hay observabilidad instrumentada",
                      contiene("src/aula/api/app.py", r"log|trace|metric")
                      or existe("src/aula/observabilidad.py"),
                      "sin instrumentacion no se puede medir nada"))
    return c


if __name__ == "__main__":
    for x in verificar():
        print(("OK   " if x["ok"] else "FALLA"), x["id"], x["descripcion"], x["detalle"])
