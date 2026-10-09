"""Transiciones permitidas para una matrícula."""
from __future__ import annotations

from .modelos import EstadoMatricula, Matricula


TRANSICIONES = {
    EstadoMatricula.SOLICITADA: {
        EstadoMatricula.VALIDADA,
        EstadoMatricula.ANULADA,
    },
    EstadoMatricula.VALIDADA: {
        EstadoMatricula.CONFIRMADA,
        EstadoMatricula.ANULADA,
    },
    EstadoMatricula.CONFIRMADA: {
        EstadoMatricula.EN_CURSO,
    },
    EstadoMatricula.EN_CURSO: {
        EstadoMatricula.CALIFICADA,
    },
    EstadoMatricula.CALIFICADA: {
        EstadoMatricula.CERRADA,
    },
    EstadoMatricula.CERRADA: set(),
    EstadoMatricula.ANULADA: set(),
}


class TransicionInvalida(Exception):
    """Se intentó una transición que no está permitida."""


class PlanInmutable(Exception):
    """Se intentó cambiar el plan tras confirmar la matrícula."""


def transiciones_validas(estado: EstadoMatricula) -> set:
    return TRANSICIONES[estado].copy()


def transicionar(
    matricula: Matricula,
    destino: EstadoMatricula,
    nuevo_plan: str = None,
) -> Matricula:
    if destino not in TRANSICIONES[matricula.estado]:
        raise TransicionInvalida(
            f"no se puede pasar de {matricula.estado.value} a {destino.value}"
        )

    estados_con_plan_inmutable = {
        EstadoMatricula.CONFIRMADA,
        EstadoMatricula.EN_CURSO,
        EstadoMatricula.CALIFICADA,
        EstadoMatricula.CERRADA,
    }
    if (
        matricula.estado in estados_con_plan_inmutable
        and nuevo_plan is not None
        and nuevo_plan != matricula.plan_aplicado
    ):
        raise PlanInmutable("el plan no puede cambiar después de confirmar")

    matricula.estado = destino
    if nuevo_plan is not None:
        matricula.plan_aplicado = nuevo_plan
    return matricula