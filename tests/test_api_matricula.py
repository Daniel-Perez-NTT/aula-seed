from fastapi.testclient import TestClient

from aula.api.app import app, EXPEDIENTES, MATRICULAS


def setup_function():
    EXPEDIENTES.clear()
    MATRICULAS.clear()


def test_post_matricula_devuelve_una_linea_por_codigo():
    cliente = TestClient(app)

    respuesta = cliente.post(
        "/matriculas",
        json={
            "estudiante_id": "EST-API-01",
            "curso_academico": "2026-2027",
            "codigos": ["MAT101"],
            "momento": "2026-09-10T10:00:00",
        },
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estudiante_id"] == "EST-API-01"
    assert len(cuerpo["lineas"]) == 1


def test_post_matricula_rechaza_codigos_repetidos():
    cliente = TestClient(app)

    respuesta = cliente.post(
        "/matriculas",
        json={
            "estudiante_id": "EST-API-02",
            "curso_academico": "2026-2027",
            "codigos": ["MAT101", "MAT101"],
            "momento": "2026-09-10T10:00:00",
        },
    )

    assert respuesta.status_code == 422


def test_post_matricula_rechaza_ventana_cerrada():
    cliente = TestClient(app)

    respuesta = cliente.post(
        "/matriculas",
        json={
            "estudiante_id": "EST-API-03",
            "curso_academico": "2026-2027",
            "codigos": ["MAT101"],
            "momento": "2025-09-10T10:00:00",
        },
    )

    assert respuesta.status_code == 409
