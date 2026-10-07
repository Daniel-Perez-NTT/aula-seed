"""Verificador de S4b: Flotilla multiagente."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from aula_cli.verificacion import (contiene, criterio, ejecutar, existe,
                                   orden_en_historial, prueba_negativa,
                                   pytest_verde)


def verificar():
    c = []
    c.append(criterio("S4b-01", "existe el contrato de contexto de la flotilla",
                      existe("agentes/flotilla/contrato.json")
                      or existe("agentes/flotilla/contrato.yaml"),
                      "falta el contrato de contexto compartido"))
    c.append(criterio("S4b-02", "el contrato declara entradas, salidas y resolucion de conflicto",
                      contiene("agentes/flotilla/contrato.json", r"conflicto")
                      or contiene("agentes/flotilla/contrato.yaml", r"conflicto"),
                      "el contrato no dice que pasa cuando dos agentes tocan el mismo fichero"))
    c.append(criterio("S4b-03", "hay tres agentes declarados en la flotilla",
                      contiene("agentes/flotilla/contrato.json", r"triaje")
                      or contiene("agentes/flotilla/contrato.yaml", r"triaje"),
                      "se esperan conformidad, triaje y modernizacion"))
    p = ejecutar(["git", "worktree", "list"])
    c.append(criterio("S4b-04", "se han usado worktrees aislados",
                      p.returncode == 0 and len(p.stdout.strip().splitlines()) >= 2,
                      "worktrees activos: %d" % len(p.stdout.strip().splitlines())))
    c.append(criterio("S4b-05", "existe el diagrama de flotilla",
                      existe("labs/S4b-flotilla/flotilla.md"),
                      "falta el diagrama y la descripcion del handoff"))
    return c


if __name__ == "__main__":
    for x in verificar():
        print(("OK   " if x["ok"] else "FALLA"), x["id"], x["descripcion"], x["detalle"])
