"""Tests del protocolo de ablación (extraído de v5 para replicarlo en N semillas)."""

import os

import numpy as np
import pytest

from zeta_life.utero.ablacion import correr, medir_cola
from zeta_life.utero.creciente import run_history

FAST = dict(n0=16, max_n=64, germinal=True, toroidal=True)


def test_medir_cola_windows_are_the_v5_ones():
    # pre = media/500 en los 1000 previos ; pulso = suma de los 500 siguientes ;
    # cola = media/500 en +1000..+3000 (ignora el pulso de recolonización)
    npt = np.zeros(6000, dtype=int)
    npt[1000:2000] = 2          # pre: 2000 en 1000 ticks -> 1000 por tramo
    npt[2000:2500] = 5          # pulso: 2500
    npt[3000:5000] = 1          # cola: 2000 en 2000 ticks -> 500 por tramo
    pre, pulse, tail = medir_cola(npt, 2000)
    assert pre == 1000
    assert pulse == 2500
    assert tail == 500


def test_sin_ablacion_reproduce_la_novedad_de_run_history():
    # El registro externo de genomas debe coincidir con el contador interno
    # de step() (ambos cuentan genomas nunca vistos, tras cada tick).
    ticks = 300
    res = correr(seed=3, memoria=True, ticks=ticks, ablate_at=None, **FAST)
    h = run_history(seed=3, ticks=ticks, memoria=True, **FAST)
    np.testing.assert_array_equal(res["novedad"], np.array(h["new_genomes"]))
    assert len(res["vivas"]) == ticks


def test_ablacion_mata_la_zona_activa():
    ticks, t_abl = 200, 100
    base = correr(seed=13, memoria=True, ticks=ticks, ablate_at=None, **FAST)
    abl = correr(seed=13, memoria=True, ticks=ticks, ablate_at=t_abl, **FAST)
    # idénticos hasta la ablación (el protocolo no toca nada antes)
    np.testing.assert_array_equal(base["novedad"][:t_abl + 1],
                                  abl["novedad"][:t_abl + 1])
    # justo después de ablar hay menos celdas vivas que sin ablar
    assert abl["ablated"] > 0
    assert abl["vivas"][t_abl + 1] < base["vivas"][t_abl + 1]


def test_ablacion_es_determinista():
    a = correr(seed=5, memoria=False, ticks=150, ablate_at=80, **FAST)
    b = correr(seed=5, memoria=False, ticks=150, ablate_at=80, **FAST)
    np.testing.assert_array_equal(a["novedad"], b["novedad"])
    assert a["ablated"] == b["ablated"]


@pytest.mark.skipif(not os.environ.get("UTERO_SLOW"),
                    reason="~60 s; set UTERO_SLOW=1 para la regresión contra v5")
def test_regresion_v5_seed13_memoria_on_t8000():
    # Números publicados en results/utero_memoria_run.txt (v5, 2026-07-09)
    res = correr(seed=13, memoria=True, ticks=12000, ablate_at=8000,
                 n0=16, max_n=256, germinal=True, toroidal=True)
    pre, pulse, tail = medir_cola(res["novedad"], 8000)
    assert (round(pre), pulse, round(tail)) == (543, 3525, 950)
