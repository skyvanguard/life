"""Tests de v10: percepcion del propio estado (la energia como 5o registro de solo lectura)."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import ADD, MUL, K, execute


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


def test_execute_without_extra_is_unchanged_and_with_extra_reads_it():
    code = prog((ADD, 4, 4, 3))            # 4%4=0 -> R3 = 2*vl ; con extra: 4%5=4 -> R3 = 2*e
    a = execute(code, 0.3, 0.1, 0.2, (None, code, None), wrap=True)
    assert abs(a[0] - 0.6) < 1e-12
    b = execute(code, 0.3, 0.1, 0.2, (None, code, None), wrap=True, extra=0.45)
    assert abs(b[0] - 0.9) < 1e-12


def test_percepcion_off_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, energia=True,
                       e_mant=0.005)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, energia=True,
                       e_mant=0.005, percepcion=False)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_a_cell_can_condition_its_matter_on_its_own_energy():
    u = UteroCreciente(n0=1, seed=0, max_n=1, toroidal=True, energia=True, e0=0.8, e_mant=0.0,
                       e_gan=0.0, percepcion=True)
    u.code[0] = prog((MUL, 4, 1, 3), (ADD, 3, 1, 3))    # R3 = e*v + v : sensible a la materia y a e
    u.v[0] = 0.5
    u.step()
    assert abs(u.v[0] - ((0.8 * 0.5 + 0.5) % 1.0)) < 1e-12


def test_percepcion_changes_dynamics_on_a_real_world():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, energia=True,
                       e_mant=0.005)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, energia=True,
                       e_mant=0.005, percepcion=True)
    for _ in range(200):
        a.step()
        b.step()
    assert not (a.n == b.n and np.array_equal(a.code, b.code))
