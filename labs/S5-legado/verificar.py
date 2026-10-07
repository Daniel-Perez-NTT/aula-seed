"""Verificador de S5: Modernizacion del legado con agentes."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from aula_cli.verificacion import (contiene, criterio, ejecutar, existe,
                                   orden_en_historial, prueba_negativa,
                                   pytest_verde)


def verificar():
    c = []
    c.append(criterio("S5-01", "existe la bateria de caracterizacion del legado",
                      existe("tests/test_caracterizacion_legado.py"),
                      "sin caracterizacion no se puede tocar el legado"))

    ok, detalle = orden_en_historial(r"caracteriz", r"^refactor", por_asunto=True)
    c.append(criterio("S5-02",
                      "REGLA DURA: la caracterizacion precede al refactor en el historial",
                      ok is True, detalle))

    c.append(criterio("S5-03", "la caracterizacion captura los comportamientos no documentados",
                      contiene("tests/test_caracterizacion_legado.py", r"no_documentado_1")
                      and contiene("tests/test_caracterizacion_legado.py", r"no_documentado_2"),
                      "faltan los dos comportamientos ocultos: solo se descubren ejecutando"))

    verde, resumen = pytest_verde("tests/test_caracterizacion_legado.py")
    c.append(criterio("S5-04", "la bateria de caracterizacion esta en verde", verde, resumen))

    verde2, resumen2 = pytest_verde("tests/test_equivalencia_legado.py")
    c.append(criterio("S5-05",
                      "equivalencia sobre el corpus sin desviaciones sin justificar",
                      verde2, resumen2))

    c.append(criterio("S5-06", "toda desviacion esta declarada con causa y efecto",
                      existe("src/aula/legado/DESVIACIONES.md")
                      and contiene("src/aula/legado/DESVIACIONES.md", r"D-01")
                      and contiene("src/aula/legado/DESVIACIONES.md", r"aguas abajo"),
                      "falta DESVIACIONES.md o no documenta el efecto aguas abajo"))
    return c


if __name__ == "__main__":
    for x in verificar():
        print(("OK   " if x["ok"] else "FALLA"), x["id"], x["descripcion"], x["detalle"])
