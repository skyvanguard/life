"""Tests del Útero PLANO (v8): el mismo sustrato en 2-D, misma interfaz."""

import numpy as np

from zeta_life.utero.ablacion import correr as correr_ablacion
from zeta_life.utero.medidas import correr_medido
from zeta_life.utero.nivel2 import ADD, CONST, MUL, SPAWN, K
from zeta_life.utero.plano import DIRS, UteroPlano, execute_plano


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


def fabrica(seed, shadow, **flags):
    return UteroPlano(h=12, w=12, seed=seed, bloque=4, log_events=True,
                      shadow_deaths=shadow, **flags)


# ------------------------------------------------------------ execute_plano
def test_registers_are_the_four_neighbours_self_and_potential():
    code = prog((MUL, 4, 4, 5))                  # R = v*v ; wrap
    out, own, spawn, raw = execute_plano(code, (0.1, 0.2, 0.3, 0.4), 0.5, (None,) * 5)
    assert abs(raw - 0.25) < 1e-12 and abs(out - 0.25) < 1e-12 and spawn is None
    code = prog((CONST, 12, 0, 5))               # R = 1.0 -> materia 0.0, raw 1.0
    out, _, _, raw = execute_plano(code, (0,) * 4, 0.0, (None,) * 5)
    assert abs(out - 0.0) < 1e-12 and abs(raw - 1.0) < 1e-12


def test_spawn_direction_and_locus():
    code = prog((SPAWN, 6, 7, 9))                # dir 6%4=2 (S), pos 9, locus 7
    _, _, spawn, _ = execute_plano(code, (0,) * 4, 0.0, (None,) * 5)
    assert spawn[0] == 2 and spawn[1] == 9 and spawn[3] == 7


# ------------------------------------------------------------- el sustrato
def test_initial_block_and_void():
    u = UteroPlano(h=10, w=10, seed=0, bloque=4)
    assert int(u.alive.sum()) == 16 and u.n == 100
    assert set(u.genomas()) == {(r, c) for r in range(3, 7) for c in range(3, 7)}


def test_blind_physics_dies_and_void_is_colonized():
    u = UteroPlano(h=5, w=5, seed=0, bloque=1)
    u.code[2, 2] = prog((MUL, 4, 4, 5), (SPAWN, 1, 0, 0))   # viva, pare hacia el ESTE
    u.v[2, 2] = 0.3
    m = u.step()
    assert m["deaths"] == 0 and m["colonized"] == 1
    assert u.alive[2, 3]
    assert ((2, 2), (2, 3)) in u.spawns
    u2 = UteroPlano(h=3, w=3, seed=0, bloque=1)
    u2.code[1, 1] = 0                                        # todo NOP: ciega
    m2 = u2.step()
    assert m2["deaths"] == 1 and not u2.alive.any()


def test_wall_blocks_spawn():
    u = UteroPlano(h=3, w=3, seed=0, bloque=1)
    u.code[1, 1] = prog((MUL, 4, 4, 5), (SPAWN, 0, 0, 0))   # hacia el NORTE
    u.alive[:] = False
    u.alive[0, 1] = True
    u.code[0, 1] = u.code[1, 1]
    u.v[0, 1] = 0.3
    m = u.step()
    assert m["colonized"] == 0 and int(u.alive.sum()) == 1


def test_invasion_asentada_and_recombina_flags():
    u = UteroPlano(h=3, w=3, seed=0, bloque=1, invasion="asentada", eq_window=3, recombina=True)
    u.alive[:] = False
    settled = prog((MUL, 4, 4, 5))
    mother = prog((MUL, 4, 4, 5), (SPAWN, 1, 7, 9))          # pare hacia el ESTE, locus 7
    other = prog((MUL, 4, 4, 5))
    other[7] = (CONST, 12, 0, 1)
    for rc, code in (((1, 1), mother), ((1, 2), settled), ((1, 0), other)):
        u.alive[rc] = True
        u.code[rc] = code
        u.v[rc] = 0.0
    inv = 0
    for _ in range(12):
        inv += u.step()["invaded"]
    assert inv >= 1
    np.testing.assert_array_equal(u.code[1, 2, 7], other[7])   # la cría lleva el locus del otro progenitor


def test_memory_persists_and_child_is_born_without_it():
    u = UteroPlano(h=5, w=5, seed=3, bloque=1, memoria=True)
    u.code[2, 2] = prog((ADD, 4, 5, 5), (SPAWN, 1, 0, 0))   # R = v + R (integrador), pare al ESTE
    u.v[2, 2] = 0.3
    u.step()
    assert abs(u.mem[2, 2]) > 0            # la madre acumula potencial
    assert u.alive[2, 3] and u.mem[2, 3] == 0.0   # la cría nace sin recuerdos
    u.step()
    assert abs(u.mem[2, 2]) > 0.3          # y sigue integrando (2º orden)


def test_determinism_and_flags_off_identity():
    a = UteroPlano(h=12, w=12, seed=7, bloque=4, memoria=True)
    b = UteroPlano(h=12, w=12, seed=7, bloque=4, memoria=True, invasion=None, recombina=False)
    for _ in range(100):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_shadow_mode_kills_scheduled_number():
    sched = [0, 2, 0, 1]
    u = UteroPlano(h=8, w=8, seed=1, bloque=4, shadow_deaths=sched)
    for d in sched:
        before = int(u.alive.sum())
        assert u.step()["deaths"] == min(d, before)


# --------------------------------------------- la vara honesta lo acepta
def test_medidas_and_ablacion_accept_the_plane():
    r = correr_medido(seed=2, flags=dict(memoria=True), ticks=200, tranche=50, t_filtro=25,
                      fabrica=fabrica)
    assert r["raw"].shape == (200,) and r["filt"].shape == (4,) and r["vivas"][-1] >= 0
    a = correr_ablacion(seed=2, memoria=True, ticks=120, ablate_at=60, fabrica=fabrica)
    assert a["novedad"].shape == (120,) and a["ablated"] >= 0


# ------------------------------------------------------------- el sol en el plano
def test_plane_sun_flags_off_are_byte_identical():
    from zeta_life.utero.sol import Sol
    a = UteroPlano(h=12, w=12, seed=7, bloque=4, memoria=True)
    b = UteroPlano(h=12, w=12, seed=7, bloque=4, memoria=True, sol=None, sol_sonda=True, sol_acople=0.5)
    for _ in range(100):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)
    c = UteroPlano(h=12, w=12, seed=7, bloque=4, memoria=True, sol=Sol(seed=0, ticks=200))
    for _ in range(100):
        c.step()
    assert not (np.array_equal(a.v, c.v) and np.array_equal(a.code, c.code))


def test_plane_void_and_walls_carry_the_sun_and_surface_heats():
    from zeta_life.utero.sol import Sol
    sol = Sol(seed=1, ticks=50)
    u = UteroPlano(h=3, w=3, seed=0, bloque=1, sol=sol, sol_acople=1.0)
    u.code[1, 1] = prog((ADD, 4, 4, 5))          # R = 2v: no lee el vacío
    u.v[1, 1] = 0.3
    u.step()
    ctx, vs = u._ctx(1, 1)
    assert all(abs(x - sol(0)) < 1e-12 for x in vs)   # los 4 vecinos son vacío iluminado
    assert abs(u.v[1, 1] - sol(0)) < 1e-12           # y la superficie quedó a la temperatura del sol
