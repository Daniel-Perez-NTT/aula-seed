from dataclasses import replace

from aula.dominio.estados import PlanInmutable, transicionar
from aula.dominio.modelos import EstadoMatricula
from aula.reglas.motor import (
    Grupo,
    VentanaCerrada,
    VentanaMatricula,
    creditos_pendientes,
    creditos_superados,
    evaluar_solicitud,
    ordenar_por_prioridad,
    prioridad,
)
from tests.utilidades import expediente, plan, registro, solicitud


def test_rechaza_creditos_que_exceden_el_limite(tmp_path, monkeypatch):
    """cubre: SPEC-001/CA-03 y SPEC-001/INV-02"""
    import aula.auditoria as auditoria

    monkeypatch.setattr(auditoria, "RUTA_TRAZA", tmp_path / "auditoria.jsonl")
    datos_plan = replace(plan(), limite_creditos_curso=10)

    resultado = evaluar_solicitud(
        solicitud(["MAT101", "PRG101"]),
        expediente(),
        datos_plan,
        VentanaMatricula("2026-09-01T00:00:00", "2027-01-01T00:00:00"),
        {},
    )

    assert len(resultado.lineas) == 2
    assert resultado.lineas[0].admitida is True
    assert resultado.lineas[1].admitida is False
    assert resultado.creditos_admitidos == 6


def test_aplica_excepcion_del_limite_de_fin_de_carrera(tmp_path, monkeypatch):
    """cubre: SPEC-001/CA-03"""
    import aula.auditoria as auditoria

    monkeypatch.setattr(auditoria, "RUTA_TRAZA", tmp_path / "auditoria.jsonl")
    datos_plan = plan()

    # Se han superado todas las asignaturas menos TFG401, que vale 12 créditos.
    registros = [
        registro(codigo, "aprobada", nota="7")
        for codigo in datos_plan.asignaturas
        if codigo != "TFG401"
    ]

    resultado = evaluar_solicitud(
        solicitud(["TFG401"]),
        expediente(*registros),
        datos_plan,
        VentanaMatricula("2026-09-01T00:00:00", "2027-01-01T00:00:00"),
        {},
    )

    assert creditos_pendientes(expediente(*registros), datos_plan) == 12
    assert resultado.lineas[0].admitida is True


def test_ventana_incluye_el_inicio():
    """cubre: SPEC-001/CA-01"""
    ventana = VentanaMatricula("2026-09-01T09:00:00", "2026-09-30T17:00:00")

    assert ventana.contiene("2026-09-01T09:00:00") is True


def test_ventana_incluye_el_fin():
    """cubre: SPEC-001/CA-01"""
    ventana = VentanaMatricula("2026-09-01T09:00:00", "2026-09-30T17:00:00")

    assert ventana.contiene("2026-09-30T17:00:00") is True


def test_ventana_excluye_un_momento_anterior():
    """cubre: SPEC-001/CA-01"""
    ventana = VentanaMatricula("2026-09-01T09:00:00", "2026-09-30T17:00:00")

    assert ventana.contiene("2026-09-01T08:59:59") is False


def test_ventana_excluye_un_momento_posterior():
    """cubre: SPEC-001/CA-01"""
    ventana = VentanaMatricula("2026-09-01T09:00:00", "2026-09-30T17:00:00")

    assert ventana.contiene("2026-09-30T17:00:01") is False


def test_grupo_tiene_plaza_si_no_esta_completo():
    grupo = Grupo("MAT101", capacidad=30, ocupadas=29)

    assert grupo.libre is True


def test_grupo_no_tiene_plaza_si_esta_completo():
    grupo = Grupo("MAT101", capacidad=30, ocupadas=30)

    assert grupo.libre is False


def test_creditos_superados_incluyen_convalidaciones():
    """cubre: SPEC-001/CA-06"""
    datos_plan = plan()
    datos_expediente = expediente(registro("MAT101", "convalidada"))

    assert creditos_superados(datos_expediente, datos_plan) == 6


def test_creditos_pendientes_restan_los_superados():
    datos_plan = plan()
    datos_expediente = expediente(registro("MAT101", "aprobada"))

    assert creditos_pendientes(datos_expediente, datos_plan) == 186


