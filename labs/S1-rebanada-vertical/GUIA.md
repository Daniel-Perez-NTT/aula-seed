# S1. Rebanada vertical a mano

| | |
|---|---|
| Semana | 2 a 4 |
| Horas estimadas | 24 |
| Módulos del itinerario | 2, 3, 4 |

## Objetivo

Construir a mano una función completa de matrícula: reglas de negocio, API,
pruebas, imagen de contenedor y pipeline. Durante S1 no uses agentes para
diseñar, escribir, modificar ni revisar el código del ejercicio. La idea es que
practiques el ciclo que luego necesitarás para poder evaluar código generado.

Esta guía explica un camino de trabajo para principiantes. La especificación
funcional está en [SPEC-001](../../specs/SPEC-001-matricula.md). Si esta guía y
la spec discrepan sobre el comportamiento de matrícula, prevalece la spec. Los
verificadores son la vara de medir: puedes leer [verificar.py](verificar.py),
pero no editarlo.

## Antes de empezar: entiende el punto de partida

1. Abre una terminal en la raíz del repositorio y consulta tu estado:

   ```bash
   python -m aula_cli estado
   python -m aula_cli guia S1
   ```

   **Por qué:** confirma que S0 está sellada y S1 es la estación activa. El CLI
   lleva el progreso local en `.aula/progreso.json`.

2. Lee, en este orden, `labs/S1-rebanada-vertical/CRITERIOS.md`,
   `specs/SPEC-001-matricula.md` y `labs/S1-rebanada-vertical/verificar.py`.

   **Qué estás aprendiendo:** la spec describe qué debe hacer el producto; los
   criterios describen qué evidencia se espera; el verificador automatiza una
   parte de esa comprobación. La spec enumera ocho criterios de aceptación,
   tres invariantes y casos límite. No empieces implementando una solución que
   todavía no puedes explicar con tus palabras.

3. Mira las piezas de código que ya existen:

   - `src/aula/api/app.py`: API FastAPI. `POST /matriculas` devuelve ahora 501,
     que significa “todavía no implementado”.
   - `src/aula/dominio/modelos.py`: tipos para planes, expedientes, solicitudes
     y matrículas.
   - `src/aula/dominio/estados.py`: esqueleto de estados y transiciones.
   - `src/aula/reglas/motor.py`: esqueleto de las reglas de S1.
   - `src/aula/reglas/planes.py` y `datos/planes/PLAN-2024.json`: carga del plan
     versionado que usarán las reglas.
   - `src/aula/auditoria.py`: escritura de decisiones en JSON Lines (un objeto
     JSON por línea).
   - `tests/utilidades.py`: constructores de datos reutilizables en tests.

   **Por qué:** el proyecto separa el dominio (reglas y modelos) de la API
   (entrada/salida HTTP). Así puedes probar las reglas sin arrancar un servidor.

4. Revisa cómo ejecutar los tests y cómo está configurado el CI actual:

   ```bash
   python -m pytest tests/ -q
   ```

   El workflow actual está en `.github/workflows/ci.yml`. En la semilla hay
   pruebas de estructura, pero todavía no están los tests propios de matrícula.
   Anota el resultado inicial y cualquier problema de entorno antes de cambiar
   código.

## Paso 1: convierte la spec en una lista de comportamientos

Antes de programar, haz una lista de casos de prueba para CA-01 a CA-08 y para
los casos límite de la spec. Puedes anotar la relación en una tabla sencilla:

| Regla | Situación que prepararé | Resultado que comprobaré |
|---|---|---|
| CA-01 | Momento anterior o posterior a la ventana | Ventana cerrada |
| CA-02 | Falta un prerrequisito | Esa línea se rechaza con el motivo |
| CA-03 | Se supera el límite de créditos | Se respeta el orden y el límite |

Completa la tabla para las demás reglas. Añade también los invariantes INV-01 a
INV-03: una sola traza por evaluación, una línea de salida por código pedido y
plan inmutable desde confirmada en adelante.

**Por qué:** cada fila será una prueba concreta. Si no puedes describir la
entrada y el resultado esperado, todavía hay una pregunta funcional que
resolver antes de escribir código.

**Ojo con el alcance:** la spec dice que si falta un grupo no hay límite de
plazas y que una asignatura con prerrequisito pendiente se rechaza aunque el
grupo esté lleno. También fija que la ventana incluye exactamente el instante
de inicio y el de fin.

## Paso 2: escribe primero las pruebas de las reglas

1. Crea `tests/test_reglas_matricula.py`. Usa los constructores de
   `tests/utilidades.py` para crear el plan, expedientes, registros y solicitudes.
2. Divide las pruebas por concepto (ventana, créditos, prerrequisitos,
   convocatorias, grupos, prioridad, estados y auditoría). Pon nombres que
   expliquen el comportamiento esperado.
