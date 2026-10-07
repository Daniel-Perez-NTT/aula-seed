# S2. Spec-Driven Development

| | |
|---|---|
| Semana | 5 a 6 |
| Horas estimadas | 26 |
| Modulos del itinerario | 6 |

## Objetivo

Invertir el orden: la especificacion deja de ser documentacion y pasa a ser el artefacto del que deriva todo lo demas.

## Por que esta estacion existe

Es el posicionamiento de mercado del AoE. Escribir codigo con un agente lo hace cualquiera. Derivar codigo verificable de una especificacion trazable es lo que los clientes empiezan a pedir y casi nadie sabe hacer.

## Aviso

> La spec de partida contiene una ambigueda real y deliberada sobre el tratamiento de asignaturas repetidas y convalidadas en la nota media. Si no la detectas, el agente producira una implementacion plausible y equivocada, y el verificador te lo dira. Detectarla antes es parte de la evaluacion.

## Que tienes que conseguir

1. Escribe SPEC-002 completa siguiendo la plantilla, antes de tocar codigo.
2. Numera los criterios de aceptacion y traducelos uno a uno a test, referenciando el criterio en el docstring con la etiqueta `cubre:`.
3. Dirige al agente para que derive la implementacion de la spec, criterio a criterio.
4. Detecta y resuelve la ambigueda que contiene la spec de partida antes de implementar, no despues.
5. Registra en el apartado de ambiguedades que estaba mal definido y como lo cerraste.

Esta guia dice que conseguir, no como. Si pudieras seguirla sin pensar, no
aprenderias nada que sirva cuando cambie el contexto, que es lo que pasa en
cliente el primer dia.

## Entregable

Spec versionada, implementacion completa, trazabilidad al 100% verificada por el pipeline y registro de ambiguedades.

## Como se cierra

```bash
python -m aula_cli check S2 --prediccion pasa   # declara antes si crees que vas a pasar
python -m aula_cli cerrar S2                    # sella localmente; pide al mentor la referencia
```

Si te atascas: `python -m aula_cli pista S2` da el siguiente escalon. Si se agota la ventana,
`python -m aula_cli desbloquear S2 --motivo "..."` registra el desbloqueo; pide al mentor la referencia
antes de continuar. No penaliza las estaciones siguientes.

Criterios de superacion detallados en CRITERIOS.md.
