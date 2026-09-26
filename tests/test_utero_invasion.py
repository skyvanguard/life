"""Tests de v6: invasión de tejido asentado (SPAWN sobre una celda viva quieta)."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import MUL, SPAWN, K


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


SETTLED = prog((MUL, 1, 1, 3))                 # v' = v*v ; con v=0 queda quieta y NO es ciega
SPAWNER = prog((MUL, 1, 1, 3), (SPAWN, 1, 0, 0))   # igual, y pare hacia la derecha


def mundo(invasion, eq_window=5):
    u = UteroCreciente(n0=3, seed=0, max_n=3, toroidal=True, eq_window=eq_window,
                       invasion=invasion)
    u.code[0] = SPAWNER
    u.code[1] = SETTLED
    u.code[2] = SETTLED
    u.v[:] = 0.0
    u.mem[:] = 0.0
    return u


def test_invasion_off_never_overwrites_a_living_cell():
    u = mundo(None)
    for _ in range(30):
        m = u.step()
        assert m["invaded"] == 0
    np.testing.assert_array_equal(u.code[1], SETTLED)


def test_asentada_overwrites_only_after_the_stillness_window():
    u = mundo("asentada", eq_window=5)
    for _ in range(4):                      # todavía no cumplió la ventana
        assert u.step()["invaded"] == 0
    np.testing.assert_array_equal(u.code[1], SETTLED)
    invaded = 0
    for _ in range(10):
        invaded += u.step()["invaded"]
    assert invaded >= 1
    np.testing.assert_array_equal(u.code[1], SPAWNER)   # la cría de la madre (copia exacta)
    assert u.alive.all()                                 # reemplazo, no muerte


def test_siempre_overwrites_immediately():
    u = mundo("siempre")
    m = u.step()
    assert m["invaded"] >= 1
    np.testing.assert_array_equal(u.code[1], SPAWNER)


def test_invasion_is_logged_as_a_spawn_for_lineage():
    u = mundo("asentada", eq_window=2)
    u.log_events = True
    seen = []
    for _ in range(8):
        u.step()
        seen += u.spawns
    assert (0, 1) in seen                    # (coord_madre, coord_invadida)


def test_stillness_counter_does_not_kill_without_muerte_equilibrio():
    u = mundo("asentada", eq_window=2)
    for _ in range(20):
        u.step()
    assert u.alive.all()


def test_default_is_byte_identical_to_v5():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True,
                       invasion=None)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_asentada_changes_dynamics_on_a_real_world():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True,
                       invasion="asentada")
    inv = 0
    for _ in range(1500):
        a.step()
        inv += b.step()["invaded"]
    assert inv > 0
