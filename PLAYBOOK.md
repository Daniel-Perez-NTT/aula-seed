<!-- version: v1.0 | estado: para entregar | audiencia: students de la cohorte septiembre 2026 | fuente: diseño del laboratorio v0.3 -->

# Playbook del laboratorio

> Adaptación de la semilla: consulta primero [README.md](README.md).
> Ejecuta los comandos como `python -m aula_cli ...` desde la raíz.
> Los cierres se registran localmente; las referencias las entrega el mentor.
> La evaluación privada y el sellado independiente en CI requieren configuración
> de la organización y no están implementados en esta plantilla.

**Proyecto Aula | AI Engineering Talent Factory | AoE Agentic DevOps**
Cohorte septiembre 2026 | 196 horas | 10 estaciones | 12 semanas

---

## Lo primero

En cuatro meses vas a entrar en el equipo de un cliente real. No como observador:
como alguien de quien se espera que aporte desde la primera semana. Este
laboratorio existe para que cuando llegue ese día ya lo hayas hecho todo una vez.

Vas a construir un sistema completo, de la primera línea al despliegue, y vas a
construirlo con agentes. Pero el objetivo no es que aprendas a usar un agente:
eso lo aprende cualquiera en un fin de semana. El objetivo es que aprendas a
**gobernar lo que un agente produce**, que es lo que casi nadie sabe hacer y lo
que los clientes están empezando a pagar.

Una advertencia que va en serio: la parte difícil de este laboratorio no es
escribir código. Es no dejar pasar el código que está mal.

---

## 1. Qué vas a construir

**Proyecto Aula**: el núcleo de matrícula y expediente académico de una
universidad. Un servicio que decide qué asignaturas puede matricular un
estudiante aplicando la normativa vigente, y que calcula su expediente.

Elegimos este dominio por una razón concreta: **acabas de vivirlo desde el otro
lado**. Sabes qué pasa cuando un prerrequisito te bloquea, cuando un grupo se
llena, cuando repites una asignatura y no tienes claro cómo cuenta en tu media.
Eso significa que puedes detectar que una regla está mal definida sin que nadie
te enseñe el negocio primero. En un proyecto de seguros tardarías tres semanas
solo en entender qué es una franquicia.

El dominio es académico. El patrón no. Un motor de reglas versionado por plan de
estudios es exactamente la misma pieza que un motor de tarificación versionado
por producto en una aseguradora, o un motor de scoring versionado por política de
riesgo en un banco. En la estación final tendrás que hacer esa traducción
explícita para la torre a la que te incorpores.

### Lo que existirá al final

| Pieza | Qué es |
|-------|--------|
| Servicio de matrícula | API con validación de prerrequisitos, límites de créditos, capacidad de grupo y lista de espera |
| Motor de expediente | Cálculo de nota media ponderada, créditos superados y progreso, con precisión decimal exacta |
| Módulo heredado modernizado | Una calculadora antigua sin tests que caracterizarás y refactorizarás |
| Servidor MCP propio | El contexto del proyecto expuesto como herramientas para cualquier agente |
| Agente de conformidad | Un agente que tú construyes y que revisa PRs contra su especificación |
| Flotilla de tres agentes | Conformidad, triaje y modernización trabajando sobre el mismo contexto |
| Pipeline con gates | Tests, trazabilidad, conformidad, seguridad y gobierno de agentes |
| Todo desplegado | Servicio en la nube, con reversión probada y MTTR medido |

Eso es tu portfolio. Es lo que enseñarás en la defensa y lo que podrás enseñar en
una entrevista dentro de dos años.

---

## 2. Cómo funciona el laboratorio

### Trabajas solo, pero no aislado

Cada uno tiene su repositorio y su proyecto completo. Además perteneces a una
**escuadra de tres o cuatro**, que es tu grupo de mentoría. Con tu escuadra
revisas PRs cruzados, construyes la flotilla multiagente y os inyectáis fallos
mutuamente en la penúltima estación.

### El repositorio es la plataforma

