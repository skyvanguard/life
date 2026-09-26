"""Tests de la corrida medida (vara honesta completa en una función)."""

import numpy as np

from zeta_life.utero.creciente import run_history
from zeta_life.utero.medidas import correr_medido, media_ventana, por_tramo

FLAGS = dict(memoria=True)


def test_shapes_and_raw_matches_run_history():
    ticks = 400
    r = correr_medido(seed=3, flags=FLAGS, ticks=ticks, tranche=100, t_filtro=50, max_n=64)
    h = run_history(seed=3, ticks=ticks, germinal=True, toroidal=True, memoria=True, max_n=64)
    np.testing.assert_array_equal(r["raw"], np.array(h["new_genomes"]))
    assert r["filt"].shape == (4,) and r["eco"].shape == (4,) and r["share"].shape == (4,)
    assert r["causa"].shape == (4, 2) and r["causa"].sum() == r["raw"].sum()
    assert (r["share"] >= 0).all() and (r["share"] <= 1).all()


def test_filtered_never_exceeds_raw_per_tranche():
    r = correr_medido(seed=13, flags=FLAGS, ticks=600, tranche=100, t_filtro=100, max_n=64)
    assert (r["filt"] <= por_tramo(r["raw"], 100)).all()


def test_shadow_run_uses_the_death_schedule():
    real = correr_medido(seed=5, flags=FLAGS, ticks=300, tranche=100, t_filtro=50, max_n=64)
    sh = correr_medido(seed=5, flags=FLAGS, ticks=300, tranche=100, t_filtro=50, max_n=64,
                       shadow=list(real["deaths"]))
    # la sombra mata a lo sumo lo programado (menos si no quedan celdas)
    assert (sh["deaths"] <= real["deaths"]).all()


def test_invasion_flag_is_counted():
    r = correr_medido(seed=13, flags=dict(memoria=True, invasion="siempre"), ticks=300,
                      tranche=100, t_filtro=50, max_n=64)
    assert r["invaded"].sum() > 0


def test_media_ventana():
    xt = np.array([0, 10, 20, 30, 40])
    assert media_ventana(xt, (1000, 2500), tranche=500) == 30.0
