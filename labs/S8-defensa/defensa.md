# Defensa S8 — Aula Students

## Agenda de 20 minutos

| Minutos | Tema |
|---:|---|
| 2 | Problema |
| 2 | Spec |
| 4 | Arquitectura y demo |
| 3 | Agente y metricas |
| 2 | Gobierno |
| 2 | Coste |
| 3 | Traduccion a la torre |
| 2 | Decision tecnica |

## Problema

Aula Students decide qué asignaturas se admiten, quedan en espera o se rechazan al tramitar una matrícula. También calcula nota media, créditos superados y progreso del expediente.

El riesgo principal es producir una decisión académica incorrecta o no poder explicar después qué regla y versión de plan se aplicó. La API conserva datos en memoria, así que un reinicio pierde los expedientes: la demo muestra el alcance funcional actual, no una solución de persistencia de producción.

## Spec

La SPEC-001 define la ventana inclusiva de matrícula, prerrequisitos, límites de créditos, convocatorias y capacidad de grupos. Cada solicitud debe dejar una entrada de auditoría que identifique el plan aplicado.

La SPEC-002 define la media ponderada, el uso de Decimal y el redondeo half-up al final. Las asignaturas convalidadas cuentan como créditos superados, pero no aportan nota a la media.

La decisión de dominio importante es no suponer una regla cuando la especificación es ambigua: se documenta la resolución y se cubre con tests.

## Arquitectura

La API FastAPI expone `/salud`, `/matriculas` y los endpoints de expedientes. Las reglas se separan de los modelos de dominio y de la capa HTTP. El plan se carga desde `datos/planes/PLAN-2024.json`.

El servidor MCP publica herramientas para listar y consultar specs, consultar trazabilidad y tests, y obtener la versión del plan. El agente de conformidad analiza cobertura de criterios, alcance del diff y patrones de riesgo en tests. La flotilla añade triaje y modernización en modo de solo lectura; la decisión final sigue siendo humana.

### Demo

Terminal 1:

```powershell
.\.venv\Scripts\python.exe -m uvicorn --app-dir src aula.api.app:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/salud

$solicitud = @{
    estudiante_id = "DEMO-S8"
    curso_academico = "2026-2027"
    codigos = @("MAT101")
    momento = "2026-11-19T10:00:00"
}
Invoke-RestMethod -Method Post `
    -Uri http://127.0.0.1:8000/matriculas `
    -ContentType "application/json" `
    -Body ($solicitud | ConvertTo-Json)

$registro = @{
    codigo_asignatura = "MAT101"
    curso_academico = "2026-2027"
    convocatoria = 1
    estado = "aprobada"
    nota = 8.5
}
Invoke-RestMethod -Method Post `
    -Uri http://127.0.0.1:8000/expedientes/DEMO-S8/registros `
    -ContentType "application/json" `
    -Body ($registro | ConvertTo-Json)

Invoke-RestMethod http://127.0.0.1:8000/expedientes/DEMO-S8
```

La demostración usa datos en memoria. Al reiniciar el proceso, el expediente de demo desaparece.

## Agente y metricas

La evaluación guardada de iteración 2 tiene 15 casos offline: precisión 1,00, recall 1,00, F1 1,00 y latencia media de 1,8 ms. La línea base v0 obtuvo precisión 1,00, recall 0,10 y F1 0,182. Estos resultados describen el conjunto dorado de ejemplo incluido en el repo; no son por sí solos una validación independiente de producción.

El manifiesto registra precisión 0,800 y recall 0,850, que coinciden con los umbrales de aprobación de S4a. Antes de presentarlo, explicaré que son umbrales y no el resultado de iteración 2, o corregiré la evidencia si pretendían representar una medición.

| Métrica | Evidencia actual |
|---|---|
| Conformidad | Iteración 2: P=1,00, R=1,00, F1=1,00 sobre 15 casos offline |
| MTTR | 45 min sin agente; 30 min con agente, según el informe S7 |
| Detección adversarial | Completar con resultados reales de R1, R2 y R3 |
| Coste | El informe S6 registra 0,20 EUR / 10 criterios = 0,02 EUR por criterio. El manifiesto de evaluación registra 0 USD por ejecución offline. Son bases distintas y hay que explicar qué incluye cada una antes de compararlas. |

## Gobierno

Cada agente tiene manifiesto con propietario humano, autonomía, herramientas, evaluación, coste, reversión y hash del código. El gate de S6 comprueba los manifiestos y detiene el PR si un hash o una evaluación no cumplen la regla.

El veredicto automático ayuda a localizar hallazgos; una persona revisa la evidencia y decide si se integra el cambio. Los dos hashes que debo actualizar antes de volver a ejecutar el gate son los de `conformidad-flotilla.yml` y `triaje.yml`.

## Coste

El coste documentado es 0,02 EUR por criterio cubierto y verificado, calculado como 0,20 EUR dividido entre 10 criterios. La evaluación offline del agente registra 0 USD por ejecución porque no consume tokens de un modelo.

Antes de presentar una cifra única, verificaré qué costes incluye el cálculo de 0,20 EUR y mantendré separadas la ejecución determinista y cualquier infraestructura o revisión humana.

## Traduccion del patron a la torre de banca y seguros

Un plan versionado por curso se traduce en un producto de seguros o una tarifa versionada. La regla aplicada a una matrícula se traduce en la regla tarifaria aplicada a una decisión de contratación o liquidación.

La traza que registra código y versión del plan se traduce en una auditoría que identifica regla, versión, datos de entrada y resultado, para que supervisión pueda reconstruir la decisión. Los criterios de aceptación y sus tests se traducen en controles de conformidad antes de liberar una regla de negocio.

## Decision tecnica que cambiaria

Mantuve los expedientes en memoria para acotar la primera entrega. La decisión simplificó la demo, pero los datos desaparecen al reiniciar el proceso.

Hoy mantendría esa opción solo para una prueba local. Antes de producción elegiría almacenamiento transaccional, definiría migraciones y recuperación, y añadiría pruebas de persistencia y concurrencia. Primero validaría requisitos de retención y auditoría con el SME responsable.