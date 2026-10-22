from fastapi.testclient import TestClient

from aula.api.app import EXPEDIENTES, MATRICULAS, app


def setup_function():
    # La app guarda los datos en memoria; cada prueba empieza limpia.
    EXPEDIENTES.clear()
    MATRICULAS.clear()


def test_api_carga_registros_y_devuelve_resumen_completo():
    """cubre: SPEC-002/CA-08, SPEC-002/CA-09"""
    cliente = TestClient(app)
    estudiante_id = "EST-API-S2"
    ruta_registros = f"/expedientes/{estudiante_id}/registros"

    registros = [
        {
            "codigo_asignatura": "MAT101",
            "curso_academico": "2024-2025",
            "convocatoria": 1,
            "estado": "aprobada",
            "nota": "8",
        },
        {
            "codigo_asignatura": "PRG101",
            "curso_academico": "2024-2025",
            "convocatoria": 1,
            "estado": "suspensa",
            "nota": "4",
        },
        {
            "codigo_asignatura": "PRG101",
            "curso_academico": "2025-2026",
            "convocatoria": 2,
            "estado": "aprobada",
            "nota": "6",
        },
        {
            "codigo_asignatura": "FIS101",
            "curso_academico": "2024-2025",
            "convocatoria": 1,
            "estado": "convalidada",
            "nota": None,
        },
    ]

    for registro in registros:
        respuesta = cliente.post(ruta_registros, json=registro)
        assert respuesta.status_code == 201

    respuesta = cliente.get(f"/expedientes/{estudiante_id}")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "estudiante_id": estudiante_id,
        "nota_media": 6.8,
        "creditos_superados": 21,
        "progreso_pct": 10.94,
        "convocatorias": {
            "MAT101": 1,
            "PRG101": 2,
        },
        "plan": {
            "codigo": "PLAN-2024",
            "version": "1.2.0",
            "creditos_titulo": 192,
        },
        "registros": [
            {
                "codigo_asignatura": "MAT101",
                "nombre_asignatura": "Matematica discreta",
                "creditos": 6,
                "curso_academico": "2024-2025",
                "convocatoria": 1,
                "estado": "aprobada",
                "nota": 8,
            },
            {
                "codigo_asignatura": "PRG101",
                "nombre_asignatura": "Programacion I",
                "creditos": 9,
                "curso_academico": "2024-2025",
                "convocatoria": 1,
                "estado": "suspensa",
                "nota": 4,
            },
            {
                "codigo_asignatura": "PRG101",
                "nombre_asignatura": "Programacion I",
                "creditos": 9,
                "curso_academico": "2025-2026",
                "convocatoria": 2,
                "estado": "aprobada",
                "nota": 6,
            },
            {
                "codigo_asignatura": "FIS101",
                "nombre_asignatura": "Fisica de computadores",
                "creditos": 6,
                "curso_academico": "2024-2025",
                "convocatoria": 1,
                "estado": "convalidada",
                "nota": None,
            },
        ],
    }


def test_consulta_de_expediente_inexistente_devuelve_404():
    cliente = TestClient(app)

    respuesta = cliente.get("/expedientes/NO-EXISTE")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "expediente no encontrado"}


def test_no_acepta_registro_de_asignatura_ajena_al_plan():
    cliente = TestClient(app)

    respuesta = cliente.post(
        "/expedientes/EST-INVALIDO/registros",
        json={
            "codigo_asignatura": "NO-EXISTE",
            "curso_academico": "2024-2025",
            "convocatoria": 1,
            "estado": "aprobada",
            "nota": "8",
        },
    )

    assert respuesta.status_code == 422
    assert "EST-INVALIDO" not in EXPEDIENTES
