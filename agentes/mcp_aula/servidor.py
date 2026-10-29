"""Servidor MCP de Aula usando JSON-RPC 2.0 sobre stdio."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PROTOCOLO = "2024-11-05"
TIEMPO_MAXIMO_TESTS = 60

HERRAMIENTAS = [
    {
        "name": "listar_specs",
        "description": "Devuelve el catalogo de especificaciones del proyecto.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "obtener_spec",
        "description": "Devuelve una especificacion completa.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "trazabilidad",
        "description": "Devuelve los criterios cubiertos por tests y los que faltan.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec_id": {"type": "string"},
            },
            "required": ["spec_id"],
        },
    },
    {
        "name": "resultado_tests",
        "description": "Ejecuta tests dentro de la carpeta tests/ y resume el resultado.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ruta": {"type": "string"},
            },
            "required": [],
        },
    },
    {
        "name": "version_plan",
        "description": "Devuelve la version y los parametros de un plan.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "codigo": {"type": "string"},
            },
            "required": [],
        },
    },
]


def _specs() -> list[Path]:
    """Devuelve las specs ordenadas por nombre."""
    return sorted((RAIZ / "specs").glob("SPEC-*.md"))


def _id_de(ruta: Path) -> str:
    """Convierte SPEC-002-expediente.md en SPEC-002."""
    partes = ruta.name.split("-")
    return "-".join(partes[:2])


def _campo(texto: str, patron: str, defecto: str = "desconocido") -> str:
    coincidencia = re.search(patron, texto, re.M)
    return coincidencia.group(1).strip() if coincidencia else defecto


def criterios_de(texto: str) -> list[str]:
    """Extrae criterios de aceptacion e invariantes."""
    return sorted(set(re.findall(r"\b(?:CA|INV)-\d{2}\b", texto)))


def listar_specs(_argumentos: dict | None = None) -> dict:
    """Devuelve el catalogo de specs del repositorio."""
    salida = []

    for ruta in _specs():
        texto = ruta.read_text(encoding="utf-8")
        salida.append({
            "id": _id_de(ruta),
            "titulo": _campo(texto, r"^#\s+SPEC-\d+:\s*(.+)$"),
            "version": _campo(texto, r"Versi[oó]n:\s*(v[\d.]+)"),
            "estado": _campo(texto, r"Estado:\s*(\w+)"),
            "criterios": len(criterios_de(texto)),
            "ruta": ruta.relative_to(RAIZ).as_posix(),
        })

    return {"specs": salida}


def obtener_spec(argumentos: dict) -> dict:
    """Devuelve el texto completo de la spec solicitada."""
    ident = str(argumentos.get("id", "")).upper()

    for ruta in _specs():
        if _id_de(ruta) == ident:
            texto = ruta.read_text(encoding="utf-8")
            return {
                "id": ident,
                "criterios": criterios_de(texto),
                "contenido": texto,
            }

    return {"error": f"spec {ident or '(vacia)'} no encontrada"}


def _cubiertos() -> dict[str, list[str]]:
    """Mapea identificadores de criterio a tests con una etiqueta cubre:."""
    mapa: dict[str, list[str]] = {}

    for ruta in sorted((RAIZ / "tests").rglob("test_*.py")):
        texto = ruta.read_text(encoding="utf-8")

        # Cada bloque de funcion de test se recorre para asociar su nombre
        # a las etiquetas cubre: que haya en su docstring.
        funciones = list(re.finditer(
            r"def\s+(test_\w+)\s*\(.*?\):",
            texto,
            re.S,
        ))

        for indice, funcion in enumerate(funciones):
            inicio = funcion.end()
            fin = (
                funciones[indice + 1].start()
                if indice + 1 < len(funciones)
                else len(texto)
            )
            bloque = texto[inicio:fin]
            nombre = funcion.group(1)

            for etiqueta in re.findall(r"cubre:\s*([^\n\"]+)", bloque):
                referencias = re.findall(
                    r"(SPEC-\d+|LEG)[/-]((?:CA|INV|CAR|EQU)-[\w]+)",
                    etiqueta,
                )
                for spec_id, criterio in referencias:
                    clave = f"{spec_id}/{criterio}"
                    test_id = f"{ruta.name}::{nombre}"
                    mapa.setdefault(clave, []).append(test_id)

    return mapa


def trazabilidad(argumentos: dict) -> dict:
    """Comprueba qué criterios de una spec tienen tests etiquetados."""
    ident = str(argumentos.get("spec_id", "")).upper()
    spec = obtener_spec({"id": ident})

    if "error" in spec:
        return spec

    mapa = _cubiertos()
    cubiertos = {}
    sin_cubrir = []

    for criterio in spec["criterios"]:
        clave = f"{ident}/{criterio}"
        if clave in mapa:
            cubiertos[criterio] = mapa[clave]
        else:
            sin_cubrir.append(criterio)

    total = len(spec["criterios"])
    porcentaje = (
        round(100 * (total - len(sin_cubrir)) / total, 1)
        if total
        else 0.0
    )

    return {
        "spec": ident,
        "criterios_totales": total,
        "cubiertos": cubiertos,
        "sin_cubrir": sin_cubrir,
        "cobertura_pct": porcentaje,
    }


def resultado_tests(argumentos: dict) -> dict:
    """Ejecuta pytest solo dentro de tests/, sin usar un shell."""
    solicitado = str(argumentos.get("ruta", "tests"))

    raiz_tests = (RAIZ / "tests").resolve()
    ruta = (RAIZ / solicitado).resolve()

    try:
        ruta.relative_to(raiz_tests)
    except ValueError:
        return {
            "error": "solo se permiten rutas dentro de tests/",
            "ruta": solicitado,
        }

    if not ruta.exists():
        return {"error": "la ruta no existe", "ruta": solicitado}

    comando = [
        sys.executable,
        "-m",
        "pytest",
        ruta.relative_to(RAIZ).as_posix(),
        "-q",
    ]

    try:
        proceso = subprocess.run(
            comando,
            cwd=RAIZ,
            capture_output=True,
            text=True,
            timeout=TIEMPO_MAXIMO_TESTS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "error": "pytest supero el limite de tiempo",
            "ruta": solicitado,
            "timeout_segundos": TIEMPO_MAXIMO_TESTS,
        }

    salida = (proceso.stdout + "\n" + proceso.stderr).strip()
    lineas = [linea.strip() for linea in salida.splitlines() if linea.strip()]
    fallos = [
        linea for linea in lineas
        if linea.startswith(("FAILED ", "ERROR "))
    ]

    return {
        "ruta": solicitado,
        "correcto": proceso.returncode == 0,
        "codigo_salida": proceso.returncode,
        "resumen": lineas[-1] if lineas else "pytest no produjo salida",
        "fallos": fallos,
    }


def version_plan(argumentos: dict) -> dict:
    """Lee un plan cuyo nombre sea PLAN-<codigo>.json."""
    codigo = str(argumentos.get("codigo", "PLAN-2024")).upper()

    if not re.fullmatch(r"PLAN-[A-Z0-9_-]+", codigo):
        return {"error": "codigo de plan no valido"}

    ruta = (RAIZ / "datos" / "planes" / f"{codigo}.json").resolve()
    carpeta_planes = (RAIZ / "datos" / "planes").resolve()

    try:
        ruta.relative_to(carpeta_planes)
    except ValueError:
        return {"error": "ruta de plan no permitida"}

    if not ruta.is_file():
        return {"error": f"plan {codigo} no encontrado"}

    return json.loads(ruta.read_text(encoding="utf-8"))


IMPLEMENTACION = {
    "listar_specs": listar_specs,
    "obtener_spec": obtener_spec,
    "trazabilidad": trazabilidad,
    "resultado_tests": resultado_tests,
    "version_plan": version_plan,
}


def _ok(identificador, resultado) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": identificador,
        "result": resultado,
    }


def _error(identificador, codigo: int, mensaje: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": identificador,
        "error": {
            "code": codigo,
            "message": mensaje,
        },
    }


def manejar(mensaje: dict) -> dict | None:
    """Procesa una solicitud JSON-RPC/MCP y devuelve su respuesta."""
    if not isinstance(mensaje, dict) or mensaje.get("jsonrpc") != "2.0":
        return _error(None, -32600, "solicitud JSON-RPC no valida")

    metodo = mensaje.get("method")
    identificador = mensaje.get("id")
    parametros = mensaje.get("params") or {}

    # Las notificaciones no llevan id y no reciben respuesta.
    if metodo == "notifications/initialized":
        return None

    if metodo == "ping":
        return _ok(identificador, {})

    if metodo == "initialize":
        resultado = {
            "protocolVersion": parametros.get("protocolVersion", PROTOCOLO),
            "capabilities": {
                "tools": {
                    "listChanged": False,
                },
            },
            "serverInfo": {
                "name": "aula-contexto",
                "version": "1.0.0",
            },
        }
        return _ok(identificador, resultado)

    if metodo == "tools/list":
        return _ok(identificador, {"tools": HERRAMIENTAS})

    if metodo == "tools/call":
        nombre = parametros.get("name")
        argumentos = parametros.get("arguments") or {}

        if nombre not in IMPLEMENTACION:
            return _error(identificador, -32602, f"herramienta desconocida: {nombre}")

        try:
            resultado = IMPLEMENTACION[nombre](argumentos)
        except (KeyError, TypeError, ValueError) as exc:
            return _error(identificador, -32602, str(exc))
        except Exception as exc:
            return _error(identificador, -32603, f"error interno: {exc}")

        contenido = {
            "content": [{
                "type": "text",
                "text": json.dumps(resultado, ensure_ascii=False),
            }],
            "isError": "error" in resultado,
        }
        return _ok(identificador, contenido)

    if metodo in {"shutdown", "exit"}:
        return _ok(identificador, {})

    return _error(identificador, -32601, f"metodo desconocido: {metodo}")


def principal() -> None:
    """Lee una solicitud JSON por linea y escribe una respuesta por linea."""
    for linea in sys.stdin:
        if not linea.strip():
            continue

        try:
            mensaje = json.loads(linea)
            respuesta = manejar(mensaje)
        except json.JSONDecodeError as exc:
            respuesta = _error(None, -32700, f"JSON no valido: {exc.msg}")

        if respuesta is not None:
            sys.stdout.write(json.dumps(respuesta, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    principal()