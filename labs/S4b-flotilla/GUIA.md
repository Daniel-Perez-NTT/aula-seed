# S4b. Flotilla multiagente

| | |
|---|---|
| Semana | 10 |
| Horas estimadas | 12 |
| Modulos del itinerario | 6 |

## Objetivo

Componer tres agentes sobre el mismo contexto compartido y hacer explicito el contrato entre ellos.

## Por que esta estacion existe

Es la conversacion que se tiene en cliente cuando se pasa de un piloto a una flota. Que ve cada agente, que escribe, que se pasan, quien decide si hay conflicto.

## Que tienes que conseguir

1. Trabajo de escuadra: componed conformidad, triaje de pipeline y propuesta de modernizacion sobre el mismo servidor MCP.
2. Ejecutadlos en worktrees aislados y en paralelo.
3. Documentad el contrato de contexto: entradas, salidas, handoff y resolucion de conflicto cuando dos agentes tocan el mismo fichero.
4. Grabad un ciclo completo de los tres agentes.

Esta guia dice que conseguir, no como. Si pudieras seguirla sin pensar, no
aprenderias nada que sirva cuando cambie el contexto, que es lo que pasa en
cliente el primer dia.

## Entregable

Diagrama de flotilla, contrato de contexto en formato validable y grabacion de un ciclo completo.

## Como se cierra

```bash
python -m aula_cli check S4b --prediccion pasa   # declara antes si crees que vas a pasar
python -m aula_cli cerrar S4b                    # sella localmente; pide al mentor la referencia
```

Si te atascas: `python -m aula_cli pista S4b` da el siguiente escalon. Si se agota la ventana,
`python -m aula_cli desbloquear S4b --motivo "..."` registra el desbloqueo; pide al mentor la referencia
antes de continuar. No penaliza las estaciones siguientes.

Criterios de superacion detallados en CRITERIOS.md.
