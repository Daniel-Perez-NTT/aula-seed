# S3. Ingenieria de contexto y operacion de agentes

| | |
|---|---|
| Semana | 6 a 7 |
| Horas estimadas | 24 |
| Modulos del itinerario | 5 |

## Objetivo

Convertir el repositorio en un entorno donde el agente trabaja bien por diseno, no por suerte en el prompt.

## Por que esta estacion existe

La habilidad que se paga no es escribir buenos prompts, es que el repo imponga las reglas para que el prompt importe menos. Lo innegociable no se pide en lenguaje natural, se hace determinista.

## Aviso

> Se mide tu ratio de diff aceptado sin comentario. Un ratio alto no es productividad, es aceptacion ciega, y se trata como senal de riesgo. Un ratio de cero tampoco es bueno: significa que no confias en nada y no estas usando la herramienta.

## Que tienes que conseguir

1. Escribe CLAUDE.md con las seis secciones obligatorias: proposito, invariantes, verificacion, convenciones, limites y escalado.
2. Configura allowlist de permisos y hooks: formato al escribir, bloqueo de escritura en rutas prohibidas, tests antes de commit.
3. Define dos subagentes de proposito acotado: uno implementa, otro revisa solo el diff.
4. Resuelve el mismo encargo con Claude Code y con OpenCode y entrega la tabla comparativa con criterio de eleccion razonado.
5. Ejecuta un ciclo en worktrees paralelos con Orca aplicando el patron escritor y revisor.

Esta guia dice que conseguir, no como. Si pudieras seguirla sin pensar, no
aprenderias nada que sirva cuando cambie el contexto, que es lo que pasa en
cliente el primer dia.

## Entregable

Configuracion versionada en el repo, cuatro PRs generados con agente y revisados con evidencia, tabla comparativa entregada.

## Como se cierra

```bash
python -m aula_cli check S3 --prediccion pasa   # declara antes si crees que vas a pasar
python -m aula_cli cerrar S3                    # sella localmente; pide al mentor la referencia
```

Si te atascas: `python -m aula_cli pista S3` da el siguiente escalon. Si se agota la ventana,
`python -m aula_cli desbloquear S3 --motivo "..."` registra el desbloqueo; pide al mentor la referencia
antes de continuar. No penaliza las estaciones siguientes.

Criterios de superacion detallados en CRITERIOS.md.
