from dataclasses import replace

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

    assert resultado.lineas[0].admitida is True
    assert resultado.lineas[1].admitida is False
    assert resultado.creditos_admitidos == 6


def test_ventana_incluye_el_inicio():
    ventana = VentanaMatricula("2026-09-01T09:00:00", "2026-09-30T17:00:00")
    assert ventana.contiene("2026-09-01T09:00:00") is True


def test_ventana_incluye_el_fin():
    ventana = VentanaMatricula("2026-09-01T09:00:00", "2026-09-30T17:00:00")
    assert ventana.contiene("2026-09-30T17:00:00") is True


def test_ventana_excluye_un_momento_anterior():
    ventana = VentanaMatricula("2026-09-01T09:00:00", "2026-09-30T17:00:00")
    assert ventana.contiene("2026-09-01T08:59:59") is False


def test_ventana_excluye_un_momento_posterior():
    ventana = VentanaMatricula("2026-09-01T09:00:00", "2026-09-30T17:00:00")
    assert ventana.contiene("2026-09-30T17:00:01") is False


def test_grupo_tiene_plaza_si_no_esta_completo():
    assert Grupo("MAT101", capacidad=30, ocupadas=29).libre is True


def test_grupo_no_tiene_plaza_si_esta_completo():
    assert Grupo("MAT101", capacidad=30, ocupadas=30).libre is False


def test_creditos_superados_incluyen_convalidaciones():
    datos_plan = plan()
    datos_expediente = expediente(registro("MAT101", "convalidada"))

    assert creditos_superados(datos_expediente, datos_plan) == 6


def test_creditos_pendientes_restan_los_superados():
    datos_plan = plan()
    datos_expediente = expediente(registro("MAT101", "aprobada"))

    assert creditos_pendientes(datos_expediente, datos_plan) == 186


def test_prioridad_es_el_numero_de_creditos_superados():
    datos_plan = plan()
    datos_expediente = expediente(registro("MAT101", "aprobada"))

    assert prioridad(datos_expediente, datos_plan) == 6


def test_evalua_y_admite_una_asignatura_sin_prerrequisitos(tmp_path, monkeypatch):
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

    assert len(resultado.lineas) == 1
    assert resultado.lineas[0].admitida is True
    assert resultado.creditos_admitidos == 6


def test_rechaza_la_solicitud_completa_si_ventana_cerrada(tmp_path, monkeypatch):
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


def test_prerrequisito_pendiente_prevalece_sobre_grupo_lleno(tmp_path, monkeypatch):
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


def test_prioriza_mas_creditos_superados():
    datos_plan = plan()
    primero = solicitud(["MAT101"], estudiante="EST-1", momento="2026-09-02T10:00:00")
    segundo = solicitud(["MAT101"], estudiante="EST-2", momento="2026-09-01T10:00:00")
    expedientes = {
        "EST-1": expediente(
            registro("MAT101", "aprobada"),
            estudiante="EST-1",
        ),
        "EST-2": expediente(estudiante="EST-2"),
    }

    orden = ordenar_por_prioridad([segundo, primero], expedientes, datos_plan)

    assert orden[0].estudiante_id == "EST-1"


def test_prioriza_momento_mas_antiguo_si_empate():
    datos_plan = plan()
    primero = solicitud(["MAT101"], estudiante="EST-1", momento="2026-09-02T10:00:00")
    segundo = solicitud(["MAT101"], estudiante="EST-2", momento="2026-09-01T10:00:00")
    expedientes = {
        "EST-1": expediente(estudiante="EST-1"),
        "EST-2": expediente(estudiante="EST-2"),
    }

    orden = ordenar_por_prioridad([primero, segundo], expedientes, datos_plan)

    assert orden[0].estudiante_id == "EST-2"
