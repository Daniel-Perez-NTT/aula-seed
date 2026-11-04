# Agente de propuesta de modernización

## Objetivo

Analizar el módulo heredado del expediente y comunicar riesgos y preguntas de
caracterización para S5.

## Procedimiento

1. Anota el `run_id`, SHA de commit y PR o escenario recibido.
2. Lee `src/aula/legado/calculadora_expediente_v1.py`.
3. Consulta SPEC-002 mediante `obtener_spec` y PLAN-2024 mediante `version_plan`.
4. Lee mensajes pendientes con `leer_bandeja`.
5. Compara el comportamiento del legado con la spec vigente. Separa lo que el
   código hace de lo que la spec exige.
6. Comunica a conformidad el mensaje `riesgos_del_legado`.
7. Comunica a triaje cualquier observación útil mediante `contexto_de_fallo`.
8. Guarda la salida en `agentes/flotilla/evidencias/modernizacion.md`.

## Límites

- En S4B solo lees `src/aula/legado/`.
- No refactorices ni cambies ese módulo antes de la caracterización de S5.
- No asignes una explicación empresarial que no esté documentada.
- Usa el mismo `run_id` y SHA de commit que los otros agentes.