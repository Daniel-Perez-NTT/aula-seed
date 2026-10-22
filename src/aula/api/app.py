"""API HTTP de Aula Students."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, field_validator

from ..dominio.modelos import (
    EstadoRegistro,
    Expediente,
    RegistroAcademico,
    SolicitudMatricula,
)
from ..reglas.motor import (
    VentanaCerrada,
    VentanaMatricula,
    evaluar_solicitud,
)
from ..reglas.media import resumen_expediente
from ..reglas.planes import cargar_plan

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


class RegistroAcademicoEntrada(BaseModel):
    codigo_asignatura: str
    curso_academico: str
    convocatoria: int = Field(ge=1)
    estado: EstadoRegistro
    nota: Decimal | None = None


def _respuesta_expediente(expediente: Expediente) -> dict:
    resumen = resumen_expediente(expediente, PLAN)
    resumen["plan"] = {
        "codigo": PLAN.codigo,
        "version": PLAN.version,
        "creditos_titulo": PLAN.creditos_titulo,
    }
    resumen["registros"] = [
        {
            "codigo_asignatura": registro.codigo_asignatura,
            "nombre_asignatura": PLAN.asignatura(
                registro.codigo_asignatura
            ).nombre,
            "creditos": PLAN.asignatura(registro.codigo_asignatura).creditos,
            "curso_academico": registro.curso_academico,
            "convocatoria": registro.convocatoria,
            "estado": registro.estado.value,
            "nota": registro.nota,
        }
        for registro in expediente.registros
    ]
    return jsonable_encoder(resumen)


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
    expediente = EXPEDIENTES.get(estudiante_id)

    if expediente is None:
        raise HTTPException(
            status_code=404,
            detail="expediente no encontrado",
        )

    return _respuesta_expediente(expediente)


@app.post("/expedientes/{estudiante_id}/registros", status_code=201)
def anadir_registro_expediente(
    estudiante_id: str,
    entrada: RegistroAcademicoEntrada,
):
    codigo = entrada.codigo_asignatura
    try:
        PLAN.asignatura(codigo)
    except KeyError as exc:
        raise HTTPException(
            status_code=422,
            detail="la asignatura no pertenece al plan",
        ) from exc

    expediente = EXPEDIENTES.setdefault(
        estudiante_id,
        Expediente(estudiante_id=estudiante_id, plan=PLAN.codigo),
    )
    expediente.registros.append(
        RegistroAcademico(
            codigo_asignatura=codigo,
            curso_academico=entrada.curso_academico,
            convocatoria=entrada.convocatoria,
            estado=entrada.estado,
            nota=entrada.nota,
        )
    )
    return _respuesta_expediente(expediente)
