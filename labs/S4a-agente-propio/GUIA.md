# S4a. Servidor MCP y agente propio

| | |
|---|---|
| Semana | 8 a 10 |
| Horas estimadas | 28 |
| Modulos del itinerario | 6 |

## Objetivo

Dejar de consumir agentes y fabricar uno que interviene en el SDLC.

## Por que esta estacion existe

Es el corazon del laboratorio. Hasta aqui has conducido agentes. A partir de aqui construyes uno, lo conectas a contexto propio y lo mides. Sin la medicion es una demo; con la medicion es ingenieria.

## Aviso

> Dos iteraciones medidas es requisito, no recomendacion. Un agente que funciona a la primera no ensena nada. La linea base v0 del repo semilla obtiene recall 0,10: ese es tu punto de partida real.

## Que tienes que conseguir

1. Construye el servidor MCP del proyecto con las cinco herramientas: listar_specs, obtener_spec, trazabilidad, resultado_tests y version_plan.
2. Construye el agente de conformidad de spec: recibe un PR y la spec que declara implementar y emite veredicto estructurado.
3. Mide el agente v0 que trae el repo semilla contra el conjunto de evaluacion y guarda el informe.
4. Itera el agente hasta superar precision 0,80 y recall 0,85, y guarda el segundo informe.
5. Explica por escrito que cambiaste entre las dos versiones y por que mejoro.

Esta guia dice que conseguir, no como. Si pudieras seguirla sin pensar, no
aprenderias nada que sirva cuando cambie el contexto, que es lo que pasa en
cliente el primer dia.

## Entregable

Servidor MCP funcionando, agente publicando veredictos en PRs reales, informe de evaluacion con las dos iteraciones y sus metricas.

## Como se cierra

```bash
python -m aula_cli check S4a --prediccion pasa   # declara antes si crees que vas a pasar
python -m aula_cli cerrar S4a                    # sella localmente; pide al mentor la referencia
```

Si te atascas: `python -m aula_cli pista S4a` da el siguiente escalon. Si se agota la ventana,
`python -m aula_cli desbloquear S4a --motivo "..."` registra el desbloqueo; pide al mentor la referencia
antes de continuar. No penaliza las estaciones siguientes.

Criterios de superacion detallados en CRITERIOS.md.
