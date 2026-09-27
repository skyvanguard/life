"""Tests de §36: perillas escribibles (theta_eff = theta + S1, s_eff = s + S2 via registros lentos)."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import CONST, MUL, K

FLAGS = dict(germinal=True, toroidal=True, memoria=True, invasion="asentada", parametros=0.05, escala=True,
             lentos=0.02)


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


def test_perillas_off_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, **FLAGS)
    b = UteroCreciente(n0=16, seed=13, perillas=False, **FLAGS)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_slow_register_shifts_the_expression():
    # registros: r0 vl, r1 v, r2 vr, r3 R3, r4 S1, r5 S2. R3 = v*v ; S1 <- 0.5 (empuje lento)
    u = UteroCreciente(n0=1, seed=0, max_n=1, toroidal=True, parametros=0.05, escala=True, lentos=0.5,
                       perillas=True)
    u.code[0] = prog((MUL, 1, 1, 3), (CONST, 10, 0, 4))
    u.v[0] = 0.5
    u.theta[0] = 0.0
    u.esc[0] = 1.0
    u.step()                                   # S1 pasa de 0 a 0.25 (lambda 0.5 hacia 0.5)
    assert abs(u.S[0, 0] - 0.25) < 1e-12
    v_prev = float(u.v[0])
    u.step()                                   # S1 -> 0.375 (escrito antes de expresar); theta_eff = 0.375
    assert abs(u.S[0, 0] - 0.375) < 1e-12
    esperado = (0.375 + v_prev * v_prev) % 1.0
    assert abs(float(u.v[0]) - esperado) < 1e-9
