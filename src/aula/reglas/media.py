"""S2: resolver SPEC-002 antes de implementar el calculo del expediente."""
from __future__ import annotations

from decimal import Decimal

from ..dominio.modelos import Expediente, Plan


def nota_media_ponderada(expediente: Expediente, plan: Plan) -> Decimal:
    raise NotImplementedError("S2: implementar nota media tras cerrar la spec")


def creditos_superados(expediente: Expediente, plan: Plan) -> int:
    raise NotImplementedError("S2: calcular creditos superados")


def progreso(expediente: Expediente, plan: Plan) -> Decimal:
    raise NotImplementedError("S2: calcular progreso academico")


def convocatorias_por_asignatura(expediente: Expediente, plan: Plan) -> dict:
    raise NotImplementedError("S2: resumir convocatorias")


def resumen_expediente(expediente: Expediente, plan: Plan) -> dict:
    raise NotImplementedError("S2: construir respuesta de expediente")


def es_convalidada(registro) -> bool:
    raise NotImplementedError("S2: identificar registros convalidados")