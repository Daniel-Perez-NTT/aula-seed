# Procedimiento de reversion de Aula Students

## Objetivo

Volver a la ultima version estable si una nueva version falla durante el
despliegue o despues de iniciarse. El despliegue oficial de S7 se ejecuta en
Render desde GitHub Actions; Podman se utiliza para las comprobaciones locales.

## Cuando iniciar la reversion

Se inicia si ocurre cualquiera de estas situaciones:

- `GET /salud` no devuelve HTTP 200.
- `POST /matriculas` devuelve un error inesperado.
- Los logs muestran errores repetidos.
- El healthcheck de GitHub Actions falla.
- La aplicacion arranca, pero una prueba funcional demuestra que la version es incorrecta.

## Reversion local con Podman

1. Identificar la etiqueta estable, por ejemplo `localhost/aula:1.0.0`.
2. Detener y eliminar el contenedor nuevo:

   ```powershell
   podman stop aula-app
   podman rm aula-app
   ```

3. Arrancar la imagen estable:

   ```powershell
   podman run --detach --name aula-app --publish 8000:8000 localhost/aula:1.0.0
   ```

4. Comprobar la recuperacion:

   ```powershell
   Invoke-RestMethod http://localhost:8000/salud
   python src/aula/observabilidad.py
   ```

## Reversion cloud en Render

Render conserva los despliegues anteriores del servicio. Para volver a una
version que ya funcionaba:

1. Entrar en [Render Dashboard](https://dashboard.render.com/).
2. Abrir el servicio `aula-seed`.
3. Pulsar la pestana **Deploys**.
4. Localizar el despliegue anterior que termino correctamente.
5. Abrir el menu de ese despliegue y pulsar **Rollback**.
6. Confirmar con **Rollback to this deploy**.
7. Esperar a que Render marque el nuevo despliegue como **Live**.
8. Comprobar desde Internet:

   ```powershell
   Invoke-RestMethod https://aula-seed.onrender.com/salud
   ```

9. Revisar en **Logs** que aparecen peticiones `GET /salud` y
   `POST /matriculas` con estado 200.

Este procedimiento no requiere crear recursos de pago. El rollback devuelve
el servicio a una imagen/commit que Render ya tiene registrado y no borra el
repositorio de GitHub.

## Como evitar que vuelva a fallar

Despues del rollback se corrige la causa en una rama, se ejecutan las pruebas
y se integra mediante un Pull Request. Al llegar a `main`, el workflow
`.github/workflows/ci.yml` vuelve a ejecutar tests, construye la imagen,
publica el artefacto y solicita el despliegue de Render mediante su Deploy
Hook. El job no termina correctamente si la URL publica no supera `/salud` y
`POST /matriculas`.
