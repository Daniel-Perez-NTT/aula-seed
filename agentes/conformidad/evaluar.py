"""Evaluacion del agente de conformidad contra el conjunto dorado.

Umbrales de la estacion S4a: precision >= 0,80 y recall >= 0,85 sobre la
deteccion de no conformidad.

Definiciones usadas, explicitas para que nadie las interprete a su manera:
  positivo   = el agente dice "no conforme"
  verdadero  = la etiqueta del conjunto dorado empieza por "no_conforme"
  precision  = aciertos entre todo lo que el agente marco como no conforme
  recall     = aciertos entre todo lo que realmente era no conforme

En el laboratorio real este conjunto NO vive en el repositorio del student:
se ejecuta como flujo reutilizable de la organizacion y el student recibe las
metricas sin ver las etiquetas. La copia de `evals/dorado_ejemplo` esta aqui
para que la referencia sea ejecutable de forma autonoma.

Uso:
    python3 -m agentes.conformidad.evaluar
    python3 -m agentes.conformidad.evaluar --dorado evals/dorado_ejemplo --guardar
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import date
from pathlib import Path

from .agente import NO_CONFORME, evaluar

RAIZ = Path(__file__).resolve().parents[2]


def es_no_conforme(etiqueta: str) -> bool:
    return etiqueta.startswith("no_conforme")


def ejecutar(directorio: Path) -> dict:
    etiquetas = json.loads((directorio / "etiquetas.json").read_text(encoding="utf-8"))
    vp = fp = vn = fn = 0
    detalle, latencias = [], []

    for ident, etiqueta in sorted(etiquetas.items()):
        caso = json.loads((directorio / ("%s.json" % ident)).read_text(encoding="utf-8"))
        t0 = time.perf_counter()
        v = evaluar(caso, caso.get("spec", "SPEC-002"))
        latencias.append((time.perf_counter() - t0) * 1000)

        predicho = v.veredicto == NO_CONFORME
        real = es_no_conforme(etiqueta)
        if predicho and real:
            vp += 1
            resultado = "acierto"
        elif predicho and not real:
            fp += 1
            resultado = "falso positivo"
        elif not predicho and real:
            fn += 1
            resultado = "falso negativo"
        else:
            vn += 1
            resultado = "acierto"
        detalle.append({"caso": ident, "esperado": etiqueta, "obtenido": v.veredicto,
                        "resultado": resultado})

    precision = vp / (vp + fp) if (vp + fp) else 0.0
    recall = vp / (vp + fn) if (vp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return {
        "fecha": date.today().isoformat(),
        "casos": len(etiquetas),
        "matriz": {"vp": vp, "fp": fp, "vn": vn, "fn": fn},
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "latencia_media_ms": round(sum(latencias) / len(latencias), 1) if latencias else 0.0,
        "coste_usd_por_ejecucion": 0.0,
        "juez": "offline",
        "detalle": detalle,
    }


def principal(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dorado", default="evals/dorado_ejemplo")
    ap.add_argument("--guardar", action="store_true",
                    help="escribe el informe en evals/informes/")
    args = ap.parse_args(argv)

    directorio = RAIZ / args.dorado
    if not (directorio / "etiquetas.json").is_file():
        print("Evaluacion privada no configurada. El conjunto dorado no se entrega "
              "en la semilla; solicita al mentor el informe de evaluacion externa.")
        return 2
    informe = ejecutar(directorio)
    print(json.dumps({k: v for k, v in informe.items() if k != "detalle"},
                     ensure_ascii=False, indent=2))
    fallos = [d for d in informe["detalle"] if d["resultado"] != "acierto"]
    if fallos:
        print("\nCasos fallados:")
        for f in fallos:
            print("  %s: esperado %s, obtenido %s (%s)"
                  % (f["caso"], f["esperado"], f["obtenido"], f["resultado"]))

    if args.guardar:
        destino = RAIZ / "evals" / "informes"
        destino.mkdir(parents=True, exist_ok=True)
        ruta = destino / ("evaluacion-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
        ruta.write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
        print("\ninforme guardado en %s" % ruta.relative_to(RAIZ))

    ok = informe["precision"] >= 0.80 and informe["recall"] >= 0.85
    print("\numbrales de S4a: %s" % ("SUPERADOS" if ok else "NO SUPERADOS"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(principal())