No hay campus virtual, ni plataforma de cursos, ni hoja de cálculo donde apuntar
el progreso. Todo está en tu repositorio: las guías, los criterios, las pistas,
el verificador y tu progreso. Trabajas desde el primer día con las mismas
herramientas que usarás en cliente.

### Tú puedes saber si has terminado bien

Esto es lo más importante de todo el diseño. **No dependes de que un mentor te
diga si algo está bien.** Cada estación tiene un verificador que ejecutas cuando
quieras y que te dice, criterio a criterio, qué está en verde y qué no, y por qué.

El mentor no está para decirte "está bien". Está para preguntarte "por qué lo has
hecho así", que es una conversación mucho más útil y para la que hay tiempo
precisamente porque la primera no hace falta.

### Nunca te quedas bloqueado

Si te atascas tienes tres escalones de pista. Si se acaba la ventana de la
estación y sigues atascado, ejecutas `python -m aula_cli desbloquear --motivo "..."`.
El comando registra el desbloqueo; el mentor debe entregarte la referencia por
separado. Conserva tu trabajo, incorpora la nueva base y continúa.

Esto no se te deniega nunca y no penaliza las estaciones posteriores. Lo decimos
en serio: preferimos que llegues a la estación 8 habiendo desbloqueado la 4, a
que te quedes clavado en la 4 y te pierdas donde está la mitad del valor. Lo que
sí se evalúa es tu bitácora: qué intentaste antes de desbloquear.

---

## 3. Los comandos

Todo el laboratorio se opera con un comando.

```bash
python -m aula_cli estado                          # dónde estás y qué te falta
python -m aula_cli guia                            # qué tienes que conseguir en la estación activa
python -m aula_cli check --prediccion pasa         # verifica, tras declarar si crees que vas a pasar
python -m aula_cli pista                           # siguiente escalón de ayuda
python -m aula_cli bitacora "lo que sea"           # anota en tu cuaderno
python -m aula_cli cerrar                          # sella localmente; solicita la referencia
python -m aula_cli desbloquear --motivo "..."      # registra el desbloqueo; no copia archivos
```

### Sobre `--prediccion`

Antes de verificar, declaras si crees que vas a pasar. El sistema compara tu
predicción con el resultado y calcula tu **calibración**.

No es un juego. La calibración mide si sabes lo que sabes, y resulta ser el mejor
predictor de si vas a aprobar por error un PR defectuoso cuando estés en cliente.
Alguien que cree que va bien y falla sistemáticamente es exactamente el perfil de
riesgo que este programa existe para no producir. Si tu calibración es mala, tu
mentor lo verá y hablaréis de ello: no es un castigo, es la señal más útil que
tenemos de que hay algo que revisar en cómo te evalúas.

### Cómo se ve un check

```
verificando S2: Spec-Driven Development

  OK   S2-01      existen specs activas en specs/
  OK   S2-02:SPEC-001  SPEC-001: todos los criterios tienen test que los referencia
 FALLA S2-02:SPEC-002  SPEC-002: todos los criterios tienen test que los referencia
        sin cubrir: CA-04, CA-07
  OK   S2-05      la suite completa está en verde
 FALLA S2-06      los tests fallan al mutar la implementación (no son decorativos)
        mutaciones que sobreviven (la suite sigue verde): == -> !=

quedan criterios en rojo
```

Fíjate en el último: el verificador **rompe tu implementación a propósito** y
exige que tus tests lo detecten. Si cambia un `==` por un `!=` y tus tests siguen
en verde, tus tests no están comprobando nada. Es la misma pregunta que te vamos
a hacer sobre el código que genere un agente.

---

## 4. El ciclo de una estación

Siempre igual, sea cual sea la estación:

1. **`python -m aula_cli guia`**. Lee qué hay que conseguir. La guía dice el qué, no el cómo.
   Es deliberado: si pudieras seguirla sin pensar, no aprenderías nada que sirva
   cuando el contexto cambie, y en cliente cambia el primer día.
