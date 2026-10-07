.PHONY: ayuda test check estado cobertura agente eval mcp imagen corpus

ayuda:
	@echo "make test       ejecuta la suite"
	@echo "make check      verifica la estacion activa"
	@echo "make estado     muestra el progreso del laboratorio"
	@echo "make eval       evalua el agente de conformidad"
	@echo "make imagen     construye la imagen OCI"

test:
	python3 -m pytest tests/ -q

cobertura:
	python3 -m pytest tests/ -q --cov=src/aula --cov-report=term-missing

estado:
	python3 -m aula_cli estado

check:
	python3 -m aula_cli check

eval:
	python3 -m agentes.conformidad.evaluar --guardar

mcp:
	python3 -m agentes.mcp_aula.servidor

corpus:
	python3 herramientas/generar_corpus.py

imagen:
	podman build -t aula:dev . || docker build -t aula:dev .
