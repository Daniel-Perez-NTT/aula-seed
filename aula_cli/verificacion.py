"""Utilidades compartidas por los verificadores de estacion.

Dos ideas rinden mas que el resto y estan aqui:

  `mutar_y_exigir_fallo`: no comprueba que un test exista, comprueba que falla
  cuando se rompe la implementacion. Un test que no falla al mutar no es un test.

  `prueba_negativa`: no comprueba que un gate este configurado, comprueba que
  bloquea cuando se intenta pasar. Un gate que nunca ha bloqueado nada no esta
  verificado.

Es el mismo criterio que se le pide al student en la revision adversarial,
aplicado al propio laboratorio.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def criterio(ident, descripcion, ok, detalle="", nivel="V1"):
    return {"id": ident, "descripcion": descripcion, "ok": bool(ok),
            "detalle": detalle, "nivel": nivel}


def ejecutar(comando, cwd=None, timeout=300):
    return subprocess.run(comando, cwd=cwd or RAIZ, capture_output=True,
                          text=True, timeout=timeout)


def pytest_verde(ruta="tests/", cwd=None):
    p = ejecutar([sys.executable, "-m", "pytest", ruta, "-q", "--no-header"], cwd=cwd)
    resumen = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "sin salida"
    return p.returncode == 0, resumen


def existe(ruta):
    return (RAIZ / ruta).exists()


def contiene(ruta, patron):
    p = RAIZ / ruta
    if not p.exists():
        return False
    return re.search(patron, p.read_text(encoding="utf-8"), re.M | re.S | re.I) is not None


# Conjunto de operadores elegido a proposito. Operadores como `continue -> pass`
# producen mutantes equivalentes (el codigo cambia y el comportamiento no), que
# harian fallar el verificador sin que haya ningun test decorativo. Es un
# fenomeno conocido de la tecnica y merece explicarselo al student cuando
# pregunte por que no se mutan todas las palabras clave.
MUTACIONES = [
    (r"==", "!="),
    (r"(?<![*\w])\*(?![*=])", "/"),
    (r"\+=", "-="),
    (r">=", ">"),
]


def mutar_y_exigir_fallo(fichero, tests, mutaciones=None, maximo=3):
    """Aplica mutaciones al fichero y exige que la suite falle en cada una.

    Devuelve (todas_detectadas, detalle). Si alguna mutacion pasa desapercibida,
    hay una rama de codigo sin test que la defienda.
    """
    mutaciones = mutaciones or MUTACIONES
    origen = RAIZ / fichero
    if not origen.exists():
        return False, "no existe %s" % fichero

    supervivientes = []
    aplicadas = 0
    texto = origen.read_text(encoding="utf-8")

    for patron, reemplazo in mutaciones:
        if aplicadas >= maximo:
            break
        mutado, n = re.subn(patron, reemplazo, texto, count=1)
        if n == 0:
            continue
        aplicadas += 1
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "repo"
            shutil.copytree(RAIZ, copia, ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "*.pyc", "node_modules", ".aula"))
            (copia / fichero).write_text(mutado, encoding="utf-8")
            verde, _ = pytest_verde(tests, cwd=copia)
            if verde:
                supervivientes.append("%s -> %s" % (patron, reemplazo))

    if aplicadas == 0:
        return False, "ninguna mutacion aplicable sobre %s" % fichero
    if supervivientes:
        return False, ("mutaciones que sobreviven (la suite sigue verde): %s"
                       % "; ".join(supervivientes))
    return True, "%d mutaciones aplicadas, todas detectadas por la suite" % aplicadas


def prueba_negativa(accion, descripcion):
    """Ejecuta una accion que DEBE fallar. Devuelve True si efectivamente fallo."""
    try:
        resultado = accion()
    except Exception:
        return True, "%s: bloqueado, correcto" % descripcion
    if resultado is False:
        return True, "%s: bloqueado, correcto" % descripcion
    return False, "%s: NO se bloqueo, el control no esta activo" % descripcion


def orden_en_historial(patron_antes, patron_despues, por_asunto=False):
    """Comprueba que los commits de caracterizacion preceden a los de refactor.

    Con `por_asunto=True` la deteccion usa el mensaje del commit y no los
    ficheros tocados, que es lo semanticamente correcto: anadir el modulo
    heredado al repo no es refactorizarlo.
    """
    p = ejecutar(["git", "log", "--reverse", "--format=%H|%s", "--name-only"])
    if p.returncode != 0:
        return None, "sin historial de git disponible"
    primer_antes = primer_despues = None
    orden = 0
    for linea in p.stdout.splitlines():
        if "|" in linea and len(linea.split("|")[0]) == 40:
            orden += 1
            asunto = linea.split("|", 1)[1]
            if por_asunto:
                if re.search(patron_antes, asunto, re.I) and primer_antes is None:
                    primer_antes = orden
                if re.search(patron_despues, asunto, re.I) and primer_despues is None:
                    primer_despues = orden
            continue
        if por_asunto or not linea.strip():
            continue
        if re.search(patron_antes, linea) and primer_antes is None:
            primer_antes = orden
        if re.search(patron_despues, linea) and primer_despues is None:
            primer_despues = orden
    if primer_antes is None:
        return False, "no hay ningun commit que anada caracterizacion"
    if primer_despues is None:
        return True, "todavia no hay commits de refactor"
    if primer_antes < primer_despues:
        return True, "caracterizacion en el commit %d, refactor a partir del %d" % (
            primer_antes, primer_despues)
    return False, ("el refactor (commit %d) precede a la caracterizacion (commit %d)"
                   % (primer_despues, primer_antes))
