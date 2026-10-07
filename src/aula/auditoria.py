"""Traza de auditoria.

Invariante del contrato de contexto: toda decision de matricula registra la
version de plan aplicada. Si una rama del codigo decide y no escribe traza, el
verificador de S6 lo detecta.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

RUTA_TRAZA = Path(os.environ.get("AULA_TRAZA", ".aula/auditoria.jsonl"))


def registrar_decision(estudiante_id: str, curso_academico: str, plan: str,
                       version_plan: str, momento: str, resultado: dict) -> dict:
    entrada = {
        "estudiante_id": estudiante_id,
        "curso_academico": curso_academico,
        "plan": plan,
        "version_plan": version_plan,
        "momento": momento,
        "resultado": resultado,
    }
    RUTA_TRAZA.parent.mkdir(parents=True, exist_ok=True)
    with RUTA_TRAZA.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    return entrada


def leer_traza(ruta: Path = None) -> list:
    ruta = ruta or RUTA_TRAZA
    if not ruta.exists():
        return []
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]
