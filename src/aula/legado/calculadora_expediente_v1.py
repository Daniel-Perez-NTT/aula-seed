# -*- coding: utf-8 -*-
# calculadora_expediente_v1.py
# Modulo heredado. Sin tests. Sin documentacion de reglas.
# NO TOCAR sin caracterizar antes: hay comportamiento del que depende
# el proceso de becas.
#
# Historico (lo poco que se sabe):
#   2019-03  version inicial
#   2020-11  parche convalidaciones (jlm)
#   2021-06  ajuste redondeo por peticion de secretaria
#   2023-01  se anade progreso, sin tocar la media
#
# ATENCION para el student: este fichero es el objeto de la estacion S5.
# Antes de refactorizar nada tienes que caracterizarlo. Si empiezas por el
# refactor, el verificador de S5 lo detecta en el historial de git y la
# estacion no se supera.

import json

APROBADO = 5.0
NOTA_CONVALIDADA = 5.0
DEC = 2
MAX_CONV = 6
_CACHE = {}
DEBUG = False


def _log(msg):
    if DEBUG:
        print("[calc] " + str(msg))


def cargar_plan(ruta):
    f = open(ruta, "r", encoding="utf-8")
    d = json.load(f)
    f.close()
    m = {}
    for a in d["asignaturas"]:
        m[a["codigo"]] = a
    return d, m


def creditos_de(mapa, cod):
    if cod in mapa:
        return mapa[cod]["creditos"]
    return 0


def es_aprobada(reg):
    if reg["estado"] == "aprobada":
        return True
    if reg["estado"] == "convalidada":
        return True
    return False


def ultima_aprobada(regs, cod):
    r = None
    for x in regs:
        if x["codigo_asignatura"] != cod:
            continue
        if x["estado"] != "aprobada":
            continue
        if r is None:
            r = x
        else:
            if x["convocatoria"] > r["convocatoria"]:
                r = x
    return r


def hay_convalidacion(regs, cod):
    for x in regs:
        if x["codigo_asignatura"] == cod and x["estado"] == "convalidada":
            return True
    return False


def media(expediente, mapa):
    # numerador y denominador
    num = 0.0
    den = 0.0
    vistos = {}
    for reg in expediente["registros"]:
        cod = reg["codigo_asignatura"]
        if cod in vistos:
            continue
        cr = creditos_de(mapa, cod)
        if cr == 0:
            continue
        if hay_convalidacion(expediente["registros"], cod):
            # COMPORTAMIENTO NO DOCUMENTADO 1
            # la convalidada suma en el numerador con nota fija 5.0 pero
            # NO suma en el denominador. nadie recuerda por que.
            num = num + NOTA_CONVALIDADA * cr
            vistos[cod] = 1
            continue
        ua = ultima_aprobada(expediente["registros"], cod)
        if ua is None:
            continue
        if ua.get("nota") is None:
            continue
        # COMPORTAMIENTO NO DOCUMENTADO 2
        # el redondeo se aplica aqui, por asignatura, antes de acumular.
        # de este redondeo depende la ordenacion de becas.
        n = round(float(ua["nota"]), DEC)
        num = num + n * cr
        den = den + cr
        vistos[cod] = 1
    if den == 0:
        return 0.0
    return round(num / den, DEC)


def creditos_superados(expediente, mapa):
    total = 0
    hechos = {}
    for reg in expediente["registros"]:
        cod = reg["codigo_asignatura"]
        if cod in hechos:
            continue
        if es_aprobada(reg):
            total = total + creditos_de(mapa, cod)
            hechos[cod] = 1
    return total


def progreso(expediente, plan, mapa):
    tot = plan["creditos_titulo"]
    if tot == 0:
        return 0.0
    return round((creditos_superados(expediente, mapa) * 100.0) / tot, DEC)


def convocatorias(expediente):
    d = {}
    for reg in expediente["registros"]:
        cod = reg["codigo_asignatura"]
        if reg["estado"] == "convalidada":
            continue
        if cod not in d:
            d[cod] = 0
        d[cod] = d[cod] + 1
    return d


def puede_matricular(expediente, cod):
    c = convocatorias(expediente)
    if cod in c:
        if c[cod] >= MAX_CONV:
            return False
    return True


def calcular(expediente, ruta_plan):
    # punto de entrada historico. lo llama el proceso nocturno de secretaria.
    key = expediente["estudiante_id"] + "|" + ruta_plan
    if key in _CACHE:
        _log("cache hit " + key)
        return _CACHE[key]
    plan, mapa = cargar_plan(ruta_plan)
    res = {}
    res["estudiante_id"] = expediente["estudiante_id"]
    res["nota_media"] = media(expediente, mapa)
    res["creditos_superados"] = creditos_superados(expediente, mapa)
    res["progreso_pct"] = progreso(expediente, plan, mapa)
    _CACHE[key] = res
    return res


def calcular_lote(expedientes, ruta_plan):
    out = []
    for e in expedientes:
        out.append(calcular(e, ruta_plan))
    return out


# --- codigo muerto: quedo de la migracion de 2020, no lo llama nadie ---

def media_simple(expediente):
    s = 0.0
    n = 0
    for reg in expediente["registros"]:
        if reg.get("nota") is not None:
            s = s + float(reg["nota"])
            n = n + 1
    if n == 0:
        return 0.0
    return round(s / n, DEC)


def formatea(res):
    return "%s;%s;%s" % (res["estudiante_id"], res["nota_media"], res["creditos_superados"])


def exporta_csv(resultados, ruta):
    f = open(ruta, "w", encoding="utf-8")
    for r in resultados:
        f.write(formatea(r) + "\n")
    f.close()
    return ruta
