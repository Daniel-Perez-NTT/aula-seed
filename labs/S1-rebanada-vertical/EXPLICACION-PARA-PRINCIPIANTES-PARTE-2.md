# S1 explicado desde cero: continuación

Esta parte continúa la explicación para principiantes y cubre el entorno, Docker, GitHub Actions, Pull Requests y el cierre de S1.

## 8. Entorno virtual y dependencias

Python es el lenguaje del proyecto. Una dependencia es una biblioteca externa
que el programa necesita. `requirements.txt` enumera las dependencias para que
se puedan instalar de forma repetible.

Un entorno virtual es una instalación privada de paquetes dentro del proyecto.
En Windows está en `.venv/`. No hace falta ser administrador porque sus
archivos viven en el repositorio, no en las carpetas protegidas del sistema.

Se usa así:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Al principio la instalación falló porque `PyYAML==6.0.2` no tenía una rueda
precompilada apropiada para el Python 3.14 del equipo. Pip intentó compilarla y
pidió herramientas C++ de Windows. Se actualizó la dependencia a 6.0.3, que sí
proporciona un paquete precompilado para ese entorno.

Por claridad, usa siempre el Python de `.venv` para ejecutar pytest, Uvicorn y
el CLI del laboratorio. Así evitas instalar algo en un Python y ejecutarlo con
otro.

## 9. Docker, imágenes y contenedores

### 9.1 Qué son

Una imagen es un paquete con el programa y las dependencias que necesita. Un
contenedor es un proceso que se ejecuta usando esa imagen. Se parece a entregar
una caja preparada, para que otra máquina no tenga que reconstruir a mano el
entorno de Python.

Docker es una herramienta que construye imágenes y ejecuta contenedores. Podman
es otra herramienta compatible con muchas de las mismas órdenes. En este equipo
no se encontró ni Docker ni Podman, así que no se pudo construir la imagen
localmente.

### 9.2 Qué hace el Dockerfile

El `Dockerfile` tiene dos instrucciones `FROM`, por lo que utiliza dos etapas:

1. `build` instala las dependencias en `/install`.
2. `runtime` copia esas dependencias y el código necesario para ejecutar
   Uvicorn.

Esta separación se llama multi-stage. Permite que la imagen de ejecución no
contenga cada herramienta temporal usada durante la preparación.

`.dockerignore` lista archivos que Docker no necesita enviar al construir la
imagen, como `.git`, `.venv`, los tests y la caché de pytest.

### 9.3 Cómo se comprobará sin Docker local

El workflow de GitHub Actions ejecuta el build en un runner Linux que sí
dispone de Docker. Después arranca el contenedor y solicita `/salud`. Así se
comprueba la imagen aunque el portátil no pueda ejecutarla. Que el YAML tenga
esos pasos no demuestra todavía que hayan funcionado: hay que ver el resultado
de una ejecución real en GitHub Actions.

## 10. CI, Pull Requests y publicación

### 10.1 ¿Qué es CI?

CI significa integración continua. Cada vez que proponemos cambios, un servidor
limpio ejecuta automáticamente una serie de controles. En este workflow:

1. Se valida el tamaño del Pull Request, con el límite de S0 de 400 líneas de
   diff.
2. Se validan los mensajes de commit con el formato Conventional Commits.
3. Se instalan dependencias y se ejecutan las pruebas.
4. Se construye la imagen Docker.
5. Se arranca el contenedor y se comprueba `/salud`.
6. Cuando los cambios llegan a `main`, otro job intenta publicar la imagen en
   GitHub Container Registry (GHCR).

### 10.2 Qué es un Pull Request

Un Pull Request (PR) es una propuesta para integrar los commits de una rama
en otra, normalmente en main. GitHub muestra el diff, ejecuta CI y permite
revisar el cambio antes de integrarlo.

El workflow de este repositorio limita cada PR a 400 líneas de diff. Suma las
líneas añadidas y eliminadas respecto a la rama destino; no suma cada commit
por separado. Por eso un PR puede fallar aunque el código funcione: este
control revisa el tamaño del cambio, no la lógica.

En este trabajo aparecieron dos casos concretos. El PR del motor dio 410
líneas (383 añadidas y 27 eliminadas), así que se redujo para pasar el control.
El documento completo para principiantes añadía 512 líneas; se partió al
inicio de la sección 8 y se envió en dos PRs más pequeños. No se cambió el
límite ni se desactivó el control.

### 10.3 ¿Qué significa publicar la imagen?

GHCR es un registro de imágenes de contenedor de GitHub. Publicar significa
subir ahí la imagen construida, para que pueda descargarse por su etiqueta.
`GITHUB_TOKEN` da al workflow credenciales limitadas para publicar; no hay que
guardar una contraseña en el repositorio.

