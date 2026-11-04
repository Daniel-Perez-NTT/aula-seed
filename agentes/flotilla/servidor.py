"""Extiende el servidor MCP de Aula con mensajería entre agentes."""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from agentes.mcp_aula.servidor import HERRAMIENTAS as HERRAMIENTAS_AULA
from agentes.mcp_aula.servidor import RAIZ
from agentes.mcp_aula.servidor import manejar as manejar_aula


ROLES = {
    "conformidad",
    "triaje",
    "modernizacion",
}
DESTINATARIOS = ROLES | {"responsable_humano"}

HERRAMIENTAS_MENSAJERIA = [
    {
        "name": "publicar_mensaje",
        "description": "Envía un mensaje estructurado a otro agente de la flotilla.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "de": {"type": "string"},
                "para": {"type": "string"},
                "tipo": {"type": "string"},
                "commit": {"type": "string"},
                "payload": {"type": "object"},
            },
            "required": ["run_id", "de", "para", "tipo", "commit", "payload"],
        },
    },
    {
        "name": "leer_bandeja",
        "description": "Lee mensajes pendientes para un agente en un ciclo concreto.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "destinatario": {"type": "string"},
            },
            "required": ["run_id", "destinatario"],
        },
    },
    {
        "name": "confirmar_mensaje",
        "description": "Marca como recibido un mensaje dirigido al agente.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mensaje_id": {"type": "string"},
                "destinatario": {"type": "string"},
            },
            "required": ["mensaje_id", "destinatario"],
        },
    },
]


def _ruta_bandeja() -> Path:
    valor = os.environ.get("AULA_FLOTILLA_DB")
    if not valor:
        raise ValueError(
            "falta la variable AULA_FLOTILLA_DB; debe señalar la base SQLite "
            "compartida por las sesiones"
        )

    ruta = Path(valor).expanduser().resolve()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return ruta


def _conectar() -> sqlite3.Connection:
    conexion = sqlite3.connect(_ruta_bandeja(), timeout=10)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA busy_timeout = 10000")
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS mensajes (
            mensaje_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            emisor TEXT NOT NULL,
            destinatario TEXT NOT NULL,
            tipo TEXT NOT NULL,
            commit_id TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            creado_utc TEXT NOT NULL,
            recibido INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conexion.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_mensajes_bandeja
        ON mensajes(run_id, destinatario, recibido, creado_utc)
        """
    )
    conexion.commit()
    return conexion


def _destinatarios_permitidos(emisor: str) -> set[str]:
    ruta = RAIZ / "agentes" / "flotilla" / "contrato.json"
    contrato = json.loads(ruta.read_text(encoding="utf-8"))
    for agente in contrato.get("agentes", []):
        if agente.get("id") == emisor:
            return set(agente.get("destinatarios_permitidos", []))
    return set()


def publicar_mensaje(argumentos: dict) -> dict:
    run_id = str(argumentos.get("run_id", "")).strip()
    emisor = str(argumentos.get("de", "")).strip()
    destinatario = str(argumentos.get("para", "")).strip()
    tipo = str(argumentos.get("tipo", "")).strip()
    commit_id = str(argumentos.get("commit", "")).strip().lower()
    payload = argumentos.get("payload")

    if not run_id:
        raise ValueError("run_id es obligatorio")
    if emisor not in ROLES:
        raise ValueError(f"emisor desconocido: {emisor}")
    if destinatario not in DESTINATARIOS:
        raise ValueError(f"destinatario desconocido: {destinatario}")
    if destinatario not in _destinatarios_permitidos(emisor):
        raise ValueError(
            f"{emisor} no tiene permiso para enviar mensajes a {destinatario}"
        )
    if not tipo:
        raise ValueError("tipo es obligatorio")
    if not re.fullmatch(r"[0-9a-f]{7,40}", commit_id):
        raise ValueError("commit debe ser un SHA de Git de 7 a 40 caracteres")
    if not isinstance(payload, dict):
        raise ValueError("payload debe ser un objeto JSON")

    mensaje = {
        "mensaje_id": str(uuid.uuid4()),
        "run_id": run_id,
        "de": emisor,
        "para": destinatario,
        "tipo": tipo,
        "commit": commit_id,
        "payload": payload,
        "creado_utc": datetime.now(timezone.utc).isoformat(),
    }

    with _conectar() as conexion:
        conexion.execute(
            """
            INSERT INTO mensajes (
                mensaje_id, run_id, emisor, destinatario, tipo,
                commit_id, payload_json, creado_utc
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mensaje["mensaje_id"],
                mensaje["run_id"],
                mensaje["de"],
                mensaje["para"],
                mensaje["tipo"],
                mensaje["commit"],
                json.dumps(payload, ensure_ascii=False),
                mensaje["creado_utc"],
            ),
        )

    return {"publicado": True, "mensaje": mensaje}