def test_prioridad_es_el_numero_de_creditos_superados():
    """cubre: SPEC-001/CA-07"""
    datos_plan = plan()
    datos_expediente = expediente(registro("MAT101", "aprobada"))

    assert prioridad(datos_expediente, datos_plan) == 6


def test_prioridad_desempata_por_momento_de_solicitud():
    """cubre: SPEC-001/CA-07"""
    datos_plan = plan()
    estudiantes = ["EST-TARDE", "EST-TEMPRANO"]

    solicitudes = [
        solicitud(
            ["MAT101"],
            momento="2026-09-10T12:00:00",
            estudiante="EST-TARDE",
        ),
        solicitud(
            ["PRG101"],
            momento="2026-09-10T09:00:00",
            estudiante="EST-TEMPRANO",
        ),
    ]
    expedientes = {
        "EST-TARDE": expediente(
            registro("MAT101", "aprobada"),
            estudiante="EST-TARDE",
        ),
        "EST-TEMPRANO": expediente(
            registro("MAT101", "aprobada"),
            estudiante="EST-TEMPRANO",
        ),
    }

    ordenadas = ordenar_por_prioridad(solicitudes, expedientes, datos_plan)

    assert [item.estudiante_id for item in ordenadas] == [
        "EST-TEMPRANO",
        "EST-TARDE",
    ]


def test_evalua_y_admite_una_asignatura_sin_prerrequisitos(tmp_path, monkeypatch):
    """cubre: SPEC-001/INV-02"""
    import aula.auditoria as auditoria

    monkeypatch.setattr(auditoria, "RUTA_TRAZA", tmp_path / "auditoria.jsonl")
    datos_plan = plan()
    peticion = solicitud(["MAT101"])

    resultado = evaluar_solicitud(
        peticion,
        expediente(),
        datos_plan,
        VentanaMatricula("2026-09-01T00:00:00", "2027-01-01T00:00:00"),
        {},
    )

    assert len(resultado.lineas) == len(peticion.codigos)
    assert resultado.lineas[0].admitida is True
    assert resultado.creditos_admitidos == 6


def test_rechaza_la_solicitud_completa_si_ventana_cerrada(tmp_path, monkeypatch):
    """cubre: SPEC-001/CA-01"""
    import aula.auditoria as auditoria

    monkeypatch.setattr(auditoria, "RUTA_TRAZA", tmp_path / "auditoria.jsonl")

    try:
        evaluar_solicitud(
            solicitud(["MAT101"], momento="2026-08-01T10:00:00"),
            expediente(),
            plan(),
            VentanaMatricula("2026-09-01T00:00:00", "2027-01-01T00:00:00"),
            {},
        )
    except VentanaCerrada:
        assert True
    else:
        assert False, "debía lanzar VentanaCerrada"


def test_rechaza_asignatura_si_falta_prerrequisito(tmp_path, monkeypatch):
    """cubre: SPEC-001/CA-02"""
    import aula.auditoria as auditoria

    monkeypatch.setattr(auditoria, "RUTA_TRAZA", tmp_path / "auditoria.jsonl")
    resultado = evaluar_solicitud(
        solicitud(["PRG102"]),
        expediente(),
        plan(),
        VentanaMatricula("2026-09-01T00:00:00", "2027-01-01T00:00:00"),
        {},
    )

    assert resultado.lineas[0].admitida is False
    assert "PRG101" in resultado.lineas[0].motivo_rechazo


def test_rechaza_asignatura_ya_superada(tmp_path, monkeypatch):
    """cubre: SPEC-001/CA-08"""
    import aula.auditoria as auditoria

    monkeypatch.setattr(auditoria, "RUTA_TRAZA", tmp_path / "auditoria.jsonl")
    resultado = evaluar_solicitud(
        solicitud(["MAT101"]),
        expediente(registro("MAT101", "aprobada")),
        plan(),
        VentanaMatricula("2026-09-01T00:00:00", "2027-01-01T00:00:00"),
        {},
    )

    assert resultado.lineas[0].admitida is False
    assert "superada" in resultado.lineas[0].motivo_rechazo


