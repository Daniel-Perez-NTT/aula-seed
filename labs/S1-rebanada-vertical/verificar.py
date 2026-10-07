"""Verificador de S1: Rebanada vertical a mano."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from aula_cli.verificacion import (contiene, criterio, ejecutar, existe,
                                   orden_en_historial, prueba_negativa,
                                   pytest_verde)


def verificar():
    c = []
    verde, resumen = pytest_verde()
    c.append(criterio("S1-01", "la suite esta en verde", verde, resumen))
    c.append(criterio("S1-02", "existe el modulo de dominio con la maquina de estados",
                      existe("src/aula/dominio/estados.py")
                      and contiene("src/aula/dominio/estados.py", r"TRANSICIONES"),
                      "falta la maquina de estados de la matricula"))
    c.append(criterio("S1-03", "existe Containerfile o Dockerfile multi-stage",
                      (existe("Containerfile") or existe("Dockerfile"))
                      and (contiene("Containerfile", r"(?s)FROM.*FROM")
                           or contiene("Dockerfile", r"(?s)FROM.*FROM")),
                      "no hay imagen OCI, o no usa construccion multi-stage"))
    c.append(criterio("S1-04", "el pipeline construye la imagen",
                      contiene(".github/workflows/ci.yml", r"build.*imagen|podman build|docker build|buildah"),
                      "el workflow no construye la imagen"))
    p = ejecutar([sys.executable, "-m", "pytest", "tests/", "-q", "--no-header"])
    c.append(criterio("S1-05", "hay al menos 15 tests propios",
                      "passed" in p.stdout and int(p.stdout.split("passed")[0].split()[-1]) >= 15,
                      p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""))
    c.append(criterio("S1-06", "la bitacora registra el tiempo por tarea",
                      contiene("labs/S1-rebanada-vertical/bitacora.md", r"20\d\d-"),
                      "sin registro de tiempos no hay linea base para medir el salto en S2 y S3",
                      nivel="V1"))
    return c


if __name__ == "__main__":
    for x in verificar():
        print(("OK   " if x["ok"] else "FALLA"), x["id"], x["descripcion"], x["detalle"])
