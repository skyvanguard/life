"""Tests de v9: metabolismo mínimo (persistir cuesta; el desequilibrio con el mundo alimenta)."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import ADD, CONST, MUL, SPAWN, K


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


def test_energia_off_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, energia=False,
                       e_mant=0.5)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_a_cell_in_equilibrium_with_a_cold_void_starves():
    # sola, materia 0 = vacío frío: no hay gradiente, no cosecha; paga e_mant y muere en e0/e_mant
    u = UteroCreciente(n0=1, seed=0, max_n=1, toroidal=True, energia=True, e0=1.0, e_mant=0.1)
    u.code[0] = prog((MUL, 1, 1, 3))        # R3 = v*v -> 0 con v=0 (sensible a la materia)
    u.v[0] = 0.0
    vivos = [bool(u.step() and u.alive[0]) for _ in range(12)]
    assert vivos[:9] == [True] * 9 and not vivos[-1]


def test_a_cell_far_from_the_void_harvests_and_lives():
    u = UteroCreciente(n0=1, seed=0, max_n=1, toroidal=True, energia=True, e0=1.0, e_mant=0.1,
                       e_gan=0.5)
    u.code[0] = prog((CONST, 10, 0, 3), (ADD, 3, 1, 3))    # R3 = 0.5 + v : lejos del 0 del vacío
    u.v[0] = 0.0
    e_prev = u.e[0]
    for _ in range(50):
        u.step()
    assert u.alive[0] and u.e[0] > e_prev                  # cosecha > mantenimiento


def test_child_receives_a_share_of_the_mothers_energy():
    u = UteroCreciente(n0=3, seed=0, max_n=3, toroidal=True, energia=True, e0=1.0, e_mant=0.0,
                       e_gan=0.0, e_dif=0.0, e_parto=0.5)
    u.alive[:] = False
    u.alive[1] = True
    u.code[1] = prog((MUL, 1, 1, 3), (SPAWN, 1, 0, 0))     # pare hacia la derecha
    u.v[1] = 0.3
    u.step()
    assert u.alive[2] and abs(u.e[2] - 0.5) < 1e-12 and abs(u.e[1] - 0.5) < 1e-12


def test_diffusion_is_conservative():
    u = UteroCreciente(n0=8, seed=1, max_n=8, toroidal=True, energia=True, e0=1.0, e_mant=0.0,
                       e_gan=0.0, e_dif=0.3)
    for i in range(8):
        u.code[i] = prog((MUL, 1, 1, 3))                   # sin partos, sensible
        u.v[i] = 0.3
    u.e[:] = np.linspace(0.2, 1.8, 8)
    total = u.e.sum()
    for _ in range(20):
        u.step()
    assert u.alive.all()
    assert abs(u.e[u.alive].sum() - total) < 1e-9
    assert u.e.std() < 0.45                                 # se va homogeneizando (inicial 0.52)


def test_energia_luz_off_is_byte_identical_and_on_feeds_the_interior():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, energia=True,
                       e_mant=0.005)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, energia=True,
                       e_mant=0.005, energia_luz=False)
    for _ in range(200):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.e, b.e)
    # tres celdas: la del medio es interior; sin luz no come (solo paga); con luz come
    def mundo(luz):
        u = UteroCreciente(n0=3, seed=0, max_n=3, toroidal=True, energia=True, e0=1.0,
                           e_mant=0.01, e_gan=0.5, e_dif=0.0, energia_luz=luz)
        for i in range(3):
            u.code[i] = prog((CONST, 10, 0, 3), (ADD, 3, 1, 3))    # R3 = 0.5 + v : lejos del 0
            u.v[i] = 0.0
        return u
    sin, con = mundo(False), mundo(True)
    sin.step()
    con.step()
    assert sin.e[1] < 1.0 < con.e[1]
