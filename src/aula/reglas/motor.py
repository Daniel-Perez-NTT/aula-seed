"""S1: implementar las reglas de matricula descritas en SPEC-001."""
from __future__ import annotations

from dataclasses import dataclass

from ..dominio.modelos import Expediente, Matricula, Plan, SolicitudMatricula


class VentanaCerrada(Exception):
    pass


@dataclass(frozen=True)
class VentanaMatricula:
    inicio: str
    fin: str

    def contiene(self, momento: str) -> bool:
        raise NotImplementedError("S1: comprobar la ventana de matricula")


@dataclass(frozen=True)
class Grupo:
    codigo_asignatura: str
    capacidad: int
    ocupadas: int

    @property
    def libre(self) -> bool:
        raise NotImplementedError("S1: comprobar la capacidad del grupo")


def creditos_superados(expediente: Expediente, plan: Plan) -> int:
    raise NotImplementedError("S1: calcular creditos superados segun SPEC-001")


def creditos_pendientes(expediente: Expediente, plan: Plan) -> int:
    raise NotImplementedError("S1: calcular creditos pendientes")


def prioridad(expediente: Expediente, plan: Plan) -> int:
    raise NotImplementedError("S1: calcular prioridad de matricula")


def evaluar_solicitud(solicitud: SolicitudMatricula, expediente: Expediente,
                      plan: Plan, ventana: VentanaMatricula,
                      grupos: dict) -> Matricula:
    raise NotImplementedError("S1: evaluar solicitud y registrar auditoria")


def ordenar_por_prioridad(solicitudes: list, expedientes: dict, plan: Plan) -> list:
    raise NotImplementedError("S1: ordenar solicitudes segun SPEC-001")