En este workflow la publicación ocurre en pushes a `main`, no al crear un PR.
Por tanto, primero se revisa y se integran los PRs con CI verde; después se
comprueba en GitHub que el job `publicar` terminó bien y que el paquete aparece
en Packages. Si ese job falla por permisos, el build puede haber pasado, pero
la estación aún no ha demostrado la publicación que pide su entregable.

### 10.4 El recorrido de un PR, paso a paso

Una rama es una línea de trabajo separada. Permite preparar un cambio y
proponerlo sin modificar directamente main. Estos fueron los nombres usados
para organizar S1:

| Rama | Para qué se usó |
|---|---|
| feat/s1-matricula | Motor de matrícula y sus pruebas. |
| feat/s1-api-ci | Estados, API, dependencias, Dockerfile y workflow. |
| docs/s1-guia | Guía del ejercicio y bitácora. |
| docs/s1-explicacion | Primera parte de la explicación. |
| docs/s1-explicacion-parte-2 | Continuación de la explicación. |
| chore/s1-cierre | Registro del cierre local de S1 en .aula/progreso.json. |

Los comandos siguientes se ejecutan en PowerShell desde la carpeta del
proyecto. Primero miro la rama activa y los cambios pendientes:

    git branch --show-current
    git status --short

git status muestra archivos modificados, nuevos y preparados. Antes de un PR
de documentación quiero evitar incluir por accidente el archivo de progreso,
así que añado rutas concretas en vez de usar git add ..

Para empezar una rama basada en la versión actual de main:

    git fetch origin
    git switch main
    git pull --ff-only origin main
    git switch -c docs/mi-cambio origin/main

origin es el nombre habitual del repositorio remoto de GitHub. fetch trae
información nueva sin cambiar mis archivos; pull --ff-only actualiza main sin
crear una mezcla automática; switch -c crea y activa la rama nueva. Cada rama
debe tener un objetivo claro y acotado.

Después preparo solo los archivos que pertenecen a ese objetivo y reviso la
propuesta antes de guardarla como commit:

    git add labs/S1-rebanada-vertical/EXPLICACION-PARA-PRINCIPIANTES-PARTE-2.md
    git diff --cached --stat
    git diff --cached --name-only

El área preparada, llamada staging, es la lista de cambios que entrarán en el
siguiente commit. Si aparece un archivo inesperado, lo saco de esa lista antes
de continuar. Luego guardo el cambio y lo subo a GitHub:

    git commit -m "docs(s1): explicar el proyecto para principiantes"
    git push -u origin docs/mi-cambio

Un commit es una versión identificada del cambio. El mensaje sigue
Conventional Commits: empieza por una categoría como feat, test, docs o chore,
puede indicar el área entre paréntesis y explica el cambio. push envía la rama
al repositorio remoto. -u la vincula para que los siguientes git push sepan
dónde enviar los cambios.

En la página de GitHub, elijo Compare & pull request y compruebo que la base
sea main y que la rama de origen sea la que acabo de subir. En el PR reviso
Files changed, el tamaño y Checks. Solo cuando entiendo el diff y los
controles requeridos están verdes, uso Merge pull request. Después actualizo
mi main antes de crear la siguiente rama.

Los checks revisan el tamaño del PR, el formato de los commits, las pruebas,
la cobertura, el build de Docker y una petición HTTP a /salud dentro del
contenedor. Si algo falla, abro los detalles y leo el mensaje concreto. Por
ejemplo, tamano-pr informa el total de líneas que superó el límite.

## 11. Qué comprueba aula_cli

El CLI es el programa de línea de comandos del laboratorio. Se ejecuta desde
la raíz del proyecto. En este equipo usamos el Python del entorno virtual:

    .\.venv\Scripts\python.exe -m aula_cli estado
    .\.venv\Scripts\python.exe -m aula_cli guia S1
    .\.venv\Scripts\python.exe -m aula_cli check S1 --prediccion pasa
    .\.venv\Scripts\python.exe -m aula_cli cerrar S1

estado enseña qué estación está activa. guia muestra la guía. check ejecuta
el verificador. Antes puedo declarar si creo que pasará: pasa o falla. Esa
predicción no cambia el resultado técnico; sirve para registrar si calibré
bien mi evaluación.

El verificador local de S1 comprueba seis cosas: suite verde, máquina de
estados, Dockerfile multi-stage, referencia a un build de imagen en CI, al
menos 15 tests y una fecha en la bitácora. No comprueba que CI ya haya corrido,
que GHCR tenga una imagen publicada, que la cobertura supere el umbral ni que
cada entrada de la bitácora tenga una duración. Esos puntos se verifican por
separado porque forman parte del entregable.

