"""Tests de v15: tierra quemada (el lugar de una celda muerta queda incolonizable T ticks)."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import MUL, SPAWN, K


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


def test_refractario_off_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, invasion="asentada")
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, invasion="asentada",
                       refractario=0)
    for _ in range(400):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)
    np.testing.assert_array_equal(a.alive, b.alive)


def test_burned_slot_blocks_colonization_until_T_then_allows_it():
    T = 50
    u = UteroCreciente(n0=3, seed=0, max_n=3, toroidal=True, refractario=T)
    u.alive[:] = False
    u.alive[1] = True
    u.code[1] = prog((MUL, 1, 1, 3), (SPAWN, 1, 0, 0))       # R3 = v*v (sensible); pare a la derecha
    u.v[1] = 0.5
    u.step()
    assert u.alive[2]                                        # colonizó el vacío no quemado
    u.vaciar(2)                                              # muere: el lugar queda quemado
    assert not u.alive[2]
    t0 = u._tick
    for _ in range(T - 2):
        u.step()
        assert not u.alive[2], "colonizó tierra quemada"
    for _ in range(4):
        u.step()
    assert u.alive[2], "el lugar no se liberó al vencer el refractario"
    assert u.quemada[2] <= u._tick or u.alive[2]
    assert u._tick > t0


def test_edge_growth_keeps_arrays_consistent():
    u = UteroCreciente(n0=8, seed=3, max_n=64, germinal=True, toroidal=True, refractario=100)
    for _ in range(300):
        u.step()
    assert u.quemada.shape == u.alive.shape == u.v.shape