2. **Lee `CRITERIOS.md`**. Sabes exactamente cómo se te va a medir. También
   puedes leer `verificar.py`: no es un examen secreto. Lo que no puedes es
  modificarlo: es la vara de medir. Esta semilla cierra localmente con su copia;
  la organización debe configurar la validación independiente si la requiere.
3. **Trabaja**. Con agente o sin él, según la estación.
4. **`python -m aula_cli check --prediccion`** las veces que quieras. Es barato y es local.
5. **`python -m aula_cli bitacora`** cuando algo te sorprenda, te bloquee o te salga mal. No
   escribas el resumen bonito al final: escribe en caliente. Esa bitácora es la
   materia prima de tu lámina final "lo que hoy haría distinto".
6. **`python -m aula_cli cerrar`**. Se sella localmente la estación. Solicita al mentor la
  referencia y compárala con la tuya; el comando no descarga soluciones.

---

## 5. Las diez estaciones

| ID | Estación | Semanas | Horas | Qué demuestras |
|----|----------|---------|-------|----------------|
| S0 | Bootstrap y disciplina de repositorio | 1 | 8 | Sabes montar un repo donde se pueda gobernar el trabajo |
| S1 | Rebanada vertical a mano | 2 a 4 | 24 | Sabes escribir, no solo revisar |
| S2 | Spec-Driven Development | 5 a 6 | 26 | Sabes derivar código verificable de una especificación |
| S3 | Ingeniería de contexto | 6 a 7 | 24 | Sabes preparar un repo para que un agente trabaje bien |
| S4a | Servidor MCP y agente propio | 8 a 10 | 28 | Sabes construir un agente y medirlo |
| S4b | Flotilla multiagente | 10 | 12 | Sabes coordinar varios agentes sobre un contexto común |
| S5 | Modernización del legado | 10 a 11 | 22 | Sabes tocar código heredado sin romperlo |
| S6 | Gobierno del agente | 11 | 18 | Sabes poner un agente en producción en un entorno regulado |
| S7 | Despliegue, fallo y MTTR | 12 | 24 | Sabes desplegar, romper y recuperar |
| S8 | Defensa ante panel | 12 | 10 | Sabes contarlo y defenderlo |

**130 de las 196 horas están en S2 a S6.** Es donde está el diferencial y donde
deberías concentrar tu energía.

### S0. Bootstrap (8 h)

Proteges la rama, montas CODEOWNERS, la plantilla de PR y un límite de 400 líneas
de diff por PR.

Ese límite te va a parecer una tontería esta semana. En la semana 8, cuando un
agente te genere en diez minutos más código del que puedes leer en un día, será
lo único que impida que apruebes cosas sin mirarlas.

### S1. Rebanada vertical a mano (24 h)

Construyes la primera funcionalidad completa, con tests, contenedor y pipeline,
**sin usar ningún agente**.

Sabemos que es contraintuitivo en un programa de desarrollo agéntico. La razón es
simple: no se puede revisar lo que no se sabe escribir. Si llegas al módulo 5 sin
haber escrito nunca un test a mano, aceptarás lo que te proponga el agente porque
no tendrás criterio con el que discrepar.

Además, apunta tus tiempos. Es tu línea base. En S2 y S3 vas a medir tu propio
salto de productividad con datos tuyos, no con la cifra de un informe de un
analista que no te conoce.

### S2. Spec-Driven Development (26 h)

Escribes la especificación antes que el código, numeras los criterios de
aceptación, y cada uno tiene que tener un test que lo referencie. El pipeline lo
comprueba y bloquea el merge si falta alguno.

**Aviso**: la spec de partida contiene una ambigüedad real y puesta a propósito.
Tiene que ver con cómo cuenta en tu nota media una asignatura que has repetido, y
con qué pasa con las convalidadas. Si no la detectas, el agente producirá una
implementación perfectamente plausible y equivocada, y tú la aprobarás porque los
tests que escribiste sobre tu suposición pasarán.

Detectarla antes de implementar es criterio de evaluación explícito. Y sí, es
exactamente lo que te va a pasar en cliente con una especificación funcional real.

