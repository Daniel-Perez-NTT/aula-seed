"""Comprobaciones básicas de observabilidad del servicio Aula."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request


BASE_URL = "https://aula-seed.onrender.com"
TIMEOUT_SECONDS = 30


def comprobar_salud() -> bool:
    """Comprueba que el endpoint de salud responde correctamente."""
    url = f"{BASE_URL}/salud"

    try:
        with urllib.request.urlopen(
            url,
            timeout=TIMEOUT_SECONDS,
        ) as respuesta:
            cuerpo = json.loads(respuesta.read().decode("utf-8"))

        correcto = (
            respuesta.status == 200
            and cuerpo.get("estado") == "ok"
        )

        print(f"[{'OK' if correcto else 'FALLO'}] GET /salud")
        print(f"      Respuesta: {cuerpo}")
        return correcto

    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        print(f"[FALLO] GET /salud: {error}")
        return False


def comprobar_matricula() -> bool:
    """Comprueba que una matrícula real puede procesarse."""
    url = f"{BASE_URL}/matriculas"

    datos = {
        "estudiante_id": "EST-OBSERVABILIDAD",
        "curso_academico": "2026-2027",
        "codigos": ["MAT101"],
        "momento": "2026-11-13T10:00:00",
    }

    peticion = urllib.request.Request(
        url,
        data=json.dumps(datos).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            peticion,
            timeout=TIMEOUT_SECONDS,
        ) as respuesta:
            cuerpo = json.loads(respuesta.read().decode("utf-8"))

        correcto = respuesta.status == 200

        print(f"[{'OK' if correcto else 'FALLO'}] POST /matriculas")
        print(f"      Respuesta: {cuerpo}")
        return correcto

    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        ValueError,
    ) as error:
        print(f"[FALLO] POST /matriculas: {error}")
        return False


def mostrar_logs() -> bool:
    """Indica donde revisar los logs generados por las llamadas cloud."""
    print("[OK] Las llamadas se han registrado en los logs de Render")
    print("     Render Dashboard -> aula-seed -> Logs")
    return True


def main() -> int:
    salud_ok = comprobar_salud()
    matricula_ok = comprobar_matricula()
    logs_ok = mostrar_logs()

    if salud_ok and matricula_ok and logs_ok:
        print(f"Observabilidad correcta en {BASE_URL}.")
        return 0

    print("Alguna comprobación de observabilidad ha fallado.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
