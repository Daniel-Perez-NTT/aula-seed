# S5. Modernizacion del legado con agentes

| | |
|---|---|
| Semana | 10 a 11 |
| Horas estimadas | 22 |
| Modulos del itinerario | 5, 6 |

## Objetivo

Caracterizar, refactorizar y demostrar equivalencia sobre un modulo heredado sin tests.

## Por que esta estacion existe

Es el escenario mas frecuente en cliente real y el que mas rentabiliza el discurso del AoE. Tambien es donde mas dano hace un agente mal conducido.

## Aviso

> REGLA DURA: esta prohibido pedir al agente que refactorice antes de existir la caracterizacion. El verificador comprueba el orden en el historial de git. Es la falta mas grave del laboratorio y suspende la estacion. Es tambien la que veras cometer en cliente.

## Que tienes que conseguir

1. Escribe la bateria de caracterizacion que captura el comportamiento actual del modulo heredado, incluidos los comportamientos que no estan documentados en ninguna parte.
2. Commitea la caracterizacion antes de tocar una sola linea del legado.
3. Refactoriza con la red puesta: extrae reglas, elimina duplicidad y codigo muerto, con la bateria en verde en cada paso.
4. Ejecuta la equivalencia sobre el corpus de 500 expedientes.
5. Declara cada desviacion en DESVIACIONES.md con su categoria, causa y efecto aguas abajo.

Esta guia dice que conseguir, no como. Si pudieras seguirla sin pensar, no
aprenderias nada que sirva cuando cambie el contexto, que es lo que pasa en
cliente el primer dia.

## Entregable

Caracterizacion completa, refactor entregado, informe de equivalencia sin desviaciones sin justificar.

## Como se cierra

```bash
python -m aula_cli check S5 --prediccion pasa   # declara antes si crees que vas a pasar
python -m aula_cli cerrar S5                    # sella localmente; pide al mentor la referencia
```

Si te atascas: `python -m aula_cli pista S5` da el siguiente escalon. Si se agota la ventana,
`python -m aula_cli desbloquear S5 --motivo "..."` registra el desbloqueo; pide al mentor la referencia
antes de continuar. No penaliza las estaciones siguientes.

Criterios de superacion detallados en CRITERIOS.md.
