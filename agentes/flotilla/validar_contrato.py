"""Valida el contrato de la flotilla contra su esquema y el servidor MCP."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from agentes.mcp_aula.servidor import HERRAMIENTAS as HERRAMIENTAS_AULA
from agentes.flotilla.servidor import HERRAMIENTAS_MENSAJERIA


RAIZ = Path(__file__).resolve().parents[2]
RUTA_CONTRATO = RAIZ / "agentes" / "flotilla" / "contrato.json"
RUTA_ESQUEMA = RAIZ / "agentes" / "flotilla" / "contrato.schema.json"

ROLES_ESPERADOS = {
    "conformidad",
    "triaje",
    "modernizacion",
}


def cargar_json(ruta: Path) -> dict:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"No se pudo leer {ruta}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JSON inválido en {ruta}, línea {exc.lineno}, "
            f"columna {exc.colno}: {exc.msg}"
        ) from exc


def validar() -> list[str]:
    contrato = cargar_json(RUTA_CONTRATO)
    esquema = cargar_json(RUTA_ESQUEMA)
    errores = []

    validador = Draft202012Validator(esquema)
    for error in sorted(validador.iter_errors(contrato), key=lambda e: list(e.path)):
        ruta = ".".join(str(parte) for parte in error.path) or "<raíz>"
        errores.append(f"{ruta}: {error.message}")

    agentes = contrato.get("agentes", [])
    ids = [agente.get("id") for agente in agentes]

    if set(ids) != ROLES_ESPERADOS:
        errores.append(
            "agentes: se esperan exactamente conformidad, triaje y modernizacion"
        )

    nombres_mcp = {
        herramienta["name"]
        for herramienta in HERRAMIENTAS_AULA + HERRAMIENTAS_MENSAJERIA
    }

    for agente in agentes:
        identificador = agente.get("id", "<sin-id>")
        for herramienta in agente.get("herramientas_mcp", []):
            if herramienta not in nombres_mcp:
                errores.append(
                    f"agentes.{identificador}.herramientas_mcp: "
                    f"{herramienta!r} no existe en los servidores MCP disponibles"
                )

    destinos_validos = ROLES_ESPERADOS | {"responsable_humano"}

    for agente in agentes:
        identificador = agente.get("id", "<sin-id>")
        for destino in agente.get("destinatarios_permitidos", []):
            if destino not in destinos_validos:
                errores.append(
                    f"agentes.{identificador}: destinatario desconocido {destino!r}"
                )

    for handoff in contrato.get("handoffs", []):
        desde = handoff.get("desde")
        hacia = handoff.get("hacia")

        if desde not in ROLES_ESPERADOS:
            errores.append(f"handoffs: emisor desconocido {desde!r}")
        if hacia not in destinos_validos:
            errores.append(f"handoffs: destinatario desconocido {hacia!r}")
        else:
            emisor_contrato = next(
                (agente for agente in agentes if agente.get("id") == desde),
                None,
            )
            if (
                emisor_contrato is not None
                and hacia not in emisor_contrato.get("destinatarios_permitidos", [])
            ):
                errores.append(
                    f"handoffs: {desde!r} no tiene permitido enviar a {hacia!r}"
                )

    return errores


def main() -> int:
    try:
        errores = validar()
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    if errores:
        print("Contrato inválido:")
        for error in errores:
            print(f"  - {error}")
        return 1

    print("OK: contrato válido contra el esquema")
    print("OK: roles y destinatarios conocidos")
    print("OK: herramientas MCP declaradas y disponibles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
