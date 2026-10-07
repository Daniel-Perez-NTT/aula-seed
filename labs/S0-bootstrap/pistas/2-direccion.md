# Pista 2 de S0

El gate de tamano de PR es un job mas del workflow: calcula las lineas del diff con `git diff --numstat origin/main...HEAD` y falla si superan el umbral. No hace falta ninguna accion de terceros.
