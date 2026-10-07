"""Verificador de S6: Gobierno del agente."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from aula_cli.verificacion import (contiene, criterio, ejecutar, existe,
                                   orden_en_historial, prueba_negativa,
                                   pytest_verde)


import hashlib
import json
from datetime import date


def _manifiestos():
    d = RAIZ / "manifiestos"
    return sorted(d.glob("*.yaml")) + sorted(d.glob("*.yml")) if d.exists() else []


def _campo(texto, clave):
    import re
    m = re.search(r"^%s:\s*(.+)$" % clave, texto, re.M)
    return m.group(1).strip() if m else None


def verificar():
    c = []
    manifiestos = _manifiestos()
    c.append(criterio("S6-01", "existe un Agent Release Manifest por agente",
                      len(manifiestos) >= 1,
                      "manifiestos encontrados: %d" % len(manifiestos)))

    obligatorios = ["agente", "version", "propietario_humano", "nivel_autonomia",
                    "herramientas", "evaluacion", "coste", "reversion"]
    for m in manifiestos:
        texto = m.read_text(encoding="utf-8")
        faltan = [o for o in obligatorios if o + ":" not in texto]
        c.append(criterio("S6-02:%s" % m.stem,
                          "%s tiene todos los apartados obligatorios" % m.name,
                          not faltan, "faltan: %s" % ", ".join(faltan)))

        nivel = _campo(texto, "nivel_autonomia")
        c.append(criterio("S6-03:%s" % m.stem,
                          "%s declara nivel de autonomia valido y no N4" % m.name,
                          nivel in ("N0", "N1", "N2", "N3"),
                          "nivel declarado: %s. N4 esta fuera del laboratorio" % nivel))

        fecha = _campo(texto, "  fecha") or _campo(texto, "fecha")
        vigente = False
        if fecha:
            try:
                dias = (date.today() - date.fromisoformat(fecha)).days
                vigente = dias <= 30
            except ValueError:
                dias = None
        c.append(criterio("S6-04:%s" % m.stem,
                          "%s referencia una evaluacion de menos de 30 dias" % m.name,
                          vigente, "fecha de evaluacion declarada: %s" % fecha))

    c.append(criterio("S6-05", "el pipeline tiene el gate de manifiesto",
                      existe(".github/workflows/gate-manifiesto.yml"),
                      "sin gate, el manifiesto es documentacion y no gobierno"))

    def pr_sin_manifiesto_pasa():
        """Prueba negativa: un PR que toca agentes/ sin manifiesto debe ser bloqueado."""
        gate = RAIZ / ".github" / "workflows" / "gate-manifiesto.yml"
        if not gate.exists():
            return True
        texto = gate.read_text(encoding="utf-8")
        bloquea = ("sys.exit(1" in texto or "exit 1" in texto)
        return not (bloquea and "manifiestos" in texto)

    ok, detalle = prueba_negativa(pr_sin_manifiesto_pasa,
                                  "PR que toca agentes/ sin manifiesto")
    c.append(criterio("S6-06", "el gate bloquea de verdad, no solo avisa", ok, detalle))

    c.append(criterio("S6-07", "existe el informe de coste por criterio verificado",
                      existe("labs/S6-gobierno/coste.md"),
                      "falta la traduccion de tokens a unidad de negocio"))
    c.append(criterio("S6-08", "existe la argumentacion escrita sobre el nivel N4",
                      existe("labs/S6-gobierno/n4.md"),
                      "falta el analisis de que haria falta para operar a N4",
                      nivel="V3"))
    return c


if __name__ == "__main__":
    for x in verificar():
        print(("OK   " if x["ok"] else "FALLA"), x["id"], x["descripcion"], x["detalle"])
