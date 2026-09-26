"""Tests del sol (entorno con estructura) y de su acople al borde del mundo."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import ADD, K
from zeta_life.utero.sol import Sol


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


def test_sol_is_deterministic_bounded_and_seasonal():
    a, b = Sol(seed=3, ticks=5000), Sol(seed=3, ticks=5000)
    np.testing.assert_array_equal(a.serie, b.serie)
    assert (a.serie >= 0).all() and (a.serie < 1).all()
    names = [n for n, _, _ in a.estaciones]
    assert names[:6] == ["A", "B", "C", "A", "B", "C"]      # orden fijo y cíclico
    durs = [f - i for _, i, f in a.estaciones[:-1]]
    assert min(durs) >= 300 and max(durs) <= 900 and len(set(durs)) > 3   # típicas pero variables
    assert a.estaciones[-1][2] == 5000
    assert Sol(seed=4, ticks=5000).estaciones != a.estaciones


def test_sol_regimen_and_long_seasons():
    s = Sol(seed=0, ticks=20000)
    n, i, f = s.estaciones[2]
    assert s.regimen(i) == n and s.regimen(f - 1) == n
    tip = s.duracion_tipica()
    for _, i, f in s.largas():
        assert f - i > 1.25 * tip


def test_void_is_cold_without_sun_and_sunny_with_it():
    sol = Sol(seed=1, ticks=100)
    u = UteroCreciente(n0=4, seed=0, max_n=4, toroidal=True, sol=sol)
    u.step()                                    # _tick pasa a 1: el vacío vale sol(0)
    u.alive[:] = True
    assert u._ctx(0)[1] == sol(0) and u._ctx(3)[2] == sol(0)     # más allá
    u.alive[1] = False
    assert u._ctx(0)[2] == sol(0) and u._ctx(2)[1] == sol(0)     # vacío interior: también iluminado
    u0 = UteroCreciente(n0=4, seed=0, max_n=4, toroidal=True)
    u0.step()
    assert u0._ctx(0)[1] == 0.0 and u0._ctx(3)[2] == 0.0


def test_edge_cell_feels_the_sun_in_its_matter():
    # celda de borde izquierdo: R3 = vl + v  -> con sol su materia sigue al sol
    sol = Sol(seed=2, ticks=50)
    u = UteroCreciente(n0=3, seed=0, max_n=3, toroidal=True, sol=sol)
    for i in range(3):
        u.code[i] = prog((ADD, 0, 1, 3))
    u.v[:] = 0.0
    u.step()
    assert abs(u.v[0] - (sol(0) % 1.0)) < 1e-12 or abs(u.v[2] - (sol(0) % 1.0)) < 1e-12


def test_sol_none_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, sol=None)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_sun_changes_the_dynamics():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True,
                       sol=Sol(seed=0, ticks=2000))
    for _ in range(600):
        a.step()
        b.step()
    assert not (a.n == b.n and np.array_equal(a.v, b.v))


# ------------------------------------------------ el clima cuenta (sol_sonda)
def test_sol_sonda_off_or_without_sun_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, sol_sonda=True)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_sol_sonda_kills_a_physics_blind_to_the_current_climate():
    from zeta_life.utero.nivel2 import CONST, MUL, THR
    # R3 = 0.5·THR(vl > 0.75): sensible sólo cuando el mundo está alto. (El ×0.5
    # evita que el 1.0 de THR se envuelva en 0 en el toro: 0 y 1 son el mismo punto.)
    code = prog((CONST, 11, 0, 2), (THR, 0, 2, 3), (CONST, 10, 0, 1), (MUL, 3, 1, 3))
    sol_bajo = lambda t: 0.15      # noqa: E731  clima bajo: 0.15 y 0.768 -> ambos < 0.75? 0.768 > 0.75
    sol_alto = lambda t: 0.30      # noqa: E731  clima: 0.30 y 0.918 -> 0 y 1: distingue
    # con la sonda fija (0 y 0.618): ambos < 0.75 -> ciega -> muere
    u = UteroCreciente(n0=1, seed=0, max_n=1, toroidal=True, sol=sol_bajo)
    u.code[0] = code
    u.step()
    assert not u.alive[0]
    # con el clima en la sonda y sol=0.30: referencias 0.30 y 0.918 -> distingue -> vive
    u2 = UteroCreciente(n0=1, seed=0, max_n=1, toroidal=True, sol=sol_alto, sol_sonda=True)
    u2.code[0] = code
    u2.step()
    assert u2.alive[0]
    # y con el clima en 0.15: referencias 0.15 y 0.768 -> 0 y 1 -> también distingue
    u3 = UteroCreciente(n0=1, seed=0, max_n=1, toroidal=True, sol=lambda t: 0.90, sol_sonda=True)
    u3.code[0] = code
    u3.step()                       # referencias 0.90 y 0.518 -> 1 y 0 -> distingue
    assert u3.alive[0]
    # clima 0.05: referencias 0.05 y 0.668 -> ambos < 0.75 -> ciega en ESTA estación
    u4 = UteroCreciente(n0=1, seed=0, max_n=1, toroidal=True, sol=lambda t: 0.05, sol_sonda=True)
    u4.code[0] = code
    u4.step()
    assert not u4.alive[0]


def test_sol_sonda_changes_who_dies_across_seasons():
    sol = Sol(seed=0, ticks=3000)
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, sol=sol)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, sol=sol,
                       sol_sonda=True)
    da = db = 0
    for _ in range(1500):
        da += a.step()["deaths"]
        db += b.step()["deaths"]
    assert da != db


# ------------------------------------------------ el sol calienta (sol_acople)
def test_sol_acople_off_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, sol_acople=0.3)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_sol_acople_makes_the_surface_follow_the_sun():
    sol = Sol(seed=2, ticks=200)
    u = UteroCreciente(n0=3, seed=0, max_n=3, toroidal=True, sol=sol, sol_acople=1.0)
    for i in range(3):
        u.code[i] = prog((ADD, 1, 1, 3))          # R3 = 2v: no lee el vacío
    u.v[:] = 0.3
    u.step()
    assert abs(u.v[0] - sol(0)) < 1e-12 and abs(u.v[2] - sol(0)) < 1e-12   # superficie = sol
    assert abs(u.v[1] - 0.6) < 1e-12                                        # interior: su regla
