"""Hook de formato: normaliza el fichero editado. Silencioso si no hay nada que hacer."""
import json
import sys
from pathlib import Path


def main():
    try:
        entrada = json.load(sys.stdin)
    except Exception:
        return 0
    ruta = (entrada.get("tool_input", {}) or {}).get("file_path", "")
    p = Path(ruta)
    if not p.exists() or p.suffix != ".py":
        return 0
    texto = p.read_text(encoding="utf-8")
    limpio = "\n".join(l.rstrip() for l in texto.splitlines())
    if not limpio.endswith("\n"):
        limpio += "\n"
    if limpio != texto:
        p.write_text(limpio, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