3. Empieza con un caso sencillo que debe funcionar y ejecútalo:

   ```bash
   python -m pytest tests/test_reglas_matricula.py -q
   ```

   Es normal que falle mientras la implementación no exista. Lee el primer
   error; pytest suele indicar el archivo, la línea y el resultado que faltó.
4. Añade casos límite y verifica también los motivos de rechazo, no solo si una
   línea fue admitida. Comprueba que los resultados de una asignatura no
   descartan las demás.
5. Llega al menos a 15 tests propios entre toda la suite. Un test debe hacer una
   afirmación útil con `assert`; contar archivos o tests vacíos no demuestra el
   comportamiento.

**Por qué:** el test es un ejemplo ejecutable del contrato. Escribirlo antes de
la lógica evita adaptar, sin darte cuenta, lo que esperabas a lo que terminó
haciendo tu código.

## Paso 3: implementa el dominio por partes pequeñas

Trabaja en `src/aula/reglas/motor.py` y `src/aula/dominio/estados.py`. Ejecuta
los tests relacionados cada vez que completes un concepto.

1. Implementa la comparación de la ventana. Compara momentos ISO-8601 y trata
   ambos extremos como incluidos, tal como pide la spec.
2. Implementa la propiedad que indica si un grupo tiene plaza disponible.
3. Calcula créditos superados y pendientes usando el plan. Una convalidación
   cuenta como superada y no consume convocatoria.
4. Implementa la prioridad: primero más créditos superados; en empate, momento
   de solicitud más antiguo.
5. Evalúa las líneas en el orden solicitado. Para cada asignatura, comprueba
   pertenencia al plan, si ya está superada, prerrequisitos, convocatorias,
   plazas y límite de créditos. Usa la prioridad indicada por la spec para
   ordenar solicitudes concurrentes.
6. Implementa los estados y sus transiciones permitidas. Una matrícula
   confirmada o posterior no puede cambiar a otro plan.
7. Registra exactamente una decisión de auditoría por evaluación, incluida la
   versión de plan aplicada. Mantén la auditoría fuera de los cálculos puros
   cuando puedas; será más fácil probar cada parte.

**Por qué hacerlo en este orden:** primero resuelves operaciones pequeñas y
fáciles de probar; después las combinas para tomar la decisión completa. Cuando
un test falle, el área a investigar será más pequeña.

No inventes reglas que la spec no defina. Si una decisión del contrato HTTP o
del almacenamiento en memoria no está especificada, anótala en la bitácora y
elige una convención sencilla y consistente para esta primera versión. No
cambies la spec para hacer pasar el código.

## Paso 4: conecta las reglas con la API y la persistencia en memoria

1. En `src/aula/api/app.py`, sustituye el comportamiento pendiente de
   `POST /matriculas` por el flujo de alta. Conserva `/salud` y no implementes
   `GET /expedientes/{estudiante_id}`: eso pertenece a S2.
2. Define y prueba cómo la petición HTTP se convierte en
   `SolicitudMatricula`, cómo se obtiene el expediente y el plan, y cómo se
   devuelve la matrícula.
3. Guarda las matrículas en una estructura en memoria del proceso, como un
   diccionario o una lista. Para S1 no hace falta una base de datos: al reiniciar
   la aplicación esos datos pueden perderse.
4. Prueba la ruta con una petición HTTP. Puedes arrancar Uvicorn y enviar una
   petición desde otra terminal; también puedes usar el cliente de pruebas de
   FastAPI si instalas su dependencia HTTPX, que no está fijada ahora mismo en
   `requirements.txt`. Comprueba una petición válida, entradas inválidas y
   errores de negocio. Mantén claro qué errores son validación de la petición y
   cuáles son rechazos de matrícula.

**Por qué:** una rebanada vertical pasa por todas las capas: una petición entra,
se convierte en datos de dominio, las reglas deciden, se guarda el resultado y
la API responde. Probar solo una función no prueba ese recorrido completo.

La spec no define todos los detalles HTTP (por ejemplo, el formato de error o
los datos ficticios de ventana y grupos del servicio en memoria). Decide esos
detalles de forma explícita, documenta la convención y escribe tests para ella.

## Paso 5: revisa que los tests realmente protegen las reglas

Ejecuta la suite completa:

```bash
python -m pytest tests/ -q
```

Después ejecuta cobertura del dominio:

```bash
python -m pytest tests/ --cov=src/aula/dominio --cov-report=term-missing
```

La tabla muestra el porcentaje cubierto y las líneas no ejecutadas. Añade casos
que recorran las ramas relevantes hasta superar el 60 % en `src/aula/dominio`.
Lee también cualquier fallo de cobertura para decidir qué caso hace falta; no
añadas tests vacíos solo para subir el número.

**Por qué:** cobertura indica qué código se ejecutó durante las pruebas, pero
no si se comprobó el resultado correcto. La calidad viene de combinar casos
significativos y aserciones claras.

El verificador S1 exige suite verde y al menos 15 tests propios. No calcula por
sí mismo el 60 % de cobertura; aun así, el 60 % forma parte del entregable de
la guía y debes comprobarlo con el comando anterior.