check actualiza .aula/progreso.json: incrementa los intentos, registra el
resultado y, si usé --prediccion, guarda si acerté. cerrar S1 marca el
progreso local como sellado si los criterios automáticos están verdes. Como
ese archivo está versionado, el cierre se envía en un PR propio; no se mezcla
con los PR de funcionalidad o documentación.

El cierre del CLI no comprueba por sí mismo GitHub Actions, la publicación de
GHCR ni la revisión del mentor. Esos pasos se comprueban aparte.

## 12. Lo que observamos al hacer S1

- La instalación inicial pidió Visual C++ porque PyYAML 6.0.2 intentaba
  compilarse con Python 3.14. El equipo no tenía permisos de administrador.
  Se usó el entorno virtual y una versión de PyYAML con paquete precompilado;
  también se añadió httpx para las pruebas de FastAPI.
- Al principio pytest no estaba instalado en el Python general. Ejecutar el
  Python de .venv evitó mezclar las dependencias del sistema y las del proyecto.
- Las primeras 21 pruebas fallaron con NotImplementedError porque quedaban
  funciones del motor sin implementar. Después hubo un fallo de límite de
  créditos: el escenario no excedía el límite configurado. Se corrigió el
  escenario para que comprobara realmente ese rechazo.
- La prueba del límite también llegó a parecer que no cambiaba. La revisión
  descubrió que había dos funciones con el mismo nombre; Python usa la última
  definición del archivo, así que se quitó la duplicada.
- Una ejecución posterior informó 30 pruebas correctas y 92 % de cobertura de
  src/aula/dominio. Es el último resultado local compartido en esta guía.
- Al ejecutar docker build, PowerShell dijo que docker no se reconocía.
  Get-Command podman tampoco encontró Podman. No instalé herramientas en el
  ordenador de empresa: GitHub Actions hace el build en un runner con Docker.
- Arranqué la API con Uvicorn y PYTHONPATH apuntando a src. /salud devolvió
  200. Las peticiones a / y /favicon.ico dieron 404 porque esas rutas no
  existen; eso no significaba que el servidor estuviera caído.
- El control tamano-pr detuvo PRs grandes. La salida mostró 410 líneas para
  el cambio del motor y 512 para el documento completo. La solución fue
  separar cambios coherentes en más de un PR, sin quitar el control.

## 13. Estado del ejercicio en la última revisión local

La copia revisada el 15 de octubre de 2026 muestra que los cambios del motor,
la API y el pipeline, la guía y la bitácora, y las dos partes de esta
explicación están integrados en main. Los títulos y nombres de rama identifican
cada entrega; los números de PR que muestra GitHub pueden cambiar según el
historial del repositorio.

También existe el commit chore(s1): registrar cierre de la estacion en la
rama chore/s1-cierre. El archivo .aula/progreso.json de ese commit marca S1
como sellada el 15 de octubre de 2026. La rama se había enviado a GitHub, pero
ese commit todavía no aparecía integrado en main en el historial local
revisado. Comprueba su PR y fusiónalo con los controles verdes.

La última salida de pruebas comunicada fue de 30 pruebas correctas y 92 % de
cobertura de dominio. La API también arrancó localmente y /salud respondió
200. Son evidencias locales obtenidas durante el trabajo; hay que comprobar
en GitHub el resultado actual de Actions y la publicación de la imagen.

## 14. Qué queda por confirmar o completar

- [x] Motor, estados, API y pipeline integrados en main.
- [x] Guía, bitácora y las dos partes de la explicación integradas en main.
- [x] El CLI registró localmente S1 como sellada en el commit de cierre.
- [ ] Confirmar y fusionar el PR de chore/s1-cierre; en la revisión local ese
  commit aún no está en main.
- [ ] Revisar en GitHub Actions que la ejecución más reciente termine bien,
  incluidos tests, cobertura, build y prueba de /salud.
- [ ] Confirmar que el job publicar terminó correctamente y que la imagen
  aparece en Packages de GitHub Container Registry.
- [ ] Decidir si se restauran las dos pruebas de orden de prioridad que se
  apartaron al reducir el PR del motor. No aparecen en
  tests/test_reglas_matricula.py en la rama principal revisada. El motor sí
  tiene la implementación de prioridad, pero esos casos ya no tienen una
  prueba explícita; se pueden volver a añadir en un PR pequeño.
- [ ] Comparar el resultado con la referencia del mentor y guardar sus
  observaciones.

El estado sellada del CLI registra el progreso local. No reemplaza la
integración del commit de cierre, la publicación en GHCR ni la validación
externa del entregable.
