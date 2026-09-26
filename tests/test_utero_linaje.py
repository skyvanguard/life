"""Tests de los ganchos de registro (eventos, engendros, sombra) y del filtro
de persistencia de linaje (MODES) — todo byte-idéntico con los flags apagados."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.linaje import RastreadorLinaje
from zeta_life.utero.nivel2 import ADD, CONST, COPY, MUTO, K, execute


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


# ----------------------------------------------------------- execute(stats=)
def test_execute_stats_counts_effective_copy_and_muto_writes():
    own = prog((COPY, 0, 0, 5), (MUTO, 6, 1, 0))   # instr 0 del izq -> propia 5 ; MUTO en la 6
    left = prog((CONST, 12, 0, 1))                 # genoma DISTINTO al propio
    stats: dict = {}
    _, own_next, _, _ = execute(own, 0.3, 0.3, 0.3, (left, own, None), wrap=True, stats=stats)
    # COPY: own[5] pasa de NOP a (CONST,12,0,1) -> escritura efectiva desde genoma distinto
    assert np.array_equal(own_next[5], left[0])
    # MUTO: |R1|=v=0.3 -> op int(3.0)%10 = 3 en la instr 6 (era NOP) -> escritura efectiva
    assert own_next[6, 0] == 3
    assert stats == {"copy_writes": 1, "muto_writes": 1, "copy_distinct": True}


def test_execute_stats_zero_when_copy_is_noop():
    own = prog((COPY, 1, 2, 2))      # copia de sí misma la instr 2 a la 2: no cambia nada
    stats: dict = {}
    execute(own, 0.0, 0.0, 0.0, (None, own, None), wrap=True, stats=stats)
    assert stats == {"copy_writes": 0, "muto_writes": 0, "copy_distinct": False}


def test_execute_without_stats_is_unchanged():
    own = prog((COPY, 0, 0, 5), (ADD, 1, 1, 3))
    left = prog((CONST, 12, 0, 1))
    a = execute(own, 0.3, 0.3, 0.3, (left, own, None), wrap=True)
    b = execute(own, 0.3, 0.3, 0.3, (left, own, None), wrap=True, stats={})
    assert a[0] == b[0] and np.array_equal(a[1], b[1]) and a[2] == b[2] and a[3] == b[3]


# ------------------------------------------------------- log_events / deaths
def test_log_events_is_byte_identical_and_records():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True,
                       log_events=True)
    total_spawns = total_copy = 0
    for _ in range(300):
        ma = a.step()
        mb = b.step()
        assert ma["colonized"] + ma["grown"] == len(b.spawns)
        total_spawns += len(b.spawns)
        total_copy += sum(s["copy_writes"] for s in b.events.values())
        assert "deaths" in mb
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)
    assert total_spawns > 0 and total_copy > 0
    for parent, child in b.spawns:
        assert abs(parent - child) == 1        # el engendro es siempre vecino


def test_spawn_coords_are_stable_across_left_growth():
    u = UteroCreciente(n0=16, seed=3, germinal=True, toroidal=True, log_events=True)
    for _ in range(400):
        u.step()
        for parent, child in u.spawns:
            i = child + u.left_grown            # la cría existe en esa coordenada
            assert 0 <= i < u.n and u.alive[i]


# ---------------------------------------------------------------- sombra
def test_shadow_mode_kills_the_scheduled_number_and_skips_the_probe():
    sched = [0, 3, 0, 5]
    u = UteroCreciente(n0=16, seed=0, germinal=True, toroidal=True, memoria=True,
                       shadow_deaths=sched)
    for k, d in enumerate(sched):
        alive_before = int(u.alive.sum())
        m = u.step()
        assert m["deaths"] == min(d, alive_before)
    # con sonda apagada, la física ciega (todo NOP) sobrevive
    u2 = UteroCreciente(n0=4, seed=0, toroidal=True, shadow_deaths=[0] * 5)
    u2.code[:] = 0
    for _ in range(5):
        u2.step()
    assert u2.alive.all()


# ------------------------------------------------------- filtro de linaje
def test_lineage_filter_counts_only_genomes_with_living_descent():
    r = RastreadorLinaje(t_filtro=10)
    # t=0: la coord 0 acuña el genoma A, la coord 1 acuña B
    r.tick(0, vivas={0: b"A", 1: b"B"}, spawns=[])
    # t=1: la coord 1 muere (B sin descendencia); la 0 sigue viva reescrita a C
    r.tick(1, vivas={0: b"C"}, spawns=[])
    # t=2: la 0 engendra a la 2 (que nace con C)
    r.tick(2, vivas={0: b"C", 2: b"C"}, spawns=[(0, 2)])
    # t=3..: la 0 muere, la 2 persiste hasta el final
    for t in range(3, 15):
        r.tick(t, vivas={2: b"C"}, spawns=[])
    res = r.resueltos()
    assert res[b"A"] is True       # A -> C -> cría 2 viva en t>=10: linaje persistente
    assert res[b"B"] is False      # B murió sin descendencia
    assert res[b"C"] is True


def test_lineage_filter_novelty_per_tranche():
    r = RastreadorLinaje(t_filtro=5)
    r.tick(0, vivas={0: b"A"}, spawns=[])
    r.tick(1, vivas={0: b"A", 1: b"B"}, spawns=[(0, 1)])
    for t in range(2, 12):
        r.tick(t, vivas={0: b"A"}, spawns=[])          # B murió en t=2
    nov = r.novedad_filtrada(tramo=5, ticks=12)
    assert list(nov) == [1, 0, 0]      # sólo A (acuñada en el tramo 0) persiste
