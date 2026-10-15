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

Un Pull Request (PR) es una propuesta para integrar los commits de una rama en
otra, normalmente en `main`. GitHub muestra el diff, ejecuta CI y permite una
revisión antes de integrar el cambio.

El límite de 400 líneas cuenta líneas añadidas y eliminadas en todo el PR, no
por cada commit. Los cambios completos de S1 superan ese límite; por eso no se
deben subir como un único PR enorme. Hay que dividirlos en PRs pequeños y
coherentes, manteniendo la suite y los gates útiles en cada paso. No elimines
ni desactives el control de tamaño para sortearlo.

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

## 11. Qué comprueba `aula_cli`

El CLI es el programa de línea de comandos del laboratorio. Se ejecuta con
`python -m aula_cli` y lleva el progreso de las estaciones.

Comandos importantes:

```powershell
python -m aula_cli estado
python -m aula_cli guia S1
python -m aula_cli check S1 --prediccion pasa
python -m aula_cli cerrar S1
```

Antes del check se declara si crees que pasarás (`pasa` o `falla`). La
predicción no cambia el resultado técnico; sirve para registrar lo bien que
calibras tu propia evaluación.

El verificador local de S1 comprueba seis cosas: suite verde, máquina de
estados, Dockerfile multi-stage, referencia a un build de imagen en CI, al
menos 15 tests y una fecha en la bitácora. No comprueba que CI ya haya corrido,
que GHCR tenga una imagen publicada, que la cobertura supere el umbral ni que
cada entrada de la bitácora contenga una duración. Esos puntos deben verificarse
por separado porque forman parte del entregable de la estación.

`cerrar S1` sella el progreso local cuando los criterios automáticos están
verdes. No sustituye el Pull Request, la revisión del mentor ni la comparación
con la referencia que entrega el mentor.

## 12. Lo que hemos observado en este trabajo

- La instalación inicial pidió Visual C++ porque la versión fijada de PyYAML
  intentaba compilarse con Python 3.14. Un entorno virtual y una versión con
  rueda compatible resolvieron el bloqueo sin instalar herramientas de
  administrador.
- Varias pruebas fallaron al principio porque el motor todavía tenía
  `NotImplementedError`. Eso era esperable antes de implementar las reglas.
- Una prueba de créditos no fallaba porque los cursos seleccionados sumaban
  menos que el límite. Se ajustó para probar un límite menor de forma
  controlada.
- La prueba corregida parecía no tener efecto porque había dos funciones con
  el mismo nombre. Python usaba la definición que aparecía al final del
  archivo; se quitó la duplicada.
- Las pruebas y la cobertura local terminaron verdes, pero el portátil no
  tiene Docker ni Podman. El contenedor debe comprobarse en Actions.

## 13. Lista final para poder decir “S1 cerrado”

- [x] Las pruebas locales pasan (30 en la última salida compartida).
- [x] La cobertura de `src/aula/dominio` supera el 60 % (92 % en la salida
  compartida).
- [x] El servicio arranca localmente con Uvicorn y `/salud` devuelve 200.
- [x] Existe un Dockerfile multi-stage y un workflow con build y prueba del
  contenedor.
- [ ] La bitácora contiene tiempos por tarea; usa valores reales o indica cuáles
  son estimaciones.
- [ ] Los cambios se dividen en PRs de menos de 400 líneas y se revisan antes
  de integrarlos.
- [ ] Una ejecución de GitHub Actions pasa tests, build y comprobación del
  contenedor.
- [ ] Tras integrar en `main`, la imagen aparece publicada en GHCR y el job de
  publicación está verde.
- [ ] Se ejecuta `python -m aula_cli cerrar S1` y se compara el trabajo con la
  referencia del mentor.

El check local verde es una parte importante, pero no equivale por sí solo a
tener todos esos puntos completados.