## Paso 6: empaqueta el servicio en una imagen OCI multi-stage

1. Crea `Containerfile` o `Dockerfile` en la raíz. Usa dos etapas `FROM`: una
   etapa de construcción/preparación y una etapa final de ejecución. La pista de
   S1 explica la intención: dependencias y preparación en la primera; solo lo
   necesario para ejecutar el servicio en la final.
2. Asegúrate de que la imagen instala las dependencias, incluye el código y
   arranca Uvicorn sirviendo `aula.api.app:app` en `0.0.0.0`.
3. Construye localmente con Podman o Docker:

   ```bash
   podman build -t aula:s1 .
   ```

   Si usas Docker, cambia `podman` por `docker`.
4. Arranca la imagen y consulta `/salud` desde otra terminal. Comprueba también
   `/docs` y una petición de matrícula.

**Qué es una imagen:** es un paquete reproducible con el programa y lo que
necesita para ejecutarse. Multi-stage significa que se construye en etapas y la
imagen final puede excluir herramientas que solo hacían falta al prepararla.

## Paso 7: amplía el pipeline para que compruebe el cambio

Edita `.github/workflows/ci.yml` para que el workflow instale las dependencias
del proyecto, ejecute los tests con cobertura y construya la imagen. Mantén los
checks actuales de tamaño de PR y formato de commits. El workflow ya se ejecuta
en pull requests.

**Por qué:** que algo funcione en tu ordenador no garantiza que funcione en un
entorno limpio. CI repite las comprobaciones automáticamente cuando propones
cambios.

La guía original pide publicación de imagen además del build. La configuración
actual solo se activa en pull requests y no publica imágenes. Primero deja
verde el pipeline de build y tests. Después, si tienes un registry habilitado y
credenciales configuradas en los secretos del repositorio, añade un flujo de
publicación asociado a la rama o etiqueta acordada. No escribas credenciales en
el código ni en el workflow. Si no tienes acceso al registry, registra esa
limitación en la bitácora y solicita la configuración al mentor.

## Paso 8: registra tus tiempos mientras trabajas

Añade a `labs/S1-rebanada-vertical/bitacora.md` una línea por tarea con fecha,
descripción y duración real. Por ejemplo:

```text
2026-10-09 | Casos de ventana y límites | 45 min
2026-10-09 | Implementación del motor | 2 h 10 min
```

También puedes usar `python -m aula_cli bitacora "..."` para añadir una nota
con marca de tiempo automática, y luego completar la duración por tarea en el
archivo. Incluye pruebas, API, contenedor, CI y cualquier bloqueo.

**Por qué:** estas horas son tu línea base personal sin agentes. En estaciones
posteriores podrás comparar tareas equivalentes con datos tuyos.

## Paso 9: revisión final y cierre

1. Revisa el diff con `git diff` y asegúrate de entender cada cambio. Comprueba
   que no modificaste `labs/S1-rebanada-vertical/verificar.py`.
2. Repite desde un entorno limpio, si puedes: instala dependencias, ejecuta la
   suite y construye la imagen. Revisa que CI termine en verde.
3. Confirma manualmente los entregables: endpoint funcional, reglas probadas,
   al menos 15 tests, cobertura del dominio superior al 60 %, Containerfile o
   Dockerfile multi-stage, pipeline que construye la imagen y publicación si
   tienes registry disponible; bitácora con tiempos por tarea.
4. Ejecuta el verificador declarando tu predicción antes de ver el resultado:

   ```bash
   python -m aula_cli check S1 --prediccion pasa
   ```

   Si algún criterio falla, usa su detalle para decidir el siguiente cambio y
   repite el check. Si crees que todavía hay algo pendiente, declara `falla`.
5. Cuando todo esté verde, sella la estación:

   ```bash
   python -m aula_cli cerrar S1
   ```

   El cierre local no sustituye la revisión del mentor. Pídele la referencia de
   S1 y compara las decisiones con las tuyas.

## Qué comprueba automáticamente el verificador S1

`python -m aula_cli check S1` comprueba que la suite está verde, existe la
máquina de estados, existe una imagen multi-stage, CI construye la imagen, hay
al menos 15 tests y la bitácora tiene una entrada fechada. La cobertura superior
al 60 % y la publicación de la imagen aparecen en el entregable descrito, pero
no tienen un check automático en esta versión del verificador: compruébalas por
separado.

## Si te atascas

Tras releer el criterio y el fallo concreto, puedes pedir la siguiente pista:

```bash
python -m aula_cli pista S1
```

Hay tres escalones y cada apertura queda registrada. Si se agota la ventana de
la estación, registra el desbloqueo y acuerda con el mentor la referencia antes
de incorporarla:

```bash
python -m aula_cli desbloquear S1 --motivo "describe qué intentaste y dónde te bloqueaste"
```

El desbloqueo no descarga archivos ni reemplaza tu trabajo.
