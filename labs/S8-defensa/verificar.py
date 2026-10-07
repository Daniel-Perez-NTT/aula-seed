"""Verificador de S8: Defensa ante panel."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from aula_cli.verificacion import (contiene, criterio, ejecutar, existe,
                                   orden_en_historial, prueba_negativa,
                                   pytest_verde)


def verificar():
    c = []
    c.append(criterio("S8-01", "existe el guion de la defensa con la estructura fija",
                      existe("labs/S8-defensa/defensa.md"),
                      "falta el guion"))
    for seccion, etiqueta in [("problema", "problema"), ("spec", "spec"),
                              ("arquitectura", "arquitectura"), ("m[eé]tricas", "metricas"),
                              ("gobierno", "gobierno"), ("coste", "coste")]:
        c.append(criterio("S8-02:%s" % etiqueta,
                          "la defensa cubre el apartado de %s" % etiqueta,
                          contiene("labs/S8-defensa/defensa.md", seccion),
                          "apartado ausente en el guion"))
    c.append(criterio("S8-03",
                      "incluye la lamina de traduccion del patron a la torre de destino",
                      contiene("labs/S8-defensa/defensa.md", r"traducci[oó]n|torre"),
                      "sin la lamina de traduccion la defensa no esta completa"))
    c.append(criterio("S8-04", "incluye una decision que hoy tomarias distinta",
                      contiene("labs/S8-defensa/defensa.md", r"tomar[ií]a distinta|cambiar[ií]a"),
                      "es el mejor predictor de si aguantas una conversacion tecnica",
                      nivel="V4"))
    return c


if __name__ == "__main__":
    for x in verificar():
        print(("OK   " if x["ok"] else "FALLA"), x["id"], x["descripcion"], x["detalle"])
