# Manual de arranque de Aula Students

Requiere Python 3.11 o posterior. Ejecuta todo desde la raiz de `aula-students`.
Instala dependencias y activa el entorno como indica [README.md](README.md).

```bash
python -m aula_cli estado
python -m aula_cli guia S0
python -m aula_cli check S0 --prediccion falla
```

S0 comienza pendiente. Los checks rojos son normales en una semilla.

## Servicio local

Git Bash, Linux y macOS:

```bash
PYTHONPATH=src python -m uvicorn aula.api.app:app --host 127.0.0.1 --port 8001
```

PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn aula.api.app:app --host 127.0.0.1 --port 8001
```

En otra terminal:

```bash
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8001/salud').read().decode())"
```

La documentacion esta en http://127.0.0.1:8001/docs. Los recursos de matriculas
y expedientes devuelven 501 hasta que se implementen en S1 y S2.
Deten el servicio con Ctrl+C. Si el puerto esta ocupado, elige otro.