def leer_bandeja(argumentos: dict) -> dict:
    run_id = str(argumentos.get("run_id", "")).strip()
    destinatario = str(argumentos.get("destinatario", "")).strip()

    if not run_id:
        raise ValueError("run_id es obligatorio")
    if destinatario not in DESTINATARIOS:
        raise ValueError(f"destinatario desconocido: {destinatario}")

    with _conectar() as conexion:
        filas = conexion.execute(
            """
            SELECT mensaje_id, run_id, emisor, destinatario, tipo,
                   commit_id, payload_json, creado_utc
            FROM mensajes
            WHERE run_id = ? AND destinatario = ? AND recibido = 0
            ORDER BY creado_utc, mensaje_id
            """,
            (run_id, destinatario),
        ).fetchall()

    mensajes = [
        {
            "mensaje_id": fila["mensaje_id"],
            "run_id": fila["run_id"],
            "de": fila["emisor"],
            "para": fila["destinatario"],
            "tipo": fila["tipo"],
            "commit": fila["commit_id"],
            "payload": json.loads(fila["payload_json"]),
            "creado_utc": fila["creado_utc"],
        }
        for fila in filas
    ]
    return {"run_id": run_id, "destinatario": destinatario, "mensajes": mensajes}


def confirmar_mensaje(argumentos: dict) -> dict:
    mensaje_id = str(argumentos.get("mensaje_id", "")).strip()
    destinatario = str(argumentos.get("destinatario", "")).strip()

    if not mensaje_id:
        raise ValueError("mensaje_id es obligatorio")
    if destinatario not in DESTINATARIOS:
        raise ValueError(f"destinatario desconocido: {destinatario}")

    with _conectar() as conexion:
        cursor = conexion.execute(
            """
            UPDATE mensajes
            SET recibido = 1
            WHERE mensaje_id = ? AND destinatario = ? AND recibido = 0
            """,
            (mensaje_id, destinatario),
        )

    return {"confirmado": cursor.rowcount == 1, "mensaje_id": mensaje_id}


IMPLEMENTACION_MENSAJERIA = {
    "publicar_mensaje": publicar_mensaje,
    "leer_bandeja": leer_bandeja,
    "confirmar_mensaje": confirmar_mensaje,
}


def _ok(identificador, resultado: dict) -> dict:
    return {"jsonrpc": "2.0", "id": identificador, "result": resultado}


def _respuesta_herramienta(identificador, resultado: dict) -> dict:
    contenido = {
        "content": [
            {
                "type": "text",
                "text": json.dumps(resultado, ensure_ascii=False),
            }
        ],
        "isError": "error" in resultado,
    }
    return _ok(identificador, contenido)


def manejar(mensaje: dict) -> dict | None:
    if not isinstance(mensaje, dict):
        return manejar_aula(mensaje)

    metodo = mensaje.get("method")
    identificador = mensaje.get("id")
    parametros = mensaje.get("params") or {}

    if metodo == "initialize":
        respuesta = manejar_aula(mensaje)
        if "result" in respuesta:
            respuesta["result"]["serverInfo"] = {
                "name": "aula-flotilla",
                "version": "1.0.0",
            }
        return respuesta

    if metodo == "tools/list":
        respuesta = manejar_aula(mensaje)
        if "result" in respuesta:
            respuesta["result"]["tools"] = (
                HERRAMIENTAS_AULA + HERRAMIENTAS_MENSAJERIA
            )
        return respuesta

    if metodo == "tools/call":
        nombre = parametros.get("name")
        if nombre in IMPLEMENTACION_MENSAJERIA:
            try:
                resultado = IMPLEMENTACION_MENSAJERIA[nombre](
                    parametros.get("arguments") or {}
                )
                return _respuesta_herramienta(identificador, resultado)
            except (KeyError, TypeError, ValueError, OSError, sqlite3.Error) as exc:
                return _respuesta_herramienta(
                    identificador,
                    {"error": str(exc)},
                )

    return manejar_aula(mensaje)


def principal() -> None:
    for linea in sys.stdin:
        if not linea.strip():
            continue
        try:
            respuesta = manejar(json.loads(linea))
        except json.JSONDecodeError as exc:
            respuesta = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"JSON inválido: {exc.msg}",
                },
            }

        if respuesta is not None:
            sys.stdout.write(json.dumps(respuesta, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    principal()