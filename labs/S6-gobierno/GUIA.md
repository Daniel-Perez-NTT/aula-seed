# S6. Gobierno del agente

| | |
|---|---|
| Semana | 11 |
| Horas estimadas | 18 |
| Modulos del itinerario | 7 |

## Objetivo

Dejar los agentes construidos en condiciones de ser puestos en produccion por una entidad regulada.

## Por que esta estacion existe

Trabajamos para banca y seguros. El gobierno no es un apartado del documento: es un gate del pipeline o no existe.

## Aviso

> Ningun agente de student llega a N4 en el laboratorio. El ejercicio es argumentar que haria falta. Esa argumentacion es material directo de conversacion con un CISO.

## Que tienes que conseguir

1. Escribe el Agent Release Manifest de cada agente y versionalo en el repo.
2. Haz que el pipeline bloquee el merge si falta el manifiesto, si el hash del agente no coincide o si la evaluacion referenciada tiene mas de 30 dias.
3. Declara el nivel de autonomia de cada agente e implementa el control tecnico que lo hace cierto.
4. Genera el paquete de evidencia por PR: tests, cobertura, conformidad, seguridad y coste en tokens.
5. Calcula el coste por criterio de aceptacion cubierto y verificado.
6. Argumenta por escrito que haria falta para que tu agente de conformidad operase a N4 y que control lo haria seguro.

Esta guia dice que conseguir, no como. Si pudieras seguirla sin pensar, no
aprenderias nada que sirva cuando cambie el contexto, que es lo que pasa en
cliente el primer dia.

## Entregable

Manifiestos validados por el pipeline, gates activos, paquete de evidencia automatico e informe de coste por unidad de resultado.

## Como se cierra

```bash
python -m aula_cli check S6 --prediccion pasa   # declara antes si crees que vas a pasar
python -m aula_cli cerrar S6                    # sella localmente; pide al mentor la referencia
```

Si te atascas: `python -m aula_cli pista S6` da el siguiente escalon. Si se agota la ventana,
`python -m aula_cli desbloquear S6 --motivo "..."` registra el desbloqueo; pide al mentor la referencia
antes de continuar. No penaliza las estaciones siguientes.

Criterios de superacion detallados en CRITERIOS.md.
