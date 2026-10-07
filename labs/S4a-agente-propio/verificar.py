"""Verificador de S4a: Servidor MCP y agente propio."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from aula_cli.verificacion import (contiene, criterio, ejecutar, existe,
                                   orden_en_historial, prueba_negativa,
                                   pytest_verde)


def verificar():
    c = []
    c.append(criterio("S4a-01", "el servidor MCP existe y expone las cinco herramientas",
                      contiene("agentes/mcp_aula/servidor.py",
                               r"listar_specs")
                      and contiene("agentes/mcp_aula/servidor.py", r"trazabilidad")
                      and contiene("agentes/mcp_aula/servidor.py", r"version_plan"),
                      "faltan herramientas en el servidor MCP"))

    p = ejecutar([sys.executable, "-c",
                  "import sys; sys.path.insert(0,'.');"
                  "from agentes.mcp_aula.servidor import manejar;"
                  "r=manejar({'jsonrpc':'2.0','id':1,'method':'tools/list','params':{}});"
                  "print(len(r['result']['tools']))"])
    herramientas = p.stdout.strip()
    c.append(criterio("S4a-02", "el servidor MCP responde a tools/list",
                      herramientas.isdigit() and int(herramientas) >= 5,
                      p.stderr.strip()[:200] or "herramientas devueltas: %s" % herramientas))

    c.append(criterio("S4a-03", "el agente de conformidad existe y es ejecutable",
                      existe("agentes/conformidad/agente.py"),
                      "falta el agente"))

    p = ejecutar([sys.executable, "-m", "agentes.conformidad.evaluar"])
    c.append(criterio("S4a-04", "el agente supera los umbrales sobre el conjunto de evaluacion",
                      p.returncode == 0,
                      (p.stdout.strip().splitlines() or ["sin salida"])[-1]))

    informes = sorted((RAIZ / "evals" / "informes").glob("*.json")) \
        if (RAIZ / "evals" / "informes").exists() else []
    c.append(criterio("S4a-05", "hay al menos dos informes de evaluacion fechados",
                      len(informes) >= 2,
                      "informes encontrados: %d. Se exigen dos iteraciones medidas, "
                      "no una entrega unica" % len(informes)))

    c.append(criterio("S4a-06", "el veredicto del agente es determinista",
                      contiene("agentes/conformidad/agente.py", r"determinista|DETERMINISTA"),
                      "si el modelo decide el veredicto, el gate no es reproducible"))
    return c


if __name__ == "__main__":
    for x in verificar():
        print(("OK   " if x["ok"] else "FALLA"), x["id"], x["descripcion"], x["detalle"])
