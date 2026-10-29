# Comparativa Claude Code y OpenCode

## Alcance

Esta comparación describe la configuración y el flujo disponibles en el repositorio.
No afirma resultados de ejecución con Claude Code: en este ejercicio no disponemos
de una cuenta que permita realizar esa prueba.

## Criterios

| Criterio | Claude Code | OpenCode |
|---|---|---|
| Instrucciones del proyecto | `CLAUDE.md` | Configuración e instrucciones propias del proyecto |
| Agentes especializados | `.claude/agents/` | Agentes configurables, incluidos subagentes |
| Permisos y hooks | `.claude/settings.json` permite declarar permisos y hooks | Tiene su propia configuración de agentes y permisos |
| Ejecución en este ejercicio | No verificada: no tenemos acceso a una cuenta de pago | Pendiente de ejecutar y registrar |
| Coste para este ejercicio | No podemos asumirlo con la cuenta disponible | Depende del proveedor y modelo que se conecten |

## Elección razonada

Para completar este ejercicio con la cuenta disponible, OpenCode sería el candidato
a probar primero si podemos conectarlo a un proveedor y modelo accesibles. Su
configuración de agentes y permisos es propia, así que no se debe asumir que los
archivos de Claude Code se aplican automáticamente.

Claude Code encaja directamente con `CLAUDE.md`, `.claude/settings.json` y los
subagentes definidos para esta estación, pero no podemos validar su comportamiento
práctico sin acceso al servicio.

## Resultado

No se ha realizado una comparación experimental ejecutando el mismo encargo en
ambos motores. La tabla compara capacidades y limitaciones conocidas; queda
pendiente completar la prueba práctica si se obtiene acceso.