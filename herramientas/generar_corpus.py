"""Genera el corpus sintetico de expedientes para la estacion S5.

Determinista: misma semilla, mismo corpus. Es requisito, porque el informe de
equivalencia tiene que ser reproducible por el mentor.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

SEMILLA = 20260901
N = 500
RAIZ = Path(__file__).resolve().parents[1]


def generar(n=N, semilla=SEMILLA):
    plan = json.loads((RAIZ / "datos" / "planes" / "PLAN-2024.json").read_text(encoding="utf-8"))
    codigos = [a["codigo"] for a in plan["asignaturas"]]
    rnd = random.Random(semilla)
    expedientes = []
    for i in range(n):
        registros = []
        cursadas = rnd.sample(codigos, rnd.randint(0, len(codigos)))
        for cod in cursadas:
            dado = rnd.random()
            if dado < 0.12:
                registros.append({"codigo_asignatura": cod, "curso_academico": "2024-2025",
                                  "convocatoria": 1, "estado": "convalidada", "nota": None})
                continue
            intentos = 1
            if dado < 0.35:
                intentos = rnd.randint(2, 4)
            for c in range(1, intentos):
                estado = "suspensa" if rnd.random() < 0.7 else "no_presentado"
                nota = round(rnd.uniform(0, 4.9), 3) if estado == "suspensa" else None
                registros.append({"codigo_asignatura": cod, "curso_academico": "2023-2024",
                                  "convocatoria": c, "estado": estado, "nota": nota})
            if rnd.random() < 0.85:
                registros.append({"codigo_asignatura": cod, "curso_academico": "2024-2025",
                                  "convocatoria": intentos, "estado": "aprobada",
                                  "nota": round(rnd.uniform(5.0, 10.0), 3)})
            else:
                registros.append({"codigo_asignatura": cod, "curso_academico": "2024-2025",
                                  "convocatoria": intentos, "estado": "suspensa",
                                  "nota": round(rnd.uniform(0, 4.9), 3)})
        rnd.shuffle(registros)
        expedientes.append({"estudiante_id": "EST-%04d" % i, "plan": "PLAN-2024",
                            "registros": registros})
    return expedientes


if __name__ == "__main__":
    exps = generar()
    destino = RAIZ / "datos" / "expedientes_sinteticos.json"
    destino.write_text(json.dumps(exps, ensure_ascii=False), encoding="utf-8")
    print("generados %d expedientes en %s" % (len(exps), destino))
