"""Cálculos del expediente académico definidos en SPEC-002."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from ..dominio.modelos import EstadoRegistro, Expediente, Plan


DOS_DECIMALES = Decimal("0.01")


def es_convalidada(registro) -> bool:
    """Indica si el registro representa una convalidación."""
    return registro.estado is EstadoRegistro.CONVALIDADA


def nota_media_ponderada(expediente: Expediente, plan: Plan) -> Decimal:
    """Calcula la media ponderada usando el último intento aprobado."""
    numerador = Decimal("0")
    denominador = Decimal("0")
    codigos = {registro.codigo_asignatura for registro in expediente.registros}

    for codigo in codigos:
        if expediente.convalidada(codigo):
            continue

        ultimo = expediente.ultimo_intento_aprobado(codigo)
        if ultimo is None or ultimo.nota is None:
            continue

        creditos = plan.asignatura(codigo).creditos
        numerador += ultimo.nota * Decimal(creditos)
        denominador += Decimal(creditos)

    if denominador == 0:
        return Decimal("0.00")

    return (numerador / denominador).quantize(
        DOS_DECIMALES,
        rounding=ROUND_HALF_UP,
    )


def creditos_superados(expediente: Expediente, plan: Plan) -> int:
    """Suma una vez los créditos de cada asignatura superada."""
    codigos_superados = {
        registro.codigo_asignatura
        for registro in expediente.registros
        if registro.estado in (
            EstadoRegistro.APROBADA,
            EstadoRegistro.CONVALIDADA,
        )
    }

    return sum(plan.asignatura(codigo).creditos for codigo in codigos_superados)


def progreso(expediente: Expediente, plan: Plan) -> Decimal:
    """Calcula el porcentaje del título completado."""
    if plan.creditos_titulo == 0:
        return Decimal("0.00")

    porcentaje = (
        Decimal(creditos_superados(expediente, plan)) * Decimal("100")
        / Decimal(plan.creditos_titulo)
    )
    return porcentaje.quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)


def convocatorias_por_asignatura(expediente: Expediente, plan: Plan) -> dict:
    """Devuelve cuántas convocatorias consumió cada asignatura."""
    resultado = {}

    for registro in expediente.registros:
        if es_convalidada(registro):
            continue
        codigo = registro.codigo_asignatura
        resultado[codigo] = resultado.get(codigo, 0) + 1

    return resultado


def resumen_expediente(expediente: Expediente, plan: Plan) -> dict:
    """Devuelve los cálculos principales del expediente."""
    return {
        "estudiante_id": expediente.estudiante_id,
        "nota_media": nota_media_ponderada(expediente, plan),
        "creditos_superados": creditos_superados(expediente, plan),
        "progreso_pct": progreso(expediente, plan),
        "convocatorias": convocatorias_por_asignatura(expediente, plan),
    }