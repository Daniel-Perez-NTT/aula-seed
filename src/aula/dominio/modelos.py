"""Modelos del dominio.

Sin dependencias externas de forma deliberada: el nucleo tiene que poder
ejecutarse y testearse sin levantar servicio ni base de datos.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional


class EstadoRegistro(str, Enum):
    APROBADA = "aprobada"
    SUSPENSA = "suspensa"
    NO_PRESENTADO = "no_presentado"
    CONVALIDADA = "convalidada"


class EstadoMatricula(str, Enum):
    SOLICITADA = "solicitada"
    VALIDADA = "validada"
    CONFIRMADA = "confirmada"
    EN_CURSO = "en_curso"
    CALIFICADA = "calificada"
    CERRADA = "cerrada"
    ANULADA = "anulada"


@dataclass(frozen=True)
class Asignatura:
    codigo: str
    nombre: str
    creditos: int
    curso: int
    prerrequisitos: tuple = ()


@dataclass(frozen=True)
class Plan:
    codigo: str
    version: str
    creditos_titulo: int
    limite_creditos_curso: int
    max_convocatorias: int
    umbral_final_carrera: int
    asignaturas: dict

    def asignatura(self, codigo: str) -> Asignatura:
        if codigo not in self.asignaturas:
            raise KeyError("asignatura %s no pertenece al plan %s" % (codigo, self.codigo))
        return self.asignaturas[codigo]


@dataclass(frozen=True)
class RegistroAcademico:
    """Una convocatoria consumida de una asignatura, o una convalidacion."""
    codigo_asignatura: str
    curso_academico: str
    convocatoria: int
    estado: EstadoRegistro
    nota: Optional[Decimal] = None


@dataclass
class Expediente:
    estudiante_id: str
    plan: str
    registros: list = field(default_factory=list)

    def registros_de(self, codigo: str) -> list:
        return [r for r in self.registros if r.codigo_asignatura == codigo]

    def convocatorias_consumidas(self, codigo: str) -> int:
        """Una convalidacion no consume convocatoria."""
        return len([r for r in self.registros_de(codigo)
                    if r.estado is not EstadoRegistro.CONVALIDADA])

    def superada(self, codigo: str) -> bool:
        return any(r.estado in (EstadoRegistro.APROBADA, EstadoRegistro.CONVALIDADA)
                   for r in self.registros_de(codigo))

    def convalidada(self, codigo: str) -> bool:
        return any(r.estado is EstadoRegistro.CONVALIDADA
                   for r in self.registros_de(codigo))

    def ultimo_intento_aprobado(self, codigo: str):
        """S2: completar este helper si la normativa acordada lo requiere."""
        raise NotImplementedError("S2: seleccionar registro tras resolver SPEC-002")


@dataclass
class SolicitudMatricula:
    estudiante_id: str
    curso_academico: str
    codigos: list
    momento: str


@dataclass
class LineaMatricula:
    codigo_asignatura: str
    creditos: int
    admitida: bool
    en_espera: bool = False
    motivo_rechazo: Optional[str] = None


@dataclass
class Matricula:
    estudiante_id: str
    curso_academico: str
    plan_aplicado: str
    version_plan_aplicada: str
    estado: EstadoMatricula
    lineas: list = field(default_factory=list)

    @property
    def creditos_admitidos(self) -> int:
        return sum(l.creditos for l in self.lineas if l.admitida)
