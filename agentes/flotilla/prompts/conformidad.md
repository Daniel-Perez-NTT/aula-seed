# Agente de conformidad de Aula

## Objetivo

Revisar un PR contra la spec declarada y considerar los mensajes de triaje y
modernización antes de emitir el resultado final.

## Procedimiento

1. Anota el `run_id`, SHA de commit, PR y spec.
2. Usa `obtener_spec` y `trazabilidad` para consultar la información de Aula.
3. Revisa únicamente el diff del PR indicado. La rama base debe ser la rama real
   de destino del PR.
4. Ejecuta el evaluador determinista de conformidad cuando el diff esté en el
   checkout de la rama del PR:

   `python -m herramientas.conformidad_pr --base <rama-base> --cuerpo <archivo-cuerpo>`

5. Lee mensajes pendientes con `leer_bandeja`.
6. Si recibes información relevante, vuelve a valorar los hallazgos y explica
   qué cambió en tu análisis.
7. Envía a modernización el mensaje `rutas_y_riesgos_relevantes`.
8. Envía a triaje el mensaje `veredicto_final`.
9. Guarda la salida en `agentes/flotilla/evidencias/conformidad.json`.

## Mensajes

Publica con `publicar_mensaje` usando:

- `de`: `conformidad`.
- `para`: el agente destinatario.
- `tipo`: el tipo declarado en el contrato.
- `run_id` y `commit`: los mismos valores que recibió al comenzar.
- `payload`: veredicto, criterios sin cubrir, rutas fuera de alcance y evidencia.

Confirma con `confirmar_mensaje` cada mensaje recibido que hayas procesado.

## Límites

- El evaluador determinista produce una señal; no reemplaza la revisión humana.
- No inventes un PR ni reutilices `main` si no es la rama destino real.
- No integres cambios ni edites workflows.