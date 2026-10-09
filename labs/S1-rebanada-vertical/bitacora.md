# Bitácora de S1

2026-10-09

45 minutos: 
He empezado S1 preparando el entorno. Al instalar las dependencias me atasqué con PyYAML: mi Python 3.14 intentaba compilarlo y pedía Visual C++. Lo resolví usando un entorno virtual y una versión de PyYAML compatible.

2 horas:
Después escribí las pruebas y completé el motor de matrícula y las transiciones de estado. Al principio varias pruebas fallaban porque todavía quedaban partes sin implementar, algo que me ayudó a ver qué faltaba. También me confundí al corregir la prueba del límite de créditos: había dejado la versión antigua debajo de la nueva y Python estaba usando esa. Cuando quité la duplicada, las pruebas pasaron.

2 horaa:
He comprobado que pasan 30 pruebas y que la cobertura del dominio es del 92 %. No pude construir la imagen en mi ordenador porque no tengo Docker ni Podman. Sí pude arrancar la API con Uvicorn y comprobar que `/salud` responde correctamente. La comprobación de la imagen queda pendiente de GitHub Actions.

No apunté los tiempos exactos mientras trabajaba; añadiré una estimación honesta por tarea.
pd: Esta es la segunda vez que hago el ejercicio ya que ne la primera pues teniamos los problemas de el tema de que no teniamos el archivo seed; Por eso los tiempos estan bastante reducidos al estar reutilizando tanto lógica como codigo de la anterior version. Por eso que si los tiempos estasen sumados la verdad que serían bastante mas elevados.