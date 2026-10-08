Configuré una protección para la rama main obligando a trabajar mediante Pull Requests.
Añadí CODEOWNERS para proteger labs/, manifiestos/ y .github/.
Creé una plantilla de Pull Request con checklist.
Configuré un pipeline de GitHub Actions con tests, validación de commits y control de tamaño de PR.
Problemas encontrados
Push directo bloqueado
Intenté hacer git push a main y GitHub lo rechazó con un error GH013. La protección de rama estaba funcionando correctamente.

Error en CODEOWNERS
El archivo se guardó como CODEOWNERS.txt, por lo que la validación fallaba. Lo renombré a CODEOWNERS.

Error en los tests
El pipeline fallaba porque no existía el directorio manifiestos/. Lo creé junto con un .gitkeep.

Error en Conventional Commits
Algunos commits no seguían el formato requerido.
