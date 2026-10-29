"""Ejecuta la suite antes de que Claude lance un git commit."""
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def responder_bloqueo(motivo):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": motivo,
        }
    }))


def main():
    try:
        entrada = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        # No intervenir si la entrada del hook no se puede interpretar.
        return 0

    llamada = entrada.get("tool_input", {}) or {}
    comando = llamada.get("command", "")

    # Solo actuar antes de un "git commit".
    if not re.search(r"(?i)(?:^|[;&|]\s*)git(?:\.exe)?\s+commit(?:\s|$)", comando):
        return 0

    resultado = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        cwd=RAIZ,
        text=True,
        capture_output=True,
    )

    if resultado.stdout:
        print(resultado.stdout, file=sys.stderr, end="")
    if resultado.stderr:
        print(resultado.stderr, file=sys.stderr, end="")

    if resultado.returncode != 0:
        responder_bloqueo("Commit bloqueado: la suite de tests ha fallado.")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())