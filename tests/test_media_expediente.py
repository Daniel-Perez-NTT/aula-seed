"""Pruebas del cálculo del expediente según SPEC-002."""

from decimal import Decimal

from aula.reglas.media import (
    creditos_superados,
    nota_media_ponderada,
    progreso,
)
from tests.utilidades import expediente, plan, registro


def test_media_pondera_por_creditos():
    """cubre: SPEC-002/CA-01"""
    datos_plan = plan()
    datos = expediente(
        registro("MAT101", "aprobada", nota="8", convocatoria=1),
        registro("PRG101", "aprobada", nota="6", convocatoria=1),
    )

    # (8 * 6 créditos + 6 * 9 créditos) / 15 créditos = 6,80
    assert nota_media_ponderada(datos, datos_plan) == Decimal("6.80")


def test_media_usa_el_intento_aprobado_mas_reciente():
    """cubre: SPEC-002/CA-02"""
    datos_plan = plan()
    datos = expediente(
        registro("MAT101", "aprobada", nota="6", convocatoria=1),
        registro("MAT101", "suspensa", nota="4", convocatoria=2),
        registro("MAT101", "aprobada", nota="8", convocatoria=3),
    )

    assert nota_media_ponderada(datos, datos_plan) == Decimal("8.00")


def test_convalidada_no_se_incluye_en_la_media():
    """cubre: SPEC-002/CA-03"""
    datos_plan = plan()
    datos = expediente(
        registro("MAT101", "convalidada"),
        registro("PRG101", "aprobada", nota="7", convocatoria=1),
    )

    assert nota_media_ponderada(datos, datos_plan) == Decimal("7.00")


def test_media_redondea_half_up_al_final():
    """cubre: SPEC-002/CA-04"""
    datos_plan = plan()
    datos = expediente(
        registro("MAT101", "aprobada", nota="7.005", convocatoria=1),
    )

    assert nota_media_ponderada(datos, datos_plan) == Decimal("7.01")


def test_creditos_superados_cuentan_una_asignatura_una_vez():
    """cubre: SPEC-002/CA-05"""
    datos_plan = plan()
    datos = expediente(
        registro("MAT101", "suspensa", convocatoria=1),
        registro("MAT101", "aprobada", nota="6", convocatoria=2),
        registro("PRG101", "convalidada"),
    )

    assert creditos_superados(datos, datos_plan) == 15


def test_progreso_es_porcentaje_del_titulo():
    """cubre: SPEC-002/CA-06"""
    datos_plan = plan()
    datos = expediente(
        registro("MAT101", "aprobada", nota="7", convocatoria=1),
    )

    # MAT101 tiene 6 créditos y el título tiene 192: 6 / 192 * 100 = 3,13 %
    assert progreso(datos, datos_plan) == Decimal("3.13")


def test_expediente_vacio_devuelve_media_cero():
    """cubre: SPEC-002/CA-07"""
    assert nota_media_ponderada(expediente(), plan()) == Decimal("0.00")


def test_media_no_redondea_notas_intermedias():
    """cubre: SPEC-002/INV-01"""
    datos_plan = plan()
    datos = expediente(
        registro("MAT101", "aprobada", nota="7.004", convocatoria=1),
        registro("PRG101", "aprobada", nota="8.006", convocatoria=1),
    )

    esperado = (
        Decimal("7.004") * Decimal("6")
        + Decimal("8.006") * Decimal("9")
    ) / Decimal("15")

    assert nota_media_ponderada(datos, datos_plan) == esperado.quantize(
        Decimal("0.01"),
        rounding="ROUND_HALF_UP",
    )


def test_resultados_de_media_son_decimal():
    """cubre: SPEC-002/INV-02"""
    resultado = nota_media_ponderada(
        expediente(registro("MAT101", "aprobada", nota="7.5")),
        plan(),
    )

    assert isinstance(resultado, Decimal)


def test_media_no_depende_del_orden_de_los_registros():
    """cubre: SPEC-002/INV-03"""
    datos_plan = plan()
    primero = expediente(
        registro("MAT101", "aprobada", nota="7", convocatoria=1),
        registro("PRG101", "aprobada", nota="8", convocatoria=1),
    )
    invertido = expediente(
        registro("PRG101", "aprobada", nota="8", convocatoria=1),
        registro("MAT101", "aprobada", nota="7", convocatoria=1),
    )

    assert nota_media_ponderada(primero, datos_plan) == nota_media_ponderada(
        invertido, datos_plan
    )