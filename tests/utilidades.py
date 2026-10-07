"""Constructores de datos para los tests. Sin logica de negocio aqui."""
from decimal import Decimal
from pathlib import Path

from aula.dominio.modelos import (EstadoRegistro, Expediente, RegistroAcademico,
                                  SolicitudMatricula)
from aula.reglas.planes import cargar_plan

RAIZ = Path(__file__).resolve().parents[1]


def plan():
    return cargar_plan("PLAN-2024", RAIZ / "datos" / "planes")


def registro(codigo, estado, nota=None, convocatoria=1, curso="2024-2025"):
    return RegistroAcademico(
        codigo_asignatura=codigo, curso_academico=curso, convocatoria=convocatoria,
        estado=EstadoRegistro(estado),
        nota=Decimal(str(nota)) if nota is not None else None)


def expediente(*registros, estudiante="EST-0001"):
    return Expediente(estudiante_id=estudiante, plan="PLAN-2024", registros=list(registros))


def solicitud(codigos, momento="2026-09-10T10:00:00", estudiante="EST-0001"):
    return SolicitudMatricula(estudiante_id=estudiante, curso_academico="2026-2027",
                              codigos=list(codigos), momento=momento)
