from aula.dominio.estados import (
    PlanInmutable,
    TransicionInvalida,
    transicionar,
)
from aula.dominio.modelos import EstadoMatricula, Matricula


def matricula_de_prueba(estado=EstadoMatricula.SOLICITADA):
    return Matricula(
        estudiante_id="EST-0001",
        curso_academico="2026-2027",
        plan_aplicado="PLAN-2024",
        version_plan_aplicada="1.2.0",
        estado=estado,
    )


def test_no_permite_saltar_desde_solicitada_a_calificada():
    try:
        transicionar(matricula_de_prueba(), EstadoMatricula.CALIFICADA)
    except TransicionInvalida:
        assert True
    else:
        assert False, "la transición debía ser inválida"


def test_no_cambia_el_plan_despues_de_confirmar():
    try:
        transicionar(
            matricula_de_prueba(EstadoMatricula.CONFIRMADA),
            EstadoMatricula.EN_CURSO,
            nuevo_plan="PLAN-OTRO",
        )
    except PlanInmutable:
        assert True
    else:
        assert False, "el plan debía permanecer inmutable"
