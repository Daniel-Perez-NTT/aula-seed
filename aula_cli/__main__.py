"""CLI del laboratorio.

    aula estado                     estacion actual y criterios pendientes
    aula guia [ID]                  abre la guia de la estacion
    aula check [ID] [--prediccion pasa|falla]
    aula pista [ID]                 siguiente escalon de pista
    aula bitacora "texto"           anota en el cuaderno de la estacion
    aula cerrar [ID]                sella la estacion si el verificador esta verde
    aula desbloquear [ID] --motivo "..."
    aula panel                      vista agregada, la usa el Lead

El progreso vive en `.aula/progreso.json`, versionado en el repo. El fichero es
la evidencia: no hay panel paralelo ni hoja de calculo aparte.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PROGRESO = RAIZ / ".aula" / "progreso.json"

ESTACIONES = [
    ("S0", "Bootstrap y disciplina de repositorio", 8),
    ("S1", "Rebanada vertical a mano", 24),
    ("S2", "Spec-Driven Development", 26),
    ("S3", "Ingenieria de contexto y operacion de agentes", 24),
    ("S4a", "Servidor MCP y agente propio", 28),
    ("S4b", "Flotilla multiagente", 12),
    ("S5", "Modernizacion del legado con agentes", 22),
    ("S6", "Gobierno del agente", 18),
    ("S7", "Despliegue, fallo inducido y MTTR", 24),
    ("S8", "Defensa ante panel", 10),
]
IDS = [e[0] for e in ESTACIONES]
NOMBRES = {e[0]: e[1] for e in ESTACIONES}

VERDE, ROJO, GRIS, AMARILLO, RESET = "\033[32m", "\033[31m", "\033[90m", "\033[33m", "\033[0m"


def ahora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def cargar():
    if PROGRESO.exists():
        return json.loads(PROGRESO.read_text(encoding="utf-8"))
    return {"student": "sin-asignar", "estaciones": {}, "creado": ahora()}


def guardar(datos):
    PROGRESO.parent.mkdir(parents=True, exist_ok=True)
    PROGRESO.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def estado_de(datos, ident):
    return datos["estaciones"].setdefault(ident, {
        "estado": "pendiente", "pistas": 0, "intentos": 0,
        "predicciones": {"aciertos": 0, "total": 0},
        "desbloqueada": False, "sellada": None,
    })


def activa(datos):
    for ident in IDS:
        e = datos["estaciones"].get(ident, {})
        if e.get("estado") != "sellada":
            return ident
    return IDS[-1]


def carpeta(ident):
    for d in (RAIZ / "labs").iterdir():
        if d.is_dir() and d.name.split("-")[0] == ident:
            return d
    raise SystemExit("no existe carpeta de laboratorio para %s" % ident)


def cargar_verificador(ident):
    ruta = carpeta(ident) / "verificar.py"
    if not ruta.exists():
        return None
    spec = importlib.util.spec_from_file_location("verificador_%s" % ident, ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(RAIZ))
    spec.loader.exec_module(modulo)
    return modulo


# --- comandos -----------------------------------------------------------------

def cmd_estado(args):
    datos = cargar()
    actual = activa(datos)
    print("\nProyecto Aula, laboratorio del AoE Agentic DevOps")
    print("student: %s\n" % datos.get("student", "sin-asignar"))
    for ident, nombre, horas in ESTACIONES:
        e = datos["estaciones"].get(ident, {})
        est = e.get("estado", "pendiente")
        if est == "sellada":
            marca = VERDE + "sellada  " + RESET
        elif e.get("desbloqueada"):
            marca = AMARILLO + "desbloq. " + RESET
        elif ident == actual:
            marca = ROJO + "EN CURSO " + RESET
        else:
            marca = GRIS + "pendiente" + RESET
        extra = ""
        if e.get("pistas"):
            extra += "  pistas: %d" % e["pistas"]
        if e.get("intentos"):
            extra += "  intentos: %d" % e["intentos"]
        print("  %-4s %s  %-46s %2dh%s" % (ident, marca, nombre, horas, extra))
    p = calibracion(datos)
    if p["total"]:
        print("\ncalibracion: %d de %d predicciones acertadas (%.0f%%)"
              % (p["aciertos"], p["total"], 100.0 * p["aciertos"] / p["total"]))
    print()


def calibracion(datos):
    a = t = 0
    for e in datos["estaciones"].values():
        a += e.get("predicciones", {}).get("aciertos", 0)
        t += e.get("predicciones", {}).get("total", 0)
    return {"aciertos": a, "total": t}


def cmd_guia(args):
    ident = args.estacion or activa(cargar())
    ruta = carpeta(ident) / "GUIA.md"
    print(ruta.read_text(encoding="utf-8"))


def cmd_check(args):
    datos = cargar()
    ident = args.estacion or activa(datos)
    e = estado_de(datos, ident)
    modulo = cargar_verificador(ident)
    if modulo is None:
        print("la estacion %s no tiene verificador automatico: se cierra con el mentor" % ident)
        return 0

    print("\nverificando %s: %s\n" % (ident, NOMBRES[ident]))
    criterios = modulo.verificar()
    ok_total = True
    for c in criterios:
        marca = (VERDE + "  OK  " + RESET) if c["ok"] else (ROJO + " FALLA" + RESET)
        print("%s %-10s %s" % (marca, c["id"], c["descripcion"]))
        if not c["ok"] and c.get("detalle"):
            print("        %s%s%s" % (GRIS, c["detalle"], RESET))
        ok_total = ok_total and c["ok"]

    e["intentos"] += 1
    if args.prediccion:
        acierto = (args.prediccion == "pasa") == ok_total
        e["predicciones"]["total"] += 1
        e["predicciones"]["aciertos"] += 1 if acierto else 0
        print("\nprediccion '%s': %s" % (args.prediccion, "acertada" if acierto else "fallada"))
    e["estado"] = "superable" if ok_total else "en curso"
    guardar(datos)

    print("\n%s\n" % ("todos los criterios en verde, puedes ejecutar 'aula cerrar %s'" % ident
                      if ok_total else "quedan criterios en rojo"))
    return 0 if ok_total else 1


def cmd_pista(args):
    datos = cargar()
    ident = args.estacion or activa(datos)
    e = estado_de(datos, ident)
    siguiente = e["pistas"] + 1
    ruta = carpeta(ident) / "pistas"
    disponibles = sorted(ruta.glob("*.md")) if ruta.exists() else []
    if siguiente > len(disponibles):
        print("no quedan pistas en %s. Publica en el canal de la cohorte con el formato "
              "de tres lineas, o usa 'aula desbloquear'." % ident)
        return 1
    e["pistas"] = siguiente
    guardar(datos)
    print("\n[pista %d de %d en %s]\n" % (siguiente, len(disponibles), ident))
    print(disponibles[siguiente - 1].read_text(encoding="utf-8"))
    return 0


def cmd_bitacora(args):
    datos = cargar()
    ident = args.estacion or activa(datos)
    ruta = carpeta(ident) / "bitacora.md"
    cabecera = "" if ruta.exists() else "# Bitacora de %s\n\n" % ident
    with ruta.open("a", encoding="utf-8") as fh:
        fh.write("%s- %s  %s\n" % (cabecera, ahora(), args.texto))
    print("anotado en %s" % ruta.relative_to(RAIZ))


def cmd_cerrar(args):
    datos = cargar()
    ident = args.estacion or activa(datos)
    e = estado_de(datos, ident)
    modulo = cargar_verificador(ident)
    if modulo is not None:
        criterios = modulo.verificar()
        fallos = [c for c in criterios if not c["ok"]]
        if fallos:
            print("no se puede cerrar %s: %d criterios en rojo" % (ident, len(fallos)))
            for c in fallos:
                print("  - %s %s" % (c["id"], c["descripcion"]))
            return 1
    e["estado"] = "sellada"
    e["sellada"] = ahora()
    guardar(datos)
    ref = carpeta(ident) / "referencia"
    print("\nestacion %s sellada." % ident)
    if ref.exists():
        print("referencia entregada por el mentor en %s" % ref.relative_to(RAIZ))
    else:
        print("solicita al mentor la referencia para comparar; no se descarga automaticamente")
    print("siguiente estacion: %s\n" % activa(datos))
    return 0


def cmd_desbloquear(args):
    datos = cargar()
    ident = args.estacion or activa(datos)
    e = estado_de(datos, ident)
    e["desbloqueada"] = True
    e["estado"] = "sellada"
    e["sellada"] = ahora()
    e["motivo_desbloqueo"] = args.motivo
    guardar(datos)
    print("\n%s desbloqueada. Motivo registrado: %s" % (ident, args.motivo))
    print("el desbloqueo no descarga ni aplica archivos: solicita al mentor la referencia "
          "de %s y conserva tu trabajo antes de incorporarla." % ident)
    print("siguiente estacion: %s; incorpora primero la base acordada con el mentor."
          % activa(datos))
    print("esto no penaliza las estaciones siguientes. Lo que se evalua es la "
          "bitacora de lo que intentaste antes.\n")
    return 0


def cmd_panel(args):
    datos = cargar()
    fila = {"student": datos.get("student"), "estacion_actual": activa(datos)}
    for ident in IDS:
        e = datos["estaciones"].get(ident, {})
        fila[ident] = e.get("estado", "pendiente") + ("*" if e.get("desbloqueada") else "")
    fila["calibracion"] = calibracion(datos)
    print(json.dumps(fila, ensure_ascii=False, indent=2))


def principal(argv=None):
    ap = argparse.ArgumentParser(prog="aula", description="Laboratorio del AoE Agentic DevOps")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("estado").set_defaults(func=cmd_estado)

    g = sub.add_parser("guia"); g.add_argument("estacion", nargs="?"); g.set_defaults(func=cmd_guia)

    c = sub.add_parser("check")
    c.add_argument("estacion", nargs="?")
    c.add_argument("--prediccion", choices=["pasa", "falla"],
                   help="declara si crees que vas a pasar antes de verlo")
    c.set_defaults(func=cmd_check)

    p = sub.add_parser("pista"); p.add_argument("estacion", nargs="?"); p.set_defaults(func=cmd_pista)

    b = sub.add_parser("bitacora"); b.add_argument("texto"); b.add_argument("--estacion")
    b.set_defaults(func=cmd_bitacora)

    ce = sub.add_parser("cerrar"); ce.add_argument("estacion", nargs="?"); ce.set_defaults(func=cmd_cerrar)

    d = sub.add_parser("desbloquear"); d.add_argument("estacion", nargs="?")
    d.add_argument("--motivo", required=True); d.set_defaults(func=cmd_desbloquear)

    sub.add_parser("panel").set_defaults(func=cmd_panel)

    args = ap.parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    raise SystemExit(principal())
