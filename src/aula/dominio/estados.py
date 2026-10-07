"""S1: completar las transiciones y proteger el plan confirmado."""
from __future__ import annotations

from .modelos import EstadoMatricula, Matricula

TRANSICIONES: dict[EstadoMatricula, set[EstadoMatricula]] = {}


class TransicionInvalida(Exception):
    pass


class PlanInmutable(Exception):
    pass


def transiciones_validas(estado: EstadoMatricula) -> set:
    raise NotImplementedError("S1: definir transiciones validas")


def transicionar(matricula: Matricula, destino: EstadoMatricula,
                 nuevo_plan: str = None) -> Matricula:
    raise NotImplementedError("S1: validar y aplicar una transicion")