### S3. Ingeniería de contexto (24 h)

Conviertes el repositorio en un sitio donde el agente trabaja bien por diseño:
`CLAUDE.md` con invariantes y límites, allowlist de permisos, hooks deterministas,
subagentes acotados. Comparas Claude Code con OpenCode y entregas un criterio de
elección defendible, no un "cuál me gusta más".

La idea central de la estación: **lo innegociable no se pide en lenguaje natural,
se hace determinista**. Si algo tiene que pasar siempre, va en un hook o en un
gate del pipeline, no en un prompt.

Se mide tu **ratio de diff aceptado sin comentario**. Un ratio alto no es
productividad, es aceptación ciega. Un ratio de cero tampoco es bueno: significa
que no estás usando la herramienta. Hablaremos contigo por encima de 0,40 y por
debajo de 0,10.

### S4a. Servidor MCP y agente propio (28 h)

**Es el corazón del laboratorio.** Hasta aquí has conducido agentes. Aquí
fabricas uno.

Construyes el servidor MCP que expone el contexto del proyecto, y construyes el
agente de conformidad: recibe un PR y la spec que dice implementar, y emite un
veredicto. Qué criterios quedan sin cubrir, qué se ha tocado fuera del alcance,
qué tests son sospechosos.

Y lo mides. **Dos iteraciones medidas es requisito, no recomendación.** El repo
semilla trae una versión ingenua que obtiene un recall de 0,10: ese es tu punto de
partida real, y tienes que llegar por encima de 0,85 explicando qué cambiaste y
por qué funcionó.

Un consejo que te va a ahorrar horas: haz el núcleo determinista. Cobertura,
alcance y riesgo se calculan analizando la spec, el diff y los tests. Si dejas que
el modelo decida el veredicto, el mismo PR te dará resultados distintos entre
ejecuciones y no te servirá como gate. El modelo sirve para redactar la
explicación, no para decidir.

Si tu base de programación es más floja, tienes una versión con andamiaje: el
esqueleto viene hecho y te concentras en la lógica y en la evaluación. Lo decide
tu mentor con tu evaluación inicial y **no te penaliza la nota** si tu medición es
sólida.

### S4b. Flotilla (12 h, con tu escuadra)

Tres agentes sobre el mismo servidor MCP. Lo que se evalúa no es que funcionen,
es el **contrato**: qué ve cada uno, qué escribe, qué se pasan, y qué pasa cuando
dos quieren tocar el mismo fichero. Es literalmente la conversación que se tiene
en cliente al pasar de un piloto a una flota.

### S5. Modernización del legado (22 h)

Te dan un módulo heredado de unos cientos de líneas, sin tests, con números
mágicos y código muerto. Y con dos comportamientos que no están documentados en
ninguna parte y de los que depende un proceso real aguas abajo.

**REGLA DURA: está prohibido pedirle al agente que refactorice antes de que
exista la caracterización.** El verificador comprueba el orden en tu historial de
git. Es la falta más grave del laboratorio y suspende la estación.

No es una norma arbitraria. Es lo que vas a ver hacer mal en cliente: alguien
suelta un agente sobre código heredado que nadie entiende, el resultado parece
más limpio, y tres semanas después un proceso que nadie estaba mirando devuelve
números distintos.

### S6. Gobierno (18 h)

Escribes el Agent Release Manifest de cada agente y haces que el pipeline bloquee
el merge si falta, si el hash no coincide o si la evaluación caducó. Declaras el
nivel de autonomía de cada agente e implementas el control técnico que lo hace
cierto: declararlo no basta.

Y pruebas que el gate funciona **rompiéndolo**: abres a propósito un PR que
debería ser bloqueado y compruebas que lo bloquea. Un gate que nunca ha rechazado
nada no está verificado.

Ningún agente tuyo llega a nivel N4 en el laboratorio. El ejercicio es argumentar
por escrito qué haría falta para llegar. Esa argumentación es material directo de
una conversación con un responsable de seguridad de un banco.

### S7. Despliegue, fallo y MTTR (24 h)

Despliegas. Luego alguien de tu escuadra rompe tu entorno y tú rompes el suyo.
Diagnosticas y arreglas, dos rondas: la primera sin agente, la segunda con el
agente de triaje. Mides ambas.

Esa comparación es un dato tuyo. Vale más en una conversación de cliente que
cualquier estadística de un informe.

### S8. Defensa (10 h)

Veinte minutos ante el Head of AoE, SMEs y gente de las torres. Estructura fija,
incluida la lámina de traducción del patrón a tu torre de destino.

Y una lámina más: **una decisión técnica que tomaste y que hoy tomarías
distinta**. No es humildad de manual ni un truco de entrevista. Es lo que mejor
predice si vas a aguantar una conversación técnica con un arquitecto del cliente,
y el panel lo sabe.

---

## 6. Las rondas adversariales

Tres veces durante el laboratorio, tu mentor va a meter en tu rama un PR generado
con un agente que contiene **exactamente un defecto**. Tienes 45 minutos para
emitir veredicto y justificarlo.

| Ronda | Semana | Qué tipo de defecto esperar |
|-------|--------|------------------------------|
| R1 | 6 | Visible leyendo con atención |
| R2 | 9 | Solo aparece si ejecutas y compruebas |
| R3 | 11 | Requiere razonar sobre el dominio |

Encontrarlo puntúa. **Declarar conforme un PR defectuoso es el fallo grave del
ejercicio.** No porque queramos pillarte, sino porque es exactamente lo que va a
pasar en cliente: te van a llegar diffs generados por IA, plausibles, bien
formateados, con el pipeline en verde, y con un error dentro.

Tu tasa de detección acumulada aparece en el panel de la cohorte. Es, además, la
frase más vendible del programa: no salís entrenados para producir código con IA,
salís entrenados para no dejar pasar lo que la IA produce mal.

### La checklist

Está en la plantilla de PR y la usas en cada revisión, tuya o de un compañero:

1. ¿Cada criterio de aceptación tocado tiene test que lo referencia?
2. ¿Los tests fallan si rompo la implementación a propósito?
3. ¿Hay algún test omitido, marcado o con aserción vacía?
4. ¿El diff contiene algo fuera del alcance declarado en la spec?
5. ¿Alguna dependencia nueva existe, se mantiene y era necesaria?
6. ¿Se conserva la precisión decimal y el redondeo se aplica una sola vez, al final?
7. ¿La traza de auditoría se escribe en todas las ramas del código nuevo?
8. ¿La cobertura sube porque se cubre lógica o porque se añadió código trivial?
9. ¿Entiendo lo suficiente este cambio como para defenderlo ante el cliente?

La novena no es de relleno. **Si la respuesta es no, el PR no se aprueba, aunque
el pipeline esté en verde.**

---

## 7. Cuando te atascas

Publicado y sin excepciones, porque esperar a la daily te cuesta el día entero.

| Tiempo bloqueado | Qué haces |
|------------------|-----------|
| 0 a 15 min | Relees `CRITERIOS.md` y ejecutas `python -m aula_cli check` para ver qué criterio falla exactamente, no el síntoma |
| 15 min | `python -m aula_cli pista`, escalón 1 |
| 30 min | `python -m aula_cli pista`, escalón 2, y documentación oficial del fabricante |
| 45 min | Publicas en el canal de la cohorte con el formato de tres líneas |
| 90 min sin respuesta, o problema duro de entorno | Mentor, en la daily o fuera de ella |
| Fin de la ventana de la estación | `python -m aula_cli desbloquear` y sigues. Sin negociación |

### El formato de tres líneas

```
Qué intento:     [una línea]
Qué obtengo:     [la salida exacta del verificador o del error, no tu resumen]
Qué he probado:  [una línea]
```

Parece burocracia y no lo es: en un porcentaje alto de los casos resolverás el
problema mientras lo escribes. Es también el gesto exacto que te van a pedir en
el canal de un squad de cliente, donde nadie tiene tiempo de reconstruir tu
contexto a partir de un "no me funciona".

---

## 8. Cómo se te evalúa

| Dimensión | Peso |
|-----------|:----:|
| Agente propio, MCP y evaluación | 25% |
| SDD y trazabilidad | 20% |
| Ingeniería de contexto y operación | 20% |
| Gobierno, evidencia y coste | 15% |
| Criterio de revisión (rondas adversariales y revisiones a compañeros) | 10% |
| Fundamentos SDLC | 10% |

El 80% está en las capas agénticas. No es casualidad: es donde está el
diferencial de mercado y donde queremos que inviertas tu tiempo.

### Las seis métricas

| Métrica | Umbral |
|---------|--------|
| Trazabilidad de spec | 100% de criterios con test |
| Detección adversarial | Al menos 2 de 3 defectos |
| Calidad de tu agente | Precisión ≥ 0,80 en la versión final |
| Diff aceptado sin comentario | ≤ 0,40 |
| Coste por criterio verificado | Registrado, con tendencia a la baja |
| Evidencia completa en PRs | ≥ 0,90 |

### Los cuatro niveles

- **No apto**: alguna dimensión de peso alto por debajo del umbral.
- **En desarrollo**: cumples umbrales pero no demuestras criterio propio.
- **Apto**: cumples y justificas tus decisiones.
- **Destacado**: cumples, justificas, y tu agente o tu spec entra en el
  repositorio de activos del AoE **con tu nombre**, como material reutilizable
  por el resto del área.

Ese último nivel es real y tiene consecuencias. Varios de los activos que usan
hoy los equipos del AoE salieron de trabajo de alguien que empezó donde estás tú.

---

## 9. Reglas del juego

**Lo que se espera de ti**

- Que uses agentes en todo lo que no sea S1, y que uses el criterio en todo.
- Que escribas la bitácora en caliente, no el resumen bonito del viernes.
- Que revises los PRs de tu escuadra con la misma exigencia que los tuyos.
- Que pidas pista antes de perder una tarde, y que desbloquees antes de perder
  una semana.
- Que preguntes cuando una especificación sea ambigua, en lugar de suponer.

**Lo que no**

- No modifiques los verificadores: alterar la vara de medir invalida la evidencia.
  El cierre de esta plantilla es local y no sustituye la revisión del mentor.
- No optimices contra el conjunto de evaluación. No tienes acceso a sus
  etiquetas, y aunque lo tuvieras estarías entrenándote para aprobar un examen en
  lugar de para resolver un problema.
- No aceptes un diff que no entiendes. Ni aquí ni nunca. Quien acepta a ciegas
  hereda cada error sin filtro, y en cliente el error lleva tu nombre en el
  historial de git.

**Lo que puedes esperar de nosotros**

- Una daily de 15 minutos con tu mentor, todos los días.
- Feedback escrito cada viernes, con nombre y apellidos de lo que va bien y de lo
  que no.
- Una sesión técnica semanal con un SME del área.
- Retro mensual donde lo que digas cambia el programa. La biblioteca de pistas de
  la próxima cohorte la vais a escribir vosotros con lo que os atasque a vosotros.

---

## 10. Arranque

```bash
git clone <tu-repositorio> aula-students
cd aula-students
python -m pip install -r requirements.txt
python -m aula_cli estado
python -m aula_cli guia S0
```

Si algo del entorno no arranca, no pierdas la mañana: el contenedor de desarrollo
está definido en `.devcontainer/` y levanta todo preinstalado. Un problema de
entorno es la peor forma de perder un día, porque no enseña nada.

---

## Y una última cosa

Vas a usar agentes que escriben código más rápido de lo que tú puedes leerlo. Eso
no te hace más productivo por sí solo: te hace responsable de más código.

La pregunta que va a decidir tu carrera los próximos años no es si sabes hacer que
un agente escriba una función. Es si, cuando te enseñe doscientas líneas
razonables, sabes ver la que está mal.

Eso es lo que vamos a entrenar durante doce semanas.
