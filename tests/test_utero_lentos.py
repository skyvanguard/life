"""Tests de v13: registros lentos (escritura lenta S <- S + lambda (w - S); relojes a la escala de la estacion)."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import ADD, CONST, MUL, K, execute


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


def test_execute_with_list_extra_reads_and_writes_back():
    code = prog((CONST, 12, 0, 5), (ADD, 4, 4, 3))       # S1 <- 1.0 ; R3 = 2*S0
    xtra = [0.25, 0.0]                                    # S0=0.25, S1=0.0 (registros 4 y 5)
    out, _, _, _ = execute(code, 0.1, 0.1, 0.1, (None, code, None), wrap=True, extra=xtra)
    assert abs(out - 0.5) < 1e-12                          # leyó S0
    assert xtra == [0.25, 1.0]                             # devolvió lo escrito en S1


def test_lentos_off_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, lentos=0.0)
    for _ in range(300):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_slow_write_charges_exponentially_like_a_clock():
    lam = 0.01
    u = UteroCreciente(n0=1, seed=0, max_n=1, toroidal=True, lentos=lam)
    # R3 = v*v (sensible); S1 (registro 4) <- 1.0 cada tick: se carga con tau = 1/lambda
    u.code[0] = prog((MUL, 1, 1, 3), (CONST, 12, 0, 4))
    u.v[0] = 0.3
    for t in range(1, 201):
        u.step()
        assert abs(u.S[0, 0] - (1.0 - (1.0 - lam) ** t)) < 1e-9
    assert u.S[0, 1] == 0.0                                # el registro no escrito no cambia


def test_child_is_born_with_zero_clock_and_rule_can_read_the_clock():
    from zeta_life.utero.nivel2 import SPAWN
    u = UteroCreciente(n0=3, seed=0, max_n=3, toroidal=True, lentos=0.5)
    u.alive[:] = False
    u.alive[1] = True
    # R3 = v*v + S1 ; S1 <- 1 ; pare a la derecha
    u.code[1] = prog((MUL, 1, 1, 3), (CONST, 12, 0, 4), (ADD, 3, 4, 3), (SPAWN, 1, 0, 0))
    u.v[1] = 0.5
    u.step()
    assert u.alive[2] and u.S[2, 0] == 0.0 and abs(u.S[1, 0] - 0.5) < 1e-12
