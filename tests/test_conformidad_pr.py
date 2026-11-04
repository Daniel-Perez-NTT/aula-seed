"""Pruebas del lector de metadatos de PR."""

import pytest

from herramientas.conformidad_pr import metadatos


@pytest.mark.parametrize("bom", ["", "\ufeff"])
def test_parsea_metadatos_de_cuerpo_con_o_sin_bom(bom):
    cuerpo = bom + (
        "AULA_SPEC_ID: SPEC-002\n"
        "AULA_CRITERIOS: CA-01, CA-02\n"
    )

    assert metadatos(cuerpo) == ("SPEC-002", ["CA-01", "CA-02"])
