# CLAUDE.md

Contrato de contexto del proyecto Aula. Este fichero no es documentación: es la
configuración que hace que un agente trabaje bien en este repositorio por diseño
y no por suerte en el prompt. Se versiona y se revisa como código.

## Propósito

Aula es el núcleo de matrícula y expediente académico. Decide qué asignaturas se
admiten en una solicitud de matrícula aplicando la normativa del plan vigente, y
calcula el expediente del estudiante. De sus cálculos dependen procesos aguas
abajo, entre ellos la ordenación para becas, así que la reproducibilidad exacta
de los números es un requisito y no un detalle.

Es además el proyecto vertebrador del laboratorio del AoE Agentic DevOps: todo
lo que se construye aquí se evalúa contra las estaciones de `labs/`.

## Invariantes

Estas cinco cosas no se rompen nunca, aunque parezca que el código mejora:

1. El redondeo de la nota media se aplica **una sola vez y al final**. Nunca por
   asignatura. Cualquier redondeo intermedio altera la media y mueve la
   ordenación de becas.
2. Todo cálculo monetario o de calificación usa `Decimal`, nunca coma flotante.
3. Toda decisión de matrícula escribe una entrada de auditoría con el código y la
   versión de plan aplicados. Si una rama del código decide y no escribe traza,
   es un defecto.
4. Una matrícula en estado confirmada o posterior no cambia de plan de estudios.
5. Todo criterio de aceptación de una spec activa tiene al menos un test que lo
   referencia con la etiqueta `cubre:`. Sin eso el pipeline no pasa.

## Verificación

Antes de dar por terminado cualquier cambio, ejecuta y muestra la salida:

```bash
python3 -m pytest tests/ -q                    # suite completa
python3 -m aula_cli check                      # verificador de la estación activa
python3 -m agentes.conformidad.evaluar         # métricas del agente de conformidad
```

No digas que algo funciona. Enseña la salida en verde. Una afirmación no es
evidencia.

## Convenciones

- Conventional commits: `feat:`, `fix:`, `test:`, `refactor:`, `docs:`, `chore:`.
- Máximo 400 líneas de diff por PR. Es un límite duro del pipeline, no una guía.
  Si un cambio no cabe, se parte en varios.
- Un test por criterio de aceptación, con la etiqueta `cubre: SPEC-nnn/CA-nn` en
  el docstring.
- Español en documentación y en nombres de dominio. Inglés solo donde lo imponga
  una biblioteca.
- Sin dependencias nuevas sin justificarlas en el PR.

## Límites

Rutas que **no puedes modificar** sin aprobación humana explícita:

| Ruta | Motivo |
|------|--------|
| `src/aula/legado/` | Solo se toca en S5 y únicamente después de que exista la caracterización |
| `manifiestos/` | Es el gobierno de los agentes. Modificarlo desde un agente es que el vigilado escriba su propio permiso |
| `.github/workflows/` | Son los gates. Un agente que puede desactivar el gate que lo controla no está controlado |
| `labs/*/verificar.py` | Es la vara de medir del laboratorio |
| `evals/dorado*/` | Es el conjunto de evaluación. Optimizar contra él en lugar de contra el problema es el fallo clásico |

## Escalado

Ante una ambigüedad de la especificación: **pregunta, no asumas**. Una
implementación plausible derivada de una suposición no declarada es el defecto
más caro de este proyecto, porque pasa los tests que tú mismo escribiste sobre
esa suposición.

Cuando encuentres una ambigüedad, escríbela en el apartado de ambigüedades de la
spec correspondiente antes de implementar nada.
