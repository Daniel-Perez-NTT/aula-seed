# Desviaciones respecto al legado

La referencia para estas comparaciones es la calculadora original, capturada
antes de la refactorización en `tests/fixtures/legado_corpus_referencia.json`.
Las siguientes diferencias son cambios deliberados en la regla de cálculo.

## D-01: Los créditos convalidados cuentan en el divisor

- **Categoría:** cálculo de la media.
- **Comportamiento original:** asignaba a una convalidación una nota fija de
  5.0 y sumaba `5.0 × créditos` al numerador, pero no sumaba esos créditos al
  denominador. Si una asignatura convalidada era la única del expediente, la
  media resultaba `0.0`; mezclada con otras asignaturas, podía superar 10.
- **Comportamiento nuevo:** la nota fija y los créditos de la convalidación
  cuentan tanto en el numerador como en el denominador.
- **Ejemplo:** una asignatura convalidada de 6 créditos y otra con nota 8 de
  9 créditos dan `(5 × 6 + 8 × 9) / (6 + 9) = 6.80`.
- **Causa:** una media ponderada debe dividir por los créditos de todas las
  asignaturas que aportan nota.
- **Efecto aguas abajo:** cambia la media usada para ordenar expedientes en
  procesos como la asignación de becas; además, evita resultados superiores a
  10 por excluir del divisor los créditos convalidados.

## D-02: El redondeo se aplica al resultado final

- **Categoría:** precisión numérica.
- **Comportamiento original:** redondeaba cada nota a dos decimales antes de
  ponderarla y acumularla.
- **Comportamiento nuevo:** conserva las notas disponibles durante el cálculo
  y redondea la media ponderada una sola vez, al final, a dos decimales.
- **Ejemplo:** con notas `1.0` y `1.007`, de igual número de créditos, el
  redondeo por asignatura puede dar `1.01`; calcular primero la media original
  y redondear al final da `1.00`.
- **Causa:** evitar que los redondeos intermedios alteren el resultado
  acumulado.
- **Efecto aguas abajo:** una diferencia de centésimas puede cambiar la
  posición relativa de expedientes con medias próximas en una ordenación de
  becas.
