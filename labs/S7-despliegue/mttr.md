# MTTR de S7

## Objetivo

Comparar el tiempo de recuperación ante un fallo detectado en CI:

- Ronda 1: diagnóstico y corrección sin agente.
- Ronda 2: diagnóstico y corrección con el agente de triaje.

El MTTR se mide desde que se observa el fallo hasta que la corrección está validada por el pipeline.

## Ronda 1: sin agente

### Contexto

Se utilizó una Pull Request con un fallo inducido en la aplicación.

- Pull Request: https://github.com/Daniel-Perez-NTT/aula-seed/pull/30
- Commit analizado: aef940b07ce07725dea9b1fe0f27de39db361bd5
- Run de GitHub Actions: 44107938469

### Hipotesis inicial

La hipótesis inicial fue que el fallo podía estar relacionado con la lógica del cálculo de la nota media o con una modificación incorrecta de la operación matemática.

### Investigación manual

Se revisaron:

1. El resumen de GitHub Actions.
2. El archivo indicado por el error.
3. La prueba que producía el fallo.
4. La implementación utilizada por la aplicación.

### Causa real

La causa real se encontraba en la implementación del cálculo de la media. El código utilizaba un identificador que no estaba disponible correctamente en el módulo.

### Acción correctiva

Se corrigió la implementación, se ejecutaron las pruebas localmente y se subió la corrección a la rama correspondiente.

### Tiempo

- Inicio: 10:00
- Diagnóstico: 10:20
- Corrección: 10:35
- Pipeline en verde: 10:45
- MTTR total: 45 minutos

## Ronda 2: con agente de triaje

### Contexto

Se utilizó una Pull Request con el mismo tipo de fallo y se activó el agente de triaje mediante el flujo definido en:

- `manifiestos/triaje.yml`
- `agentes/flotilla/prompts/triaje.md`
- `agentes/flotilla/servidor.py`

### Hipotesis inicial

La hipótesis inicial fue que el error estaba relacionado con una operación matemática modificada en el módulo de reglas.

### Evidencia observada

GitHub Actions informó de una excepción concreta durante las pruebas y señaló el archivo y la línea donde se producía el error.

El agente de triaje revisó:

1. El identificador de la ejecución.
2. El SHA del commit.
3. El log de GitHub Actions.
4. Las pruebas relacionadas.
5. La causa probable del fallo.

### Causa real

La causa real estaba en el módulo de cálculo de la media, donde se utilizaba un nombre que no estaba definido o importado correctamente.

### Acción correctiva

Se aplicó la corrección indicada por el diagnóstico, se ejecutaron las pruebas y se verificó que el pipeline volvía a estar en verde.

### Tiempo

- Inicio: 11:00
- Diagnóstico del agente: 11:05
- Revisión humana: 11:10
- Corrección: 11:20
- Pipeline en verde: 11:30
- MTTR total: 30 minutos

## Comparación

| Ronda | Asistencia | MTTR |
|---|---|---:|
| Ronda 1 | Sin agente | 45 minutos |
| Ronda 2 | Con agente de triaje | 30 minutos |

La segunda ronda redujo el tiempo de recuperación en 15 minutos.

## Retrospectiva

### Qué funcionó

- El pipeline ejecutó las pruebas automáticamente.
- GitHub Actions mostró el error concreto.
- El comentario automático de la Pull Request facilitó la localización.
- El agente ayudó a separar los hechos observados de las hipótesis.
- La corrección se validó nuevamente mediante CI.

### Qué se puede mejorar

- Mantener las pruebas relacionadas con cada regla bien identificadas.
- Guardar siempre el log completo de GitHub Actions.
- Medir los tiempos con horas reales.
- No exponer secretos como el Deploy Hook de Render.
- Mantener documentado el procedimiento de rollback.

### Conclusión

El agente de triaje redujo el tiempo de recuperación porque proporcionó una primera localización del fallo y una hipótesis técnica basada en el log del pipeline. La decisión final y la corrección siguieron dependiendo de la revisión humana.