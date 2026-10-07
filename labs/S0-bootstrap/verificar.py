"""Verificador de S0: Bootstrap y disciplina de repositorio."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from aula_cli.verificacion import (contiene, criterio, ejecutar, existe,
                                   orden_en_historial, prueba_negativa,
                                   pytest_verde)


def verificar():
    c = []
    c.append(criterio("S0-01", "existe la plantilla de PR con la checklist",
                      existe(".github/pull_request_template.md")
                      and contiene(".github/pull_request_template.md", r"defenderlo ante el cliente"),
                      "falta .github/pull_request_template.md o no lleva la checklist de nueve puntos"))
    c.append(criterio("S0-02", "existe CODEOWNERS y protege labs, manifiestos y workflows",
                      existe(".github/CODEOWNERS")
                      and contiene(".github/CODEOWNERS", r"labs/")
                      and contiene(".github/CODEOWNERS", r"manifiestos/"),
                      "CODEOWNERS no cubre las rutas que el contrato de contexto declara prohibidas"))
    c.append(criterio("S0-03", "el pipeline incluye el gate de tamano de PR",
                      contiene(".github/workflows/ci.yml", r"tamano-pr|LIMITE_LINEAS"),
                      "no hay job que limite el tamano del diff"))
    c.append(criterio("S0-04", "el pipeline exige tests en verde para mergear",
                      contiene(".github/workflows/ci.yml", r"pytest"),
                      "el workflow no ejecuta la suite"))
    p = ejecutar(["git", "log", "--oneline"])
    commits = len(p.stdout.strip().splitlines()) if p.returncode == 0 else 0
    c.append(criterio("S0-05", "hay historial de git con al menos dos commits",
                      commits >= 2, "commits encontrados: %d" % commits))
    return c


if __name__ == "__main__":
    for x in verificar():
        print(("OK   " if x["ok"] else "FALLA"), x["id"], x["descripcion"], x["detalle"])
