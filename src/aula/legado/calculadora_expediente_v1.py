# -*- coding: utf-8 -*-
"""Calculadora modernizada de expedientes académicos."""

import json

NOTA_CONVALIDADA = 5.0
DECIMALES = 2
MAX_CONVOCATORIAS = 6
_CACHE = {}
DEBUG = False


def _log(mensaje):
    if DEBUG:
        print("[calc] " + str(mensaje))


def cargar_plan(ruta):
    """Carga el plan y crea un mapa de asignaturas por código."""
    with open(ruta, "r", encoding="utf-8") as archivo:
        plan = json.load(archivo)

    mapa = {
        asignatura["codigo"]: asignatura
        for asignatura in plan["asignaturas"]
    }
    return plan, mapa


def creditos_de(mapa, codigo):
    """Devuelve los créditos de una asignatura, o cero si no existe."""
    if codigo in mapa:
        return mapa[codigo]["creditos"]
    return 0


def es_aprobada(registro):
    """Indica si el registro cuenta como asignatura superada."""
    return registro["estado"] in {"aprobada", "convalidada"}


def ultima_aprobada(registros, codigo):
    """Devuelve la aprobación de convocatoria más alta para el código."""
    candidatas = [
        registro
        for registro in registros
        if registro["codigo_asignatura"] == codigo
        and registro["estado"] == "aprobada"
    ]

    if not candidatas:
        return None

    return max(candidatas, key=lambda registro: registro["convocatoria"])


def hay_convalidacion(registros, codigo):
    """Indica si hay algún registro convalidado para el código."""
    return any(
        registro["codigo_asignatura"] == codigo
        and registro["estado"] == "convalidada"
        for registro in registros
    )


def media(expediente, mapa):
    """Calcula la media ponderada y redondea solo el resultado final."""
    registros = expediente["registros"]
    codigos_vistos = set()
    numerador = 0.0
    denominador = 0.0

    for registro in registros:
        codigo = registro["codigo_asignatura"]

        if codigo in codigos_vistos:
            continue

        creditos = creditos_de(mapa, codigo)
        if creditos == 0:
            continue

        if hay_convalidacion(registros, codigo):
            nota = NOTA_CONVALIDADA
        else:
            aprobada = ultima_aprobada(registros, codigo)

            if aprobada is None or aprobada.get("nota") is None:
                continue

            nota = float(aprobada["nota"])

        numerador += nota * creditos
        denominador += creditos
        codigos_vistos.add(codigo)

    if denominador == 0:
        return 0.0

    return round(numerador / denominador, DECIMALES)


def creditos_superados(expediente, mapa):
    """Suma una sola vez los créditos de asignaturas superadas."""
    total = 0
    codigos_contados = set()

    for registro in expediente["registros"]:
        codigo = registro["codigo_asignatura"]

        if codigo in codigos_contados:
            continue

        if es_aprobada(registro):
            total += creditos_de(mapa, codigo)
            codigos_contados.add(codigo)

    return total


def progreso(expediente, plan, mapa):
    """Devuelve el porcentaje del título que ya está superado."""
    creditos_titulo = plan["creditos_titulo"]

    if creditos_titulo == 0:
        return 0.0

    porcentaje = creditos_superados(expediente, mapa) * 100.0
    return round(porcentaje / creditos_titulo, DECIMALES)


def convocatorias(expediente):
    """Cuenta los intentos que no sean convalidaciones."""
    resultado = {}

    for registro in expediente["registros"]:
        codigo = registro["codigo_asignatura"]

        if registro["estado"] == "convalidada":
            continue

        resultado[codigo] = resultado.get(codigo, 0) + 1

    return resultado


def puede_matricular(expediente, codigo):
    """Permite matricular si no se alcanzó el máximo de convocatorias."""
    return convocatorias(expediente).get(codigo, 0) < MAX_CONVOCATORIAS


def calcular(expediente, ruta_plan):
    """Calcula el resumen del expediente para un plan."""
    clave = expediente["estudiante_id"] + "|" + ruta_plan

    if clave in _CACHE:
        _log("cache hit " + clave)
        return _CACHE[clave]

    plan, mapa = cargar_plan(ruta_plan)
    resultado = {
        "estudiante_id": expediente["estudiante_id"],
        "nota_media": media(expediente, mapa),
        "creditos_superados": creditos_superados(expediente, mapa),
        "progreso_pct": progreso(expediente, plan, mapa),
    }

    _CACHE[clave] = resultado
    return resultado


def calcular_lote(expedientes, ruta_plan):
    """Calcula el resumen de cada expediente de la lista."""
    return [
        calcular(expediente, ruta_plan)
        for expediente in expedientes
    ]