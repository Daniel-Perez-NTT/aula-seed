# S1. Rebanada vertical a mano

| | |
|---|---|
| Semana | 2 a 4 |
| Horas estimadas | 24 |
| Modulos del itinerario | 2, 3, 4 |

## Objetivo

Construir la primera funcionalidad completa sin ningun agente.

## Por que esta estacion existe

Es la restriccion mas contraintuitiva del laboratorio y la mas importante: no se puede revisar lo que no se sabe escribir. Ademas, el tiempo que registres aqui es la linea base contra la que mediras tu propio salto de productividad en S2 y S3, con datos tuyos y no con la cifra de un informe.

## Que tienes que conseguir

1. Implementa el alta de matricula: endpoint, validacion, persistencia en memoria y tests.
2. Escribe los tests a mano, incluidos los casos limite.
3. Contenedoriza el servicio con una imagen OCI multi-stage.
4. Monta el pipeline: build, test, cobertura y publicacion de la imagen.
5. Registra el tiempo invertido por tarea en bitacora.md. Es el denominador de todo lo que viene despues.

Esta guia dice que conseguir, no como. Si pudieras seguirla sin pensar, no
aprenderias nada que sirva cuando cambie el contexto, que es lo que pasa en
cliente el primer dia.

## Entregable

Pipeline verde de extremo a extremo, imagen publicada, cobertura del modulo de dominio por encima del 60%.

## Como se cierra

```bash
python -m aula_cli check S1 --prediccion pasa   # declara antes si crees que vas a pasar
python -m aula_cli cerrar S1                    # sella localmente; pide al mentor la referencia
```

Si te atascas: `python -m aula_cli pista S1` da el siguiente escalon. Si se agota la ventana,
`python -m aula_cli desbloquear S1 --motivo "..."` registra el desbloqueo; pide al mentor la referencia
antes de continuar. No penaliza las estaciones siguientes.

Criterios de superacion detallados en CRITERIOS.md.
