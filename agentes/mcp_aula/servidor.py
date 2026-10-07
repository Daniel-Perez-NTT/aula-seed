"""Servidor MCP del proyecto Aula.

Expone el contexto del repositorio como herramientas consultables por cualquier
agente. Implementa el transporte stdio de MCP con JSON-RPC 2.0 en biblioteca
estandar: sin SDK, para que el student vea el protocolo por dentro antes de
usar una abstraccion que se lo oculte.

Arranque:
    python3 -m agentes.mcp_aula.servidor

Registro en Claude Code (.mcp.json):
    {"mcpServers": {"aula-contexto": {"command": "python3",
     "args": ["-m", "agentes.mcp_aula.servidor"]}}}
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PROTOCOLO = "2024-11-05"

HERRAMIENTAS = [
    {
        "name": "listar_specs",
        "description": "Devuelve el catalogo de especificaciones del proyecto con su estado y version.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "obtener_spec",
        "description": "Devuelve una spec completa con sus criterios de aceptacion, invariantes y alcance.",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string", "description": "Identificador, por ejemplo SPEC-002"}},
            "required": ["id"],
        },
    },
    {
        "name": "trazabilidad",
        "description": "Para una spec, devuelve que criterios estan cubiertos por test y cuales no.",
        "inputSchema": {
            "type": "object",
            "properties": {"spec_id": {"type": "string"}},
            "required": ["spec_id"],
        },
    },
    {
        "name": "resultado_tests",
        "description": "Ejecuta la suite y devuelve el resultado agregado y los tests fallidos.",
        "inputSchema": {
            "type": "object",
            "properties": {"ruta": {"type": "string", "description": "Subconjunto opcional de tests"}},
            "required": [],
        },
    },
    {
        "name": "version_plan",
        "description": "Devuelve la version vigente de un plan de estudios y sus parametros normativos.",
        "inputSchema": {
            "type": "object",
            "properties": {"codigo": {"type": "string"}},
            "required": ["codigo"],
        },
    },
]


# --- logica de las herramientas ----------------------------------------------

def _specs():
    return sorted((RAIZ / "specs").glob("SPEC-*.md"))


def _id_de(ruta: Path) -> str:
    return ruta.name.split("-")[0] + "-" + ruta.name.split("-")[1]


def _campo(texto: str, patron: str, defecto="desconocido") -> str:
    m = re.search(patron, texto, re.M)
    return m.group(1).strip() if m else defecto


def criterios_de(texto: str) -> list:
    """Extrae los identificadores CA-nn e INV-nn declarados en la spec."""
    return sorted(set(re.findall(r"\b(?:CA|INV)-\d{2}\b", texto)))


def listar_specs(_=None) -> dict:
    salida = []
    for ruta in _specs():
        texto = ruta.read_text(encoding="utf-8")
        salida.append({
            "id": _id_de(ruta),
            "titulo": _campo(texto, r"^#\s+SPEC-\d+:\s*(.+)$"),
            "version": _campo(texto, r"Versi[oó]n:\s*(v[\d.]+)"),
            "estado": _campo(texto, r"Estado:\s*(\w+)"),
            "criterios": len(criterios_de(texto)),
            "ruta": str(ruta.relative_to(RAIZ)),
        })
    return {"specs": salida}


def obtener_spec(args: dict) -> dict:
    ident = args["id"].upper()
    for ruta in _specs():
        if _id_de(ruta) == ident:
            texto = ruta.read_text(encoding="utf-8")
            return {"id": ident, "criterios": criterios_de(texto), "contenido": texto}
    return {"error": "spec %s no encontrada" % ident}


def _cubiertos() -> dict:
    """Mapea criterio -> lista de tests que lo declaran mediante `cubre:`."""
    mapa = {}
    for ruta in (RAIZ / "tests").rglob("test_*.py"):
        texto = ruta.read_text(encoding="utf-8")
        for bloque in re.finditer(r"def (test_\w+)\(.*?\):\s*(?:\"\"\"(.*?)\"\"\")?",
                                  texto, re.S):
            nombre, doc = bloque.group(1), bloque.group(2) or ""
            for etiqueta in re.findall(r"cubre:\s*([^\n\"]+)", doc):
                for ref in re.findall(r"(SPEC-\d+|LEG)[/-]((?:CA|INV|CAR|EQU)[-\w]*)", etiqueta):
                    clave = "%s/%s" % (ref[0], ref[1])
                    mapa.setdefault(clave, []).append("%s::%s" % (ruta.name, nombre))
    return mapa


def trazabilidad(args: dict) -> dict:
    ident = args["spec_id"].upper()
    spec = obtener_spec({"id": ident})
    if "error" in spec:
        return spec
    mapa = _cubiertos()
    cubiertos, huerfanos = {}, []
    for criterio in spec["criterios"]:
        clave = "%s/%s" % (ident, criterio)
        if clave in mapa:
            cubiertos[criterio] = mapa[clave]
        else:
            huerfanos.append(criterio)
    total = len(spec["criterios"])
    return {
        "spec": ident,
        "criterios_totales": total,
        "cubiertos": cubiertos,
        "sin_cubrir": huerfanos,
        "cobertura_pct": round(100.0 * (total - len(huerfanos)) / total, 1) if total else 0.0,
    }


def resultado_tests(args: dict) -> dict:
    raise NotImplementedError("S4a: ejecutar tests con limites de rutas y recursos")


def version_plan(args: dict) -> dict:
    raise NotImplementedError("S4a: exponer version y parametros del plan")


IMPLEMENTACION = {
    "listar_specs": listar_specs,
    "obtener_spec": obtener_spec,
    "trazabilidad": trazabilidad,
    "resultado_tests": resultado_tests,
    "version_plan": version_plan,
}


# --- transporte JSON-RPC sobre stdio ------------------------------------------

def manejar(mensaje: dict):
    raise NotImplementedError("S4a: implementar initialize, tools/list y tools/call")


def _ok(ident, resultado):
    return {"jsonrpc": "2.0", "id": ident, "result": resultado}


def _error(ident, codigo, mensaje):
    return {"jsonrpc": "2.0", "id": ident, "error": {"code": codigo, "message": mensaje}}


def principal():
    raise NotImplementedError("S4a: implementar transporte JSON-RPC por stdio")


if __name__ == "__main__":
    principal()
