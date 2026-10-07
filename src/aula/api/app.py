"""Servicio de arranque. S1 y S2 completan los recursos pendientes."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Aula Students", version="0.0.0")


class SolicitudEntrada(BaseModel):
    estudiante_id: str
    curso_academico: str
    codigos: list[str]
    momento: str | None = None


@app.get("/salud")
def salud():
    return {"estado": "ok", "momento": datetime.now(timezone.utc).isoformat()}


@app.post("/matriculas")
def crear_matricula(entrada: SolicitudEntrada):
    raise HTTPException(status_code=501, detail="S1: alta de matricula pendiente")


@app.get("/expedientes/{estudiante_id}")
def ver_expediente(estudiante_id: str):
    raise HTTPException(status_code=501, detail="S2: consulta de expediente pendiente")