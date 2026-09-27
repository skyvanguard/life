"""Tests de §21/§22: orden_seed (RNG aparte para el orden) y tasa_germinal (escritura germinal rara)."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente

FLAGS = dict(germinal=True, toroidal=True, memoria=True, invasion="asentada")


def test_orden_seed_none_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, **FLAGS)
    b = UteroCreciente(n0=16, seed=13, orden_seed=None, **FLAGS)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)


def test_orden_seed_keeps_the_soup_and_changes_the_trajectory():
    a = UteroCreciente(n0=16, seed=13, **FLAGS)
    b = UteroCreciente(n0=16, seed=13, orden_seed=99, **FLAGS)
    np.testing.assert_array_equal(a.code, b.code)          # misma sopa
    np.testing.assert_array_equal(a.v, b.v)
    for _ in range(300):
        a.step()
        b.step()
    assert not (a.code.shape == b.code.shape and np.array_equal(a.code, b.code) and np.array_equal(a.v, b.v))


def test_tasa_germinal_one_is_byte_identical_and_zero_never_writes():
    a = UteroCreciente(n0=16, seed=13, escritura_total=True, **FLAGS)
    b = UteroCreciente(n0=16, seed=13, escritura_total=True, tasa_germinal=1.0, **FLAGS)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    # con tasa 0 y congelado NO, las crias son copias exactas del codigo nuevo de la madre:
    # el conjunto de trios de operandos no puede crecer (solo MUTO total podria; se apaga con congelado)
    c = UteroCreciente(n0=16, seed=13, escritura_total=True, tasa_germinal=0.0, congelado=True, **FLAGS)
    inicial = {c.code[i].tobytes() for i in range(c.n)}
    for _ in range(1000):
        c.step()
    assert {c.code[i].tobytes() for i in np.flatnonzero(c.alive)} <= inicial


def test_tasa_germinal_low_writes_less_often_than_one():
    def escrituras(p):
        u = UteroCreciente(n0=16, seed=5, escritura_total=True, tasa_germinal=p, **FLAGS)
        for _ in range(1500):
            u.step()
        return len(u.seen)
    assert escrituras(0.05) < escrituras(1.0)
