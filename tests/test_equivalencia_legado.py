import gzip
import hashlib
import json
from pathlib import Path

from aula.legado import calculadora_expediente_v1 as calc


RAIZ = Path(__file__).resolve().parents[1]
RUTA_CORPUS = RAIZ / "datos/expedientes_sinteticos.json"
RUTA_PLAN = RAIZ / "datos/planes/PLAN-2024.json"
RUTA_REFERENCIA = (
    RAIZ / "tests/fixtures/legado_corpus_referencia.json.gz"
)


def media_segun_reglas_nuevas(expediente, mapa):
    """Calcula la media esperada según las dos reglas acordadas."""
    registros = expediente["registros"]
    codigos_vistos = set()
    numerador = 0.0
    denominador = 0.0

    for registro in registros:
        codigo = registro["codigo_asignatura"]

        if codigo in codigos_vistos:
            continue

        creditos = calc.creditos_de(mapa, codigo)
        if creditos == 0:
            continue

        if calc.hay_convalidacion(registros, codigo):
            nota = 5.0
        else:
            aprobada = calc.ultima_aprobada(registros, codigo)

            if aprobada is None or aprobada.get("nota") is None:
                continue

            nota = float(aprobada["nota"])

        numerador += nota * creditos
        denominador += creditos
        codigos_vistos.add(codigo)

    if denominador == 0:
        return 0.0

    return round(numerador / denominador, 2)


def test_corpus_de_500_coincide_salvo_las_dos_reglas_documentadas():
    corpus_bytes = RUTA_CORPUS.read_bytes()
    corpus = json.loads(corpus_bytes)
    referencia = json.loads(gzip.decompress(RUTA_REFERENCIA.read_bytes()))

    assert len(corpus) == 500
    assert referencia["total_expedientes"] == 500
    assert len(referencia["resultados"]) == 500

    hash_corpus = hashlib.sha256(corpus_bytes).hexdigest()
    assert referencia["corpus_sha256"] == hash_corpus

    _, mapa = calc.cargar_plan(str(RUTA_PLAN))

    # La caché es global al módulo. La vaciamos para que cada ejecución
    # del test parta de un estado conocido.
    calc._CACHE.clear()
    resultados_nuevos = calc.calcular_lote(corpus, str(RUTA_PLAN))

    for expediente, resultado_original, resultado_nuevo in zip(
        corpus,
        referencia["resultados"],
        resultados_nuevos,
    ):
        assert resultado_nuevo["estudiante_id"] == (
            resultado_original["estudiante_id"]
        )

        esperado = dict(resultado_original)
        esperado["nota_media"] = media_segun_reglas_nuevas(
            expediente,
            mapa,
        )

        # Créditos y progreso deben seguir iguales. La media puede cambiar
        # solo según las dos reglas nuevas incluidas arriba.
        assert resultado_nuevo == esperado
