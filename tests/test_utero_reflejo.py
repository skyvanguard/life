"""Tests de §37: reflejo (ganancia heredable g sobre la historia de energia propia)."""

import math

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import MUL, SPAWN, K

FLAGS = dict(germinal=True, toroidal=True, memoria=True, invasion="asentada", energia=True, luz_finita=3.0,
             parametros=0.05, escala=True)


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


def test_reflejo_off_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, **FLAGS)
    b = UteroCreciente(n0=16, seed=13, reflejo=0.0, **FLAGS)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_gain_shifts_expression_by_energy_drop():
    # la expresion se calcula ANTES de la actualizacion de energia del tick (tras la sonda)
    u = UteroCreciente(n0=1, seed=0, max_n=1, toroidal=True, energia=True, luz_finita=0.0, e0=2.0, e_mant=0.5,
                       e_gan=0.0, parametros=0.05, escala=True, reflejo=0.1)
    u.code[0] = prog((MUL, 1, 1, 3))            # salida cruda v*v
    u.v[0] = 0.5
    u.theta[0] = 0.0
    u.esc[0] = 1.0
    u.g[0] = 1.0
    u.e_lenta[0] = 2.0
    u.step()                                    # e == e_lenta al expresar: sin desplazamiento; luego e -> 1.5
    assert abs(float(u.v[0]) - 0.25) < 1e-9
    assert abs(float(u.e[0]) - 1.5) < 1e-9
    e_lenta = 2.0 + (1.5 - 2.0) / 200.0
    assert abs(float(u.e_lenta[0]) - e_lenta) < 1e-9
    u.step()                                    # ahora e_lenta > e: la expresion se desplaza g*tanh((e_lenta-e)/e0)
    esperado = (1.0 * math.tanh((e_lenta - 1.5) / 2.0) + 0.25 * 0.25) % 1.0
    assert abs(float(u.v[0]) - esperado) < 1e-9


def test_child_gain_is_a_small_perturbation_and_fixed_copies():
    for fijo in (False, True):
        u = UteroCreciente(n0=3, seed=1, max_n=3, toroidal=True, energia=True, luz_finita=3.0, parametros=0.05,
                           escala=True, reflejo=0.1, theta_fijo=fijo)
        u.alive[:] = False
        u.alive[1] = True
        u.code[1] = prog((MUL, 1, 1, 3), (SPAWN, 1, 0, 0))
        u.v[1] = 0.6
        u.g[1] = 0.3
        u.e[1] = 5.0
        u.step()
        assert u.alive[2]
        d = abs(float(u.g[2]) - 0.3)
        assert d == 0.0 if fijo else d <= 0.1 + 1e-12


def test_edge_growth_keeps_gain_aligned():
    u = UteroCreciente(n0=8, seed=3, max_n=64, reflejo=0.05, **FLAGS)
    for _ in range(300):
        u.step()
    assert u.g.shape == u.e_lenta.shape == u.alive.shape
