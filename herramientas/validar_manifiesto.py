from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

RAIZ = Path(__file__).resolve().parents[1]
OBLIGATORIOS = {
    "agente", "version", "propietario_humano", "nivel_autonomia", "herramientas",
    "evaluacion", "coste", "reversion", "codigo",
}
NIVELES = {"N0", "N1", "N2", "N3"}


def fallar(mensaje: str) -> None:
    print(f"ERROR: {mensaje}")


def _cargar_yaml(ruta: Path) -> dict:
    texto = ruta.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(texto)
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        raise RuntimeError("PyYAML no esta instalado; ejecuta pip install -r requirements.txt")


def validar(ruta: Path) -> list[str]:
    try:
        datos = _cargar_yaml(ruta)
    except (RuntimeError, OSError) as exc:
        return [f"{ruta.name}: YAML invalido o no disponible: {exc}"]
    except Exception as exc:
        return [f"{ruta.name}: YAML invalido: {exc}"]
    if not isinstance(datos, dict):
        return [f"{ruta.name}: el manifiesto debe ser un objeto YAML"]

    errores = []
    faltan = sorted(OBLIGATORIOS - datos.keys())
    if faltan:
        errores.append(f"{ruta.name}: faltan campos obligatorios: {', '.join(faltan)}")
    nivel = datos.get("nivel_autonomia")
    if nivel not in NIVELES:
        errores.append(f"{ruta.name}: nivel_autonomia debe ser uno de {sorted(NIVELES)}")
    codigo = datos.get("codigo")
    if not isinstance(codigo, dict) or set(codigo) != {"ruta", "hash_sha256"}:
        errores.append(f"{ruta.name}: codigo debe declarar ruta y hash_sha256")
    else:
        objetivo = RAIZ / codigo["ruta"]
        declarado = codigo["hash_sha256"]
        if not objetivo.is_file():
            errores.append(f"{ruta.name}: no existe el codigo declarado: {codigo['ruta']}")
        elif not isinstance(declarado, str) or len(declarado) != 64:
            errores.append(f"{ruta.name}: hash_sha256 debe contener 64 caracteres hexadecimales")
        elif hashlib.sha256(objetivo.read_bytes()).hexdigest() != declarado:
            errores.append(f"{ruta.name}: hash_sha256 no coincide con {codigo['ruta']}")

    evaluacion = datos.get("evaluacion")
    if not isinstance(evaluacion, dict) or not isinstance(evaluacion.get("fecha"), date):
        errores.append(f"{ruta.name}: evaluacion.fecha debe ser una fecha YAML")
    else:
        antiguedad = (date.today() - evaluacion["fecha"]).days
        limite = evaluacion.get("caducidad_dias", 30)
        if not isinstance(limite, int) or limite < 1:
            errores.append(f"{ruta.name}: evaluacion.caducidad_dias debe ser un entero positivo")
        elif antiguedad > limite:
            errores.append(f"{ruta.name}: evaluacion caducada hace {antiguedad} dias")

    if datos.get("agente") == "conformidad-spec" and nivel != "N3":
        errores.append(f"{ruta.name}: conformidad-spec debe declarar nivel_autonomia N3")
    return errores


def main() -> int:
    manifiestos = sorted((RAIZ / "manifiestos").glob("*.y*ml"))
    if not manifiestos:
        fallar("no hay manifiestos que validar")
        return 1
    errores = [error for ruta in manifiestos for error in validar(ruta)]
    if errores:
        for error in errores:
            fallar(error)
        return 1
    print(f"OK: {len(manifiestos)} manifiesto(s) validado(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
