"""API HTTP de Aula Students."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, field_validator

from ..dominio.modelos import Expediente
from ..reglas.motor import (
    VentanaCerrada,
    VentanaMatricula,
    evaluar_solicitud,
)
from ..reglas.planes import cargar_plan
from ..dominio.modelos import SolicitudMatricula


app = FastAPI(title="Aula Students", version="1.0.0")

# S1 usa almacenamiento en memoria: se pierde al reiniciar el proceso.
MATRICULAS = {}
EXPEDIENTES = {}

PLAN = cargar_plan("PLAN-2024")
VENTANA = VentanaMatricula(
    inicio="2026-01-01T00:00:00",
    fin="2027-12-31T23:59:59",
)
GRUPOS = {}


class SolicitudEntrada(BaseModel):
    estudiante_id: str
    curso_academico: str
    codigos: list[str] = Field(min_length=1)
    momento: str | None = None

    @field_validator("codigos")
    @classmethod
    def codigos_sin_repetir(cls, valores):
        if len(set(valores)) != len(valores):
            raise ValueError("no se permiten códigos repetidos")
        return valores


@app.get("/salud")
def salud():
    return {"estado": "ok", "momento": datetime.now(timezone.utc).isoformat()}


@app.post("/matriculas")
def crear_matricula(entrada: SolicitudEntrada):
    momento = entrada.momento or datetime.now(timezone.utc).isoformat()
    peticion = SolicitudMatricula(
        estudiante_id=entrada.estudiante_id,
        curso_academico=entrada.curso_academico,
        codigos=entrada.codigos,
        momento=momento,
    )
    expediente = EXPEDIENTES.setdefault(
        entrada.estudiante_id,
        Expediente(estudiante_id=entrada.estudiante_id, plan=PLAN.codigo),
    )

    try:
        matricula = evaluar_solicitud(
            peticion,
            expediente,
            PLAN,
            VENTANA,
            GRUPOS,
        )
    except VentanaCerrada as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    clave = f"{entrada.estudiante_id}:{entrada.curso_academico}"
    MATRICULAS[clave] = matricula
    return jsonable_encoder(matricula)


@app.get("/expedientes/{estudiante_id}")
def ver_expediente(estudiante_id: str):
    raise HTTPException(
        status_code=501,
        detail="S2: consulta de expediente pendiente",
    )