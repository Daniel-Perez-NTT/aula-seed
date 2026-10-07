# SPEC-001: motor de matrícula

Versión: v1.3.0 | Estado: activa
Autor: referencia del laboratorio | Revisor: SME de plataforma

## Propósito

Decidir, para una solicitud de matrícula de un estudiante en un curso académico,
qué asignaturas se admiten, cuáles quedan en lista de espera y cuáles se rechazan,
aplicando la normativa del plan de estudios vigente en el momento de la solicitud.
La decisión debe quedar auditada con la versión de plan aplicada.

## Entradas y salidas

| Elemento | Tipo | Restricciones |
|----------|------|---------------|
| Solicitud | estudiante, curso académico, lista de códigos, momento ISO-8601 | Lista no vacía, sin duplicados |
| Expediente | registros académicos previos | Puede estar vacío (estudiante de nuevo ingreso) |
| Plan | plan versionado | El aplicado es el vigente en el momento de la solicitud |
| Ventana | inicio y fin ISO-8601 | Inclusiva en ambos extremos |
| Grupos | capacidad y ocupación por asignatura | Ausencia de grupo significa sin límite |
| Salida | Matrícula con una línea por código solicitado | Cada línea: admitida, en espera o rechazada con motivo |

## Invariantes

- INV-01: toda evaluación de solicitud escribe exactamente una entrada de auditoría con el código y la versión de plan aplicados.
- INV-02: el número de líneas de la matrícula resultante es igual al número de códigos solicitados. Nunca se pierde ni se duplica una solicitud de asignatura.
- INV-03: una matrícula en estado confirmada o posterior no puede cambiar de plan de estudios.

## Criterios de aceptación

- CA-01: dado un momento fuera de la ventana de matrícula, cuando se evalúa la solicitud, entonces se rechaza la solicitud completa con error de ventana cerrada.
- CA-02: dada una asignatura con algún prerrequisito no superado, cuando se evalúa la solicitud, entonces esa línea se rechaza indicando los prerrequisitos pendientes, sin afectar al resto de líneas.
- CA-03: dado un conjunto de asignaturas cuya suma de créditos supera el límite del plan, cuando se evalúa la solicitud, entonces se admiten en orden de solicitud hasta agotar el límite y se rechazan las restantes. Excepción: si los créditos pendientes para terminar el título son iguales o inferiores al umbral de fin de carrera, el límite efectivo pasa a ser el total pendiente.
- CA-04: dada una asignatura con el máximo de convocatorias consumidas, cuando se evalúa la solicitud, entonces esa línea se rechaza por convocatorias agotadas. Una convalidación no consume convocatoria.
- CA-05: dada una asignatura cuyo grupo está completo, cuando se evalúa la solicitud, entonces esa línea queda en lista de espera y no consume créditos del límite. El resto de la matrícula continúa.
- CA-06: dado un expediente con asignaturas convalidadas, cuando se calculan los créditos superados, entonces los créditos convalidados cuentan como superados.
- CA-07: dadas varias solicitudes concurrentes, cuando se ordenan para asignar plazas, entonces se ordenan por créditos superados de mayor a menor y, a igualdad, por momento de solicitud ascendente.
- CA-08: dada una asignatura ya superada, cuando se evalúa la solicitud, entonces esa línea se rechaza por asignatura ya superada.

## Casos límite

| Caso | Resultado esperado |
|------|--------------------|
| Solicitud en el instante exacto de inicio o de fin de ventana | Aceptada, la ventana es inclusiva |
| Estudiante de nuevo ingreso, expediente vacío | Solo se admiten asignaturas sin prerrequisitos |
| Créditos pendientes iguales al umbral de fin de carrera | Se aplica la excepción de CA-03 |
| Asignatura con grupo completo y además prerrequisito pendiente | Prevalece el rechazo por prerrequisito, no la lista de espera |
| Plan sin grupos declarados | Ninguna línea va a lista de espera |

## Fuera de alcance

Rutas: src/aula/reglas/motor.py, src/aula/dominio/, tests/test_reglas_matricula.py, specs/SPEC-001-matricula.md

- Pago de tasas y su conciliación.
- Reserva y gestión de plazas de la lista de espera a lo largo del curso.
- Anulación de matrícula una vez confirmada.
- Convalidaciones: esta spec las consume, no las decide.
- Cálculo de la nota media, que es objeto de SPEC-002.

## Ambigüedades detectadas y resolución

| # | Ambigüedad | Resolución | Fecha |
|---|-----------|------------|-------|
| A-01 | El enunciado original decía "se rechazan las asignaturas que superen el límite" sin fijar orden. Con orden indeterminado el resultado no es reproducible | Se admiten en el orden en que aparecen en la solicitud. Recogido en CA-03 | 2026-08 |
| A-02 | No estaba definido si una convalidación consume convocatoria | No la consume. Recogido en CA-04 | 2026-08 |
