# Flotilla multiagente de Aula

## Componentes

- **MCP Aula** ofrece specs, trazabilidad, resultados de tests y datos del plan.
- **MCP Flotilla** entrega mensajes entre los tres agentes usando SQLite.
- **GitHub Actions** ejecuta las comprobaciones del pipeline y publica un resumen automático en el pull request.
- **Conformidad** revisa un PR frente a su spec.
- **Triaje** analiza los logs de CI e intenta reproducir fallos.
- **Modernización** analiza el legado en modo de solo lectura y propone trabajo para S5.
- **Responsable humano** revisa las salidas y decide qué integrar.

## Diagrama

```mermaid
flowchart LR
    C[Agente de conformidad]
    T[Agente de triaje]
    M[Agente de modernización]
    A[MCP Aula: specs, trazabilidad, tests y plan]
    B[MCP Flotilla: bandeja SQLite compartida]
    H[Responsable humano]
    P[Pull request]

    subgraph G[GitHub Actions: flotilla-s4b.yml]
        GT[Job triaje: ejecuta tests]
        GM[Job modernización: inventaría el legado]
        GC[Job conformidad: valida contrato y evidencias]
        GT --> GC
        GM --> GC
    end

    P -->|abre o actualiza| G
    G -->|comentario resumen y enlace a evidencias| P

    C -->|obtener_spec, trazabilidad| A
    T -->|resultado_tests| A
    M -->|obtener_spec, version_plan| A

    C -->|publicar / leer mensajes| B
    T -->|publicar / leer mensajes| B
    M -->|publicar / leer mensajes| B

    T -->|diagnostico_ci| C
    T -->|contexto_de_fallo| M
    C -->|rutas_y_riesgos_relevantes| M
    M -->|riesgos_del_legado| C
    C -->|veredicto_final| T

    C -->|hallazgos| H
    T -->|diagnóstico| H
    M -->|propuesta para S5| H
```

El workflow hace comprobaciones automáticas; no inicia sesiones de IA. El
comentario del pull request resume el resultado de los jobs y enlaza sus
evidencias. Los agentes siguen intercambiando sus análisis mediante MCP
Flotilla, y una persona conserva la decisión final.
