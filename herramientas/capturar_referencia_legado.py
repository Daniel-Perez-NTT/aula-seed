"""Captura la salida del legado para el corpus de 500 expedientes.

Debe ejecutarse antes de modificar la calculadora heredada.
"""

import hashlib
import gzip
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
COMMIT_CARACTERIZACION = "e6068adf65180b556181fdfeeb903174438ebeb8"
ARCHIVO_LEGADO = "src/aula/legado/calculadora_expediente_v1.py"
HUELLA_LEGADO_ORIGINAL = "343eebf51fc64155d95dbe048a93a1e739822d9f"
ARCHIVO_CORPUS = RAIZ / "datos/expedientes_sinteticos.json"
ARCHIVO_PLAN = RAIZ / "datos/planes/PLAN-2024.json"
ARCHIVO_SALIDA = RAIZ / "tests/fixtures/legado_corpus_referencia.json.gz"

sys.path.insert(0, str(RAIZ / "src"))

from aula.legado import calculadora_expediente_v1 as legado


def ejecutar_git(*argumentos):
    return subprocess.run(
        ["git", *argumentos],
        cwd=RAIZ,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main():
    # Evita capturar como referencia una calculadora que ya se haya modificado.
    blob_actual = subprocess.run(
        ["git", "hash-object", ARCHIVO_LEGADO],
        cwd=RAIZ,
        check=True,
        capture_output=True,
        text=True,
    )
    if blob_actual.stdout.strip() != HUELLA_LEGADO_ORIGINAL:
        raise SystemExit(
            "La calculadora no coincide con la versión original caracterizada. "
            "No se ha generado la referencia."
        )

    corpus_bytes = ARCHIVO_CORPUS.read_bytes()
    corpus = json.loads(corpus_bytes)

    if len(corpus) != 500:
        raise SystemExit(
            f"El corpus debe contener 500 expedientes; contiene {len(corpus)}."
        )

    # Limpiamos la caché para que esta captura comience desde cero.
    legado._CACHE.clear()

    resultados = legado.calcular_lote(corpus, str(ARCHIVO_PLAN))

    referencia = {
        "origen_commit": COMMIT_CARACTERIZACION,
        "origen_blob_legado": ejecutar_git(
            "rev-parse",
            f"{COMMIT_CARACTERIZACION}:{ARCHIVO_LEGADO}",
        ),
        "corpus_sha256": hashlib.sha256(corpus_bytes).hexdigest(),
        "plan_sha256": hashlib.sha256(ARCHIVO_PLAN.read_bytes()).hexdigest(),
        "total_expedientes": len(corpus),
        "resultados": resultados,
    }

    referencia_json = json.dumps(
        referencia,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVO_SALIDA.write_bytes(
        gzip.compress(referencia_json.encode("utf-8"), mtime=0)
    )

    print(f"Referencia creada: {ARCHIVO_SALIDA.relative_to(RAIZ)}")
    print(f"Expedientes calculados: {len(resultados)}")
    print(f"SHA-256 del corpus: {referencia['corpus_sha256']}")


if __name__ == "__main__":
    main()
