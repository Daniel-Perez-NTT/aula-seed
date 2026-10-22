# Bitacora de S2

Registra preguntas de negocio, decisiones acordadas y evidencia de verificacion.

- A-01: para asignaturas repetidas se usa la nota del aprobado con el número de convocatoria más alto. Se cuenta una sola nota y una sola vez los créditos.
- A-02: una convalidación cuenta para créditos superados y progreso, pero no aporta una nota a la media.
- Evidencia ejecutada en esta revisión: pruebas de cálculo y API (13 pasaron); trazabilidad SPEC-001 y SPEC-002 al 100 %.
- Verificacion final: `python -m aula_cli check S2 --prediccion pasa` termino con todos los criterios en verde, incluida la suite completa. S2 quedo sellada localmente con `python -m aula_cli cerrar S2`.
- Revision manual: la tabla de ambiguedades de SPEC-002 contiene A-01 y A-02. S2-04 puede dar un falso positivo por su busqueda; se comprobo la tabla y no se modifico el verificador.
- Nota de alcance: la API utiliza almacenamiento en memoria; los datos de demostración se pierden al reiniciar el servidor.
