# SPEC-002: cálculo de expediente

Versión: v0.2.0 | Estado: activa
Autor: equipo de implementación | Revisor: pendiente

## Propósito

Calcular el estado académico de un estudiante respecto de su plan: nota media
ponderada por créditos, créditos superados y porcentaje del título completado.
La nota media puede alimentar procesos aguas abajo, por lo que el resultado
debe ser reproducible y trazable.

## Entradas y salidas

| Elemento | Tipo | Restricciones |
|----------|------|---------------|
| Expediente | estudiante y lista de registros académicos | Cada registro representa una convocatoria consumida o una convalidación. |
| Plan | plan versionado | Determina los créditos de cada asignatura y los créditos totales del título. |
| Nota media | Decimal | Dos decimales, redondeo half-up. Las convalidadas no aportan nota a la media. |
| Créditos superados | entero | Cada asignatura aprobada o convalidada cuenta una sola vez. |
| Progreso | Decimal | Créditos superados / créditos del título * 100, a dos decimales. |
| Resumen HTTP | objeto JSON | Incluye estudiante, plan, nota media, créditos, progreso, convocatorias y registros con sus créditos. |

## Invariantes

- INV-01: el redondeo de cada resultado decimal se aplica una sola vez al final; no se redondean valores intermedios.
- INV-02: los cálculos decimales usan `Decimal`, nunca coma flotante binaria.
- INV-03: el mismo expediente y plan producen los mismos resultados, aunque los registros aparezcan en otro orden.

## Criterios de aceptación

- CA-01: dadas asignaturas aprobadas en primera convocatoria, la nota media es la suma de nota * créditos dividida por la suma de los créditos computables.
- CA-02: si una asignatura tiene más de un intento aprobado, la media usa la nota del aprobado con el número de convocatoria más alto. La asignatura aporta una sola nota y sus créditos una sola vez.
- CA-03: las asignaturas convalidadas se excluyen tanto del numerador como del denominador de la nota media.
- CA-04: la nota media se redondea una sola vez, al final, a dos decimales con `ROUND_HALF_UP`.
- CA-05: una asignatura aprobada o convalidada aporta sus créditos superados una sola vez, aunque tenga varios registros.
- CA-06: el progreso es créditos superados divididos por créditos totales del título y multiplicado por 100, redondeado a dos decimales con `ROUND_HALF_UP`. Si el plan tiene cero créditos totales, devuelve 0,00.
- CA-07: si no hay notas computables, la nota media es 0,00. Un expediente vacío produce media 0,00, créditos 0 y progreso 0,00.
- CA-08: `GET /expedientes/{estudiante_id}` devuelve el resumen calculado, los datos del plan y el detalle de registros académicos con créditos por asignatura. Si el estudiante no existe, responde 404.
- CA-09: `POST /expedientes/{estudiante_id}/registros` añade un registro académico válido al expediente en memoria y devuelve el resumen actualizado. Un código de asignatura ausente del plan se rechaza con 422.

## Casos límite

| Caso | Resultado esperado |
|------|--------------------|
| Expediente vacío | Nota media 0,00, créditos 0, progreso 0,00 y lista de registros vacía |
| Todas las asignaturas convalidadas | Media 0,00; sus créditos cuentan como superados una sola vez |
| Asignatura aprobada en convocatoria 2 y también en convocatoria 4 | Se usa la nota aprobada de convocatoria 4 |
| Nota con más de dos decimales en origen | Se conserva íntegra en el numerador y solo se redondea el cociente final |
| Media exactamente en el punto medio, por ejemplo 7,005 | Redondeo half-up a 7,01 |
| Consulta de estudiante no registrado | HTTP 404 |
| Registro HTTP con código que no está en el plan | HTTP 422; el expediente no se modifica |

## Alcance de implementación

Rutas: `src/aula/reglas/media.py`, `src/aula/dominio/modelos.py`, `src/aula/api/app.py`, `tests/test_media_expediente.py`, `tests/test_api_expediente.py` y `specs/SPEC-002-expediente.md`.

## Fuera de alcance

- Menciones, matrículas de honor y premios extraordinarios.
- Reconocimiento de créditos por actividades no académicas.
- Media de acceso a máster, que usa otra normativa.
- Decisión académica de convalidar; esta estación solo consume el registro de convalidación.
- Persistencia en base de datos: la API conserva expedientes en memoria y los pierde al reiniciar.

## Ambigüedades detectadas y resolución

| # | Ambigüedad | Resolución adoptada | Alternativas descartadas y por qué |
|---|-----------|---------------------|-------------------------------------|
| A-01 | La spec inicial no indicaba qué nota de una asignatura repetida debía entrar en la media. | Se usa la nota del registro aprobado con el número de convocatoria más alto; la asignatura aporta una sola nota y sus créditos se cuentan una vez. | Usar el primer aprobado ignoraría un resultado aprobado posterior. Incluir todos los intentos contaría varias veces una asignatura. |
| A-02 | La spec inicial no definía si una asignatura convalidada aportaba una nota a la media. | La convalidada no aporta nota numérica: se excluye de la media y sí cuenta como superada para créditos y progreso. Si no hay otras notas computables, la media es 0,00. | Asignarle una nota fija inventaría un dato que no está en el expediente. |
