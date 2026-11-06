from aula.legado import calculadora_expediente_v1 as calc


def registro(codigo, estado, convocatoria=1, nota=None):
    return {
        "codigo_asignatura": codigo,
        "estado": estado,
        "convocatoria": convocatoria,
        "nota": nota,
    }


def expediente(*registros, estudiante_id="EST-001"):
    return {
        "estudiante_id": estudiante_id,
        "registros": list(registros),
    }


MAPA = {
    "MAT101": {"codigo": "MAT101", "creditos": 6},
    "PRG101": {"codigo": "PRG101", "creditos": 9},
    "FIS101": {"codigo": "FIS101", "creditos": 6},
}


def test_es_aprobada_reconoce_aprobada_y_convalidada():
    assert calc.es_aprobada(registro("MAT101", "aprobada", nota=6))
    assert calc.es_aprobada(registro("MAT101", "convalidada"))
    assert not calc.es_aprobada(registro("MAT101", "suspensa", nota=4))


def test_creditos_de_asignatura_desconocida_es_cero():
    assert calc.creditos_de(MAPA, "NO-EXISTE") == 0


def test_ultima_aprobada_elige_la_convocatoria_mas_alta():
    primera = registro("MAT101", "aprobada", convocatoria=1, nota=6)
    suspendida = registro("MAT101", "suspensa", convocatoria=2, nota=3)
    ultima = registro("MAT101", "aprobada", convocatoria=3, nota=8)

    assert calc.ultima_aprobada(
        [primera, suspendida, ultima], "MAT101"
    ) == ultima


def test_ultima_aprobada_devuelve_none_si_no_hay_aprobadas():
    registros = [
        registro("MAT101", "suspensa", convocatoria=1, nota=4),
        registro("MAT101", "matriculada", convocatoria=2),
    ]

    assert calc.ultima_aprobada(registros, "MAT101") is None


def test_hay_convalidacion_detecta_convalidacion_de_la_asignatura():
    registros = [
        registro("MAT101", "suspensa", nota=4),
        registro("PRG101", "convalidada"),
    ]

    assert calc.hay_convalidacion(registros, "PRG101")
    assert not calc.hay_convalidacion(registros, "MAT101")


def test_media_sin_registros_es_cero():
    assert calc.media({"registros": []}, MAPA) == 0.0


def test_media_pondera_las_notas_por_creditos():
    datos = expediente(
        registro("MAT101", "aprobada", nota=8),
        registro("PRG101", "aprobada", nota=6),
    )

    # (8 * 6 + 6 * 9) / (6 + 9) = 6.80
    assert calc.media(datos, MAPA) == 6.8


def test_media_usa_la_nota_de_la_ultima_convocatoria_aprobada():
    datos = expediente(
        registro("MAT101", "aprobada", convocatoria=1, nota=6),
        registro("MAT101", "suspensa", convocatoria=2, nota=3),
        registro("MAT101", "aprobada", convocatoria=3, nota=8),
    )

    assert calc.media(datos, MAPA) == 8.0


def test_media_ignora_asignaturas_desconocidas_y_notas_ausentes():
    datos = expediente(
        registro("NO-EXISTE", "aprobada", nota=10),
        registro("MAT101", "aprobada", nota=None),
    )

    assert calc.media(datos, MAPA) == 0.0


def test_media_sin_creditos_en_el_denominador_es_cero():
    datos = expediente(registro("MAT101", "convalidada"))

    assert calc.media(datos, MAPA) == 0.0


def test_no_documentado_1_convalidada_aporta_al_numerador_no_al_denominador():
    datos = expediente(
        registro("MAT101", "convalidada"),
        registro("PRG101", "aprobada", nota=8),
    )

    # MAT101 aporta 5 * 6 = 30 al numerador, pero sus créditos no
    # entran en el denominador. Resultado: (30 + 8 * 9) / 9 = 11.33.
    assert calc.media(datos, MAPA) == 11.33


def test_no_documentado_2_redondea_cada_nota_antes_de_promediar():
    datos = expediente(
        registro("MAT101", "aprobada", nota=1.0),
        registro("FIS101", "aprobada", nota=1.007),
    )

    # El legado redondea las notas a 1.00 y 1.01 antes de promediarlas,
    # por eso obtiene 1.01. Si promediara las notas originales primero,
    # obtendría 1.00.
    assert calc.media(datos, MAPA) == 1.01