def test_grupo_lleno_deja_en_espera(tmp_path, monkeypatch):
    """cubre: SPEC-001/CA-05"""
    import aula.auditoria as auditoria

    monkeypatch.setattr(auditoria, "RUTA_TRAZA", tmp_path / "auditoria.jsonl")
    resultado = evaluar_solicitud(
        solicitud(["MAT101"]),
        expediente(),
        plan(),
        VentanaMatricula("2026-09-01T00:00:00", "2027-01-01T00:00:00"),
        {"MAT101": Grupo("MAT101", capacidad=10, ocupadas=10)},
    )

    assert resultado.lineas[0].en_espera is True
    assert resultado.creditos_admitidos == 0


def test_prerrequisito_pendiente_prevalece_sobre_grupo_lleno(
    tmp_path,
    monkeypatch,
):
    """cubre: SPEC-001/CA-02"""
    import aula.auditoria as auditoria

    monkeypatch.setattr(auditoria, "RUTA_TRAZA", tmp_path / "auditoria.jsonl")
    resultado = evaluar_solicitud(
        solicitud(["PRG102"]),
        expediente(),
        plan(),
        VentanaMatricula("2026-09-01T00:00:00", "2027-01-01T00:00:00"),
        {"PRG102": Grupo("PRG102", capacidad=10, ocupadas=10)},
    )

    assert resultado.lineas[0].en_espera is False
    assert "PRG101" in resultado.lineas[0].motivo_rechazo


def test_rechaza_asignatura_al_agotar_convocatorias(tmp_path, monkeypatch):
    """cubre: SPEC-001/CA-04"""
    import aula.auditoria as auditoria

    monkeypatch.setattr(auditoria, "RUTA_TRAZA", tmp_path / "auditoria.jsonl")
    intentos = [
        registro("MAT101", "suspensa", convocatoria=n)
        for n in range(1, 7)
    ]
    resultado = evaluar_solicitud(
        solicitud(["MAT101"]),
        expediente(*intentos),
        plan(),
        VentanaMatricula("2026-09-01T00:00:00", "2027-01-01T00:00:00"),
        {},
    )

    assert resultado.lineas[0].admitida is False
    assert "convocatorias" in resultado.lineas[0].motivo_rechazo


def test_convalidacion_no_consume_convocatoria():
    """cubre: SPEC-001/CA-04"""
    datos_expediente = expediente(
        registro("MAT101", "suspensa", convocatoria=1),
        registro("MAT101", "suspensa", convocatoria=2),
        registro("MAT101", "convalidada"),
    )

    assert datos_expediente.convocatorias_consumidas("MAT101") == 2


def test_cada_evaluacion_escribe_una_auditoria_con_plan_y_version(
    tmp_path,
    monkeypatch,
):
    """cubre: SPEC-001/INV-01"""
    import aula.auditoria as auditoria

    ruta_traza = tmp_path / "auditoria.jsonl"
    monkeypatch.setattr(auditoria, "RUTA_TRAZA", ruta_traza)

    datos_plan = plan()
    evaluar_solicitud(
        solicitud(["MAT101"]),
        expediente(),
        datos_plan,
        VentanaMatricula("2026-09-01T00:00:00", "2027-01-01T00:00:00"),
        {},
    )

    entradas = auditoria.leer_traza()

    assert len(entradas) == 1
    assert entradas[0]["plan"] == datos_plan.codigo
    assert entradas[0]["version_plan"] == datos_plan.version


def test_no_se_puede_cambiar_plan_despues_de_confirmar():
    """cubre: SPEC-001/INV-03"""
    from tests.test_estados_matricula import matricula_de_prueba

    matricula = matricula_de_prueba(EstadoMatricula.CONFIRMADA)

    try:
        transicionar(
            matricula,
            EstadoMatricula.EN_CURSO,
            nuevo_plan="PLAN-OTRO",
        )
    except PlanInmutable:
        assert matricula.plan_aplicado == "PLAN-2024"
    else:
        assert False, "el plan debía permanecer inmutable"