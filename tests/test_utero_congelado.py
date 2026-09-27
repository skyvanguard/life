"""Tests de §17: brazo congelado (MUTO y COPY inertes, germinal sin escribir: sin herencia de cambios)."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import CONST, MUTO, K, execute


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


def test_congelado_off_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, invasion="asentada",
                       escritura_total=True)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, invasion="asentada",
                       escritura_total=True, congelado=False)
    for _ in range(400):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_frozen_execute_does_not_write_own_code():
    code = prog((CONST, 9, 0, 0), (MUTO, 5, 0, 0))
    _, own, _, _ = execute(code, 0.1, 0.5, 0.75, (None, code, None), wrap=True, total=True, frozen=True)
    np.testing.assert_array_equal(own, code)


def test_frozen_world_never_mints_a_genome():
    u = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, invasion="asentada",
                       escritura_total=True, congelado=True)
    inicial = {u.code[i].tobytes() for i in range(u.n)}
    for _ in range(2000):
        u.step()
    vivos = {u.code[i].tobytes() for i in np.flatnonzero(u.alive)}
    assert vivos <= inicial