def test_creditos_superados_cuenta_una_sola_vez_por_asignatura():
    datos = expediente(
        registro("MAT101", "aprobada", convocatoria=1, nota=6),
        registro("MAT101", "aprobada", convocatoria=2, nota=7),
        registro("PRG101", "convalidada"),
        registro("FIS101", "suspensa", nota=4),
    )

    # MAT101 suma 6, PRG101 suma 9 por estar convalidada y FIS101 no suma.
    assert calc.creditos_superados(datos, MAPA) == 15


def test_creditos_superados_no_suma_creditos_de_codigo_desconocido():
    datos = expediente(
        registro("NO-EXISTE", "aprobada", nota=10),
    )

    assert calc.creditos_superados(datos, MAPA) == 0


def test_progreso_es_porcentaje_de_creditos_superados_sobre_el_titulo():
    datos = expediente(registro("MAT101", "aprobada", nota=6))
    plan = {"creditos_titulo": 192}

    # 6 / 192 * 100 = 3.125; el redondeo de Python da 3.12.
    assert calc.progreso(datos, plan, MAPA) == 3.12


def test_progreso_con_titulo_de_cero_creditos_es_cero():
    datos = expediente(registro("MAT101", "aprobada", nota=6))
    plan = {"creditos_titulo": 0}

    assert calc.progreso(datos, plan, MAPA) == 0.0


def test_convocatorias_cuenta_registros_no_convalidados():
    datos = expediente(
        registro("MAT101", "suspensa", convocatoria=1, nota=4),
        registro("MAT101", "aprobada", convocatoria=2, nota=6),
        registro("PRG101", "convalidada"),
    )

    assert calc.convocatorias(datos) == {"MAT101": 2}


def test_puede_matricular_hasta_cinco_convocatorias():
    datos = expediente(
        *[
            registro("MAT101", "suspensa", convocatoria=n, nota=4)
            for n in range(1, 6)
        ]
    )

    assert calc.puede_matricular(datos, "MAT101")


def test_puede_matricular_bloquea_al_llegar_a_seis_convocatorias():
    datos = expediente(
        *[
            registro("MAT101", "suspensa", convocatoria=n, nota=4)
            for n in range(1, 7)
        ]
    )

    assert not calc.puede_matricular(datos, "MAT101")


def test_convocatoria_convalidada_no_cuenta_para_el_limite():
    datos = expediente(
        registro("MAT101", "convalidada"),
    )

    assert calc.puede_matricular(datos, "MAT101")


def test_calcular_devuelve_el_resumen_y_lo_guarda_en_cache(monkeypatch):
    ruta = "plan-test.json"
    plan = {
        "creditos_titulo": 192,
        "asignaturas": [
            {"codigo": "MAT101", "creditos": 6},
        ],
    }
    mapa = {"MAT101": {"codigo": "MAT101", "creditos": 6}}

    monkeypatch.setattr(calc, "cargar_plan", lambda _ruta: (plan, mapa))
    calc._CACHE.clear()

    datos = expediente(
        registro("MAT101", "aprobada", nota=8),
        estudiante_id="EST-CACHE-1",
    )

    resultado = calc.calcular(datos, ruta)

    assert resultado == {
        "estudiante_id": "EST-CACHE-1",
        "nota_media": 8.0,
        "creditos_superados": 6,
        "progreso_pct": 3.12,
    }
    assert calc._CACHE["EST-CACHE-1|" + ruta] is resultado


def test_calcular_reutiliza_cache_por_estudiante_y_ruta(monkeypatch):
    ruta = "plan-test.json"
    plan = {"creditos_titulo": 192}
    mapa = {"MAT101": {"codigo": "MAT101", "creditos": 6}}

    monkeypatch.setattr(calc, "cargar_plan", lambda _ruta: (plan, mapa))
    calc._CACHE.clear()

    primero = expediente(
        registro("MAT101", "aprobada", nota=8),
        estudiante_id="EST-CACHE-2",
    )
    segundo = expediente(
        registro("MAT101", "aprobada", nota=4),
        estudiante_id="EST-CACHE-2",
    )

    resultado_primero = calc.calcular(primero, ruta)
    resultado_segundo = calc.calcular(segundo, ruta)

    # La segunda llamada devuelve el resultado cacheado, aunque cambien
    # los registros del expediente. También es el mismo objeto.
    assert resultado_segundo is resultado_primero
    assert resultado_segundo["nota_media"] == 8.0
