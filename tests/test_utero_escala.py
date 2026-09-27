"""Tests de v17b: escala heredable s (materia visible = (theta + s*salida) mod 1)."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import MUL, SPAWN, K

FLAGS = dict(germinal=True, toroidal=True, memoria=True, invasion="asentada")


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


def test_escala_off_is_byte_identical_with_theta_on():
    a = UteroCreciente(n0=16, seed=13, parametros=0.05, **FLAGS)
    b = UteroCreciente(n0=16, seed=13, parametros=0.05, escala=False, **FLAGS)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_scale_attenuates_matter_and_child_scale_is_a_small_perturbation():
    eps = 0.05
    u = UteroCreciente(n0=3, seed=1, max_n=3, toroidal=True, parametros=eps, escala=True)
    u.alive[:] = False
    u.alive[1] = True
    u.code[1] = prog((MUL, 1, 1, 3), (SPAWN, 1, 0, 0))     # salida cruda = v*v
    u.v[1] = 0.6
    u.esc[1] = 0.5
    th = float(u.theta[1])
    u.step()
    assert abs(u.v[1] - ((th + 0.5 * 0.36) % 1.0)) < 1e-12
    assert u.alive[2]
    assert abs(float(u.esc[2]) - 0.5) <= eps + 1e-12
    assert 0.0 <= float(u.esc[2]) <= 1.0


def test_theta_fijo_freezes_scale_too():
    u = UteroCreciente(n0=3, seed=1, max_n=3, toroidal=True, parametros=0.05, escala=True, theta_fijo=True)
    u.alive[:] = False
    u.alive[1] = True
    u.code[1] = prog((MUL, 1, 1, 3), (SPAWN, 1, 0, 0))
    u.v[1] = 0.6
    u.esc[1] = 0.7
    u.step()
    assert u.alive[2] and float(u.esc[2]) == 0.7


def test_edge_growth_keeps_scale_aligned():
    u = UteroCreciente(n0=8, seed=3, max_n=64, parametros=0.05, escala=True, **FLAGS)
    for _ in range(300):
        u.step()
    assert u.esc.shape == u.theta.shape == u.alive.shape
