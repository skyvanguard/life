"""Tests de v17: desplazamiento heredable theta (mapa local programa->materia)."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import CONST, MUL, SPAWN, K

FLAGS = dict(germinal=True, toroidal=True, memoria=True, invasion="asentada")


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


def test_parametros_off_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, **FLAGS)
    b = UteroCreciente(n0=16, seed=13, parametros=0.0, **FLAGS)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_theta_shifts_matter_but_not_the_probe():
    # programa constante (ciego): con theta sigue muriendo; programa sensible: su materia lleva theta
    u = UteroCreciente(n0=2, seed=0, max_n=2, toroidal=True, parametros=0.05)
    u.code[0] = prog((CONST, 10, 0, 3))            # R3 = 0.5 constante -> ciego
    u.code[1] = prog((MUL, 1, 1, 3))               # R3 = v*v -> sensible
    u.v[:] = [0.3, 0.5]
    th1 = float(u.theta[1])
    u.step()
    assert not u.alive[0]
    assert u.alive[1] and abs(u.v[1] - ((0.25 + th1) % 1.0)) < 1e-12


def test_child_theta_is_a_small_perturbation_and_theta_fijo_copies_exactly():
    eps = 0.05
    for congelado in (False, True):
        u = UteroCreciente(n0=3, seed=1, max_n=3, toroidal=True, parametros=eps, theta_fijo=congelado)
        u.alive[:] = False
        u.alive[1] = True
        u.code[1] = prog((MUL, 1, 1, 3), (SPAWN, 1, 0, 0))
        u.v[1] = 0.6
        th = float(u.theta[1])
        u.step()
        assert u.alive[2]
        d = abs(float(u.theta[2]) - th)
        d = min(d, 1.0 - d)
        if congelado:
            assert d == 0.0
        else:
            assert d <= eps + 1e-12


def test_edge_growth_keeps_theta_aligned():
    u = UteroCreciente(n0=8, seed=3, max_n=64, parametros=0.05, **FLAGS)
    for _ in range(300):
        u.step()
    assert u.theta.shape == u.alive.shape
