"""Reglas de matrícula definidas por SPEC-001."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from ..auditoria import registrar_decision
from ..dominio.modelos import (
    EstadoMatricula,
    LineaMatricula,
    Matricula,
)


class VentanaCerrada(Exception):
    """La solicitud se recibió fuera del periodo de matrícula."""


@dataclass(frozen=True)
class VentanaMatricula:
    inicio: str
    fin: str

    def contiene(self, momento: str) -> bool:
        inicio = _fecha(self.inicio)
        fin = _fecha(self.fin)
        instante = _fecha(momento)
        return inicio <= instante <= fin


@dataclass(frozen=True)
class Grupo:
    codigo_asignatura: str
    capacidad: int
    ocupadas: int

    @property
    def libre(self) -> bool:
        return self.ocupadas < self.capacidad


def _fecha(valor: str) -> datetime:
    fecha = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)
    return fecha.astimezone(timezone.utc)


def creditos_superados(expediente, plan) -> int:
    return sum(
        asignatura.creditos
        for codigo, asignatura in plan.asignaturas.items()
        if expediente.superada(codigo)
    )


def creditos_pendientes(expediente, plan) -> int:
    return max(plan.creditos_titulo - creditos_superados(expediente, plan), 0)


def prioridad(expediente, plan) -> int:
    return creditos_superados(expediente, plan)


def evaluar_solicitud(solicitud, expediente, plan, ventana, grupos) -> Matricula:
    resultado_auditoria = {}
    try:
        if not solicitud.codigos:
            raise ValueError("la solicitud debe incluir al menos un código")
        if len(set(solicitud.codigos)) != len(solicitud.codigos):
            raise ValueError("la solicitud no puede repetir códigos")

        if not ventana.contiene(solicitud.momento):
            raise VentanaCerrada("ventana de matrícula cerrada")

        pendientes = creditos_pendientes(expediente, plan)
        if pendientes <= plan.umbral_final_carrera:
            limite = pendientes
        else:
            limite = plan.limite_creditos_curso

        lineas = []
        creditos_admitidos = 0

        for codigo in solicitud.codigos:
            try:
                asignatura = plan.asignatura(codigo)
            except KeyError:
                lineas.append(LineaMatricula(
                    codigo_asignatura=codigo,
                    creditos=0,
                    admitida=False,
                    motivo_rechazo="asignatura desconocida en el plan",
                ))
                continue

            motivo = None
            en_espera = False

            if expediente.superada(codigo):
                motivo = "asignatura ya superada"
            else:
                requisitos_pendientes = [
                    requisito
                    for requisito in asignatura.prerrequisitos
                    if not expediente.superada(requisito)
                ]
                if requisitos_pendientes:
                    motivo = "prerrequisitos pendientes: " + ", ".join(
                        requisitos_pendientes
                    )
                elif expediente.convocatorias_consumidas(codigo) >= plan.max_convocatorias:
                    motivo = "convocatorias agotadas"
                elif codigo in grupos and not grupos[codigo].libre:
                    en_espera = True
                elif creditos_admitidos + asignatura.creditos > limite:
                    motivo = "se supera el límite de créditos"

            admitida = motivo is None and not en_espera
            if admitida:
                creditos_admitidos += asignatura.creditos

            lineas.append(LineaMatricula(
                codigo_asignatura=codigo,
                creditos=asignatura.creditos,
                admitida=admitida,
                en_espera=en_espera,
                motivo_rechazo=motivo,
            ))

        matricula = Matricula(
            estudiante_id=solicitud.estudiante_id,
            curso_academico=solicitud.curso_academico,
            plan_aplicado=plan.codigo,
            version_plan_aplicada=plan.version,
            estado=EstadoMatricula.VALIDADA,
            lineas=lineas,
        )
        resultado_auditoria = {
            "estado": matricula.estado.value,
            "lineas": [
                {
                    "codigo": linea.codigo_asignatura,
                    "admitida": linea.admitida,
                    "en_espera": linea.en_espera,
                    "motivo": linea.motivo_rechazo,
                }
                for linea in lineas
            ],
        }
        return matricula
    except Exception as exc:
        resultado_auditoria = {"error": type(exc).__name__, "detalle": str(exc)}
        raise
    finally:
        registrar_decision(
            solicitud.estudiante_id,
            solicitud.curso_academico,
            plan.codigo,
            plan.version,
            solicitud.momento,
            resultado_auditoria,
        )


def ordenar_por_prioridad(solicitudes: list, expedientes: dict, plan) -> list:
    return sorted(
        solicitudes,
        key=lambda item: (
            -prioridad(expedientes[item.estudiante_id], plan),
            item.momento,
        ),
    )