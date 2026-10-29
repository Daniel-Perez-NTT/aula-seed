"""Agente determinista de conformidad de specs para S4a."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

CONFORME = "conforme"
NO_CONFORME = "no_conforme"

RAIZ = Path(__file__).resolve().parents[2]


@dataclass
class Veredicto:
    pr: str
    spec: str
    veredicto: str
    criterios_declarados: list = field(default_factory=list)
    criterios_cubiertos: list = field(default_factory=list)
    criterios_sin_cubrir: list = field(default_factory=list)
    fuera_de_alcance: list = field(default_factory=list)
    hallazgos: list = field(default_factory=list)
    explicacion: str = ""

    def a_dict(self) -> dict:
        return asdict(self)


def _normalizar_ruta(ruta: str) -> str:
    """Normaliza separadores y prefijos comunes de rutas."""
    resultado = str(ruta).replace("\\", "/").strip()
    while resultado.startswith("./"):
        resultado = resultado[2:]
    return resultado


def _extraer_ids(texto: str) -> list[str]:
    """Extrae CA e INV mencionados en una cadena."""
    return sorted(set(re.findall(r"\b(?:CA|INV)-\d{2}\b", texto)))


def _leer_spec(spec_id: str) -> tuple[str, list[str], set[str]]:
    """Lee la spec y devuelve su texto, criterios y rutas de alcance."""
    archivos = sorted((RAIZ / "specs").glob(f"{spec_id}-*.md"))

    if not archivos:
        return "", [], set()

    texto = archivos[0].read_text(encoding="utf-8")
    criterios = sorted(set(re.findall(r"\b(?:CA|INV)-\d{2}\b", texto)))

    seccion = re.search(
        r"^##\s+Alcance de implementación\s*$"
        r"(.*?)(?=^##\s+|\Z)",
        texto,
        re.I | re.M | re.S,
    )

    alcance: set[str] = set()
    if seccion:
        contenido = seccion.group(1)
        rutas = re.findall(
            r"(?<![\w.-])(?:[\w.-]+/)+[\w.-]+(?:\.[A-Za-z0-9]+)?",
            contenido,
        )
        alcance = {_normalizar_ruta(ruta) for ruta in rutas}

    return texto, criterios, alcance


def _criterios_cubiertos(tests: list[dict], spec_id: str) -> set[str]:
    """Obtiene criterios asociados a etiquetas cubre: en los tests del PR."""
    cubiertos: set[str] = set()
    patron = re.compile(
        rf"\b{re.escape(spec_id)}/((?:CA|INV)-\d{{2}})\b",
        re.I,
    )

    for fichero in tests:
        contenido = str(fichero.get("contenido", ""))
        # Solo se consideran las etiquetas explícitas cubre:.
        for etiqueta in re.findall(r"cubre:\s*([^\n\"]+)", contenido):
            cubiertos.update(patron.findall(etiqueta))

    return {criterio.upper() for criterio in cubiertos}


def _riesgos_en_tests(tests: list[dict]) -> list[dict]:
    """Busca patrones comunes que pueden debilitar una prueba."""
    hallazgos = []

    patrones = [
        (
            "test omitido",
            re.compile(r"\bpytest\.mark\.skip\b|\bunittest\.skip\b"),
        ),
        (
            "asercion siempre verdadera",
            re.compile(r"\bassert\s+True\b"),
        ),
        (
            "valor comparado consigo mismo",
            re.compile(
                r"\bassert\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)"
                r"\s*==\s*\1\b"
            ),
        ),
        (
            "excepcion silenciada",
            re.compile(
                r"except(?:\s+[\w.]+)?\s*:\s*\n"
                r"(?:[ \t]+#[^\n]*\n)*"
                r"[ \t]+pass\b",
                re.M,
            ),
        ),
    ]

    for fichero in tests:
        ruta = _normalizar_ruta(fichero.get("ruta", ""))
        contenido = str(fichero.get("contenido", ""))

        for descripcion, patron in patrones:
            if patron.search(contenido):
                hallazgos.append({
                    "tipo": "riesgo_test",
                    "archivo": ruta,
                    "detalle": descripcion,
                })

    return hallazgos


def evaluar(pr: dict, spec_id: str, juez=None) -> Veredicto:
    """Analiza cobertura, alcance y riesgos con reglas deterministas."""
    identificador = str(spec_id).upper()
    texto_spec, criterios_spec, alcance = _leer_spec(identificador)

    ficheros = pr.get("ficheros", [])
    if not isinstance(ficheros, list):
        ficheros = []

    tests = [
        fichero for fichero in ficheros
        if _normalizar_ruta(fichero.get("ruta", "")).startswith("tests/")
    ]

    # Si el PR enumera criterios, se evalúan esos criterios.
    # Si no los enumera, se consideran todos los criterios de aceptación
    # y los invariantes de la spec.
    declarados = _extraer_ids(
        " ".join(str(item) for item in pr.get("criterios_declarados", []))
    )
    requeridos = declarados or criterios_spec

    cubiertos = _criterios_cubiertos(tests, identificador)
    criterios_cubiertos = sorted(set(requeridos) & cubiertos)
    criterios_sin_cubrir = sorted(set(requeridos) - cubiertos)

    rutas_cambiadas = sorted({
        _normalizar_ruta(fichero.get("ruta", ""))
        for fichero in ficheros
        if fichero.get("ruta")
    })

    fuera_de_alcance = []
    if alcance:
        fuera_de_alcance = sorted(
            ruta for ruta in rutas_cambiadas
            if ruta not in alcance
        )

    hallazgos = []

    if not texto_spec:
        hallazgos.append({
            "tipo": "spec_no_encontrada",
            "detalle": f"No se encontro la especificacion {identificador}.",
        })

    for criterio in criterios_sin_cubrir:
        hallazgos.append({
            "tipo": "criterio_sin_cubrir",
            "criterio": criterio,
            "detalle": f"No se encontro un test con etiqueta cubre: para {criterio}.",
        })

    for ruta in fuera_de_alcance:
        hallazgos.append({
            "tipo": "fuera_de_alcance",
            "archivo": ruta,
            "detalle": "El archivo no aparece en el alcance declarado por la spec.",
        })

    hallazgos.extend(_riesgos_en_tests(tests))

    no_conforme = bool(hallazgos)
    resultado = NO_CONFORME if no_conforme else CONFORME

    if not texto_spec:
        explicacion = f"No se encontro la spec {identificador}."
    elif no_conforme:
        explicacion = (
            f"Se detectaron {len(hallazgos)} hallazgo(s): "
            f"{len(criterios_sin_cubrir)} criterio(s) sin cubrir, "
            f"{len(fuera_de_alcance)} archivo(s) fuera de alcance y "
            f"{len(hallazgos) - len(criterios_sin_cubrir) - len(fuera_de_alcance)} "
            "otro(s) riesgo(s)."
        )
    else:
        explicacion = (
            "Los criterios declarados tienen tests etiquetados, "
            "los archivos estan dentro del alcance y no se detectaron "
            "patrones de riesgo conocidos."
        )

    return Veredicto(
        pr=pr.get("id", "sin-id"),
        spec=identificador,
        veredicto=resultado,
        criterios_declarados=requeridos,
        criterios_cubiertos=criterios_cubiertos,
        criterios_sin_cubrir=criterios_sin_cubrir,
        fuera_de_alcance=fuera_de_alcance,
        hallazgos=hallazgos,
        explicacion=explicacion,
    )


def principal(argv=None):
    parser = argparse.ArgumentParser(description="Agente de conformidad de specs")
    parser.add_argument("--pr", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    entrada = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    veredicto = evaluar(entrada, args.spec)

    if args.json:
        print(json.dumps(veredicto.a_dict(), ensure_ascii=False, indent=2))
    else:
        print(veredicto.veredicto + ": " + veredicto.explicacion)

    return 1 if veredicto.veredicto == NO_CONFORME else 0


if __name__ == "__main__":
    raise SystemExit(principal())