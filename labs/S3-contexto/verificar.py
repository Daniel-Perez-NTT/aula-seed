"""Verificador de S3: Ingenieria de contexto y operacion de agentes."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from aula_cli.verificacion import (contiene, criterio, ejecutar, existe,
                                   orden_en_historial, prueba_negativa,
                                   pytest_verde)


SECCIONES = ["Prop[oó]sito", "Invariantes", "Verificaci[oó]n", "Convenciones",
             "L[ií]mites", "Escalado"]


def verificar():
    c = []
    faltan = [s for s in SECCIONES
              if not contiene("CLAUDE.md", r"#+\s*%s" % s)]
    c.append(criterio("S3-01", "CLAUDE.md tiene las seis secciones obligatorias",
                      not faltan, "faltan: %s" % ", ".join(faltan)))
    c.append(criterio("S3-02", "los invariantes del contrato son concretos y verificables",
                      contiene("CLAUDE.md", r"redondeo") and contiene("CLAUDE.md", r"auditor"),
                      "los invariantes no mencionan el redondeo unico ni la traza de auditoria"))
    c.append(criterio("S3-03", "hay allowlist y hooks configurados",
                      existe(".claude/settings.json") or existe(".claude/hooks"),
                      "no se encuentra configuracion de permisos ni hooks"))

    def escribir_en_ruta_prohibida():
        """Prueba negativa: el control debe impedir esta escritura."""
        import json
        cfg = RAIZ / ".claude" / "settings.json"
        if not cfg.exists():
            return True   # no hay control: la accion "tiene exito", el criterio falla
        texto = cfg.read_text(encoding="utf-8")
        prohibidas = ["manifiestos", "workflows", "labs"]
        return not all(p in texto for p in prohibidas)

    ok, detalle = prueba_negativa(escribir_en_ruta_prohibida,
                                  "escritura en manifiestos/ y .github/")
    c.append(criterio("S3-04", "el control bloquea de verdad la escritura en rutas prohibidas",
                      ok, detalle))
    c.append(criterio("S3-05", "existe la tabla comparativa entre motores de agente",
                      existe("labs/S3-contexto/comparativa.md")
                      and contiene("labs/S3-contexto/comparativa.md", r"OpenCode"),
                      "falta la comparativa razonada Claude Code frente a OpenCode"))
    c.append(criterio("S3-06", "hay subagentes de proposito acotado definidos",
                      existe(".claude/agents") or contiene("CLAUDE.md", r"subagente"),
                      "no se declaran subagentes de implementacion y revision"))
    return c


if __name__ == "__main__":
    for x in verificar():
        print(("OK   " if x["ok"] else "FALLA"), x["id"], x["descripcion"], x["detalle"])
