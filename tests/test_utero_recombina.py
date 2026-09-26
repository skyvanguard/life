"""Tests de v7: recombinación al nacer (la cría toma UNA instrucción del otro
progenitor — el vecino de la madre del lado opuesto al parto — si su genoma
difiere del de la madre). Sin RNG: la variación sale del contacto."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import CONST, MUL, SPAWN, K


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


B, C = 7, 5
MOTHER = prog((MUL, 1, 1, 3), (SPAWN, 1, B, C))       # pare hacia la DERECHA
OTHER = prog((MUL, 1, 1, 3))                          # el otro progenitor (izquierda)
OTHER[B] = (CONST, 12, 0, 1)                          # instrucción distintiva en el locus B


def mundo(recombina, other=OTHER):
    u = UteroCreciente(n0=3, seed=0, max_n=3, toroidal=True, germinal=True,
                       recombina=recombina)
    u.code[0] = other
    u.code[1] = MOTHER
    u.alive[2] = False                                # vacío a la derecha de la madre
    u.code[2] = 0
    u.v[:] = 0.3
    u.mem[:] = 0.0
    return u


def test_recombina_off_child_does_not_carry_the_other_parent_locus():
    u = mundo(False)
    u.step()
    assert u.alive[2]
    assert u.code[2, B, 0] != CONST                   # sólo la mutación germinal de v2


def test_recombina_copies_one_instruction_from_the_other_parent():
    u = mundo(True)
    u.step()
    assert u.alive[2]
    np.testing.assert_array_equal(u.code[2, B], OTHER[B])    # locus B viene del otro progenitor
    # el resto sigue siendo la cría germinal de la madre (salvo la mutación en C)
    for k in range(K):
        if k not in (B, C):
            np.testing.assert_array_equal(u.code[2, k], MOTHER[k])


def test_no_recombination_with_a_clone_parent():
    u = mundo(True, other=MOTHER.copy())              # el otro progenitor es un clon
    u.step()
    assert u.alive[2]
    assert u.code[2, B, 0] != CONST


def test_no_recombination_without_other_parent():
    u = mundo(True)
    u.alive[0] = False                                # la madre no tiene otro vecino
    u.step()
    assert u.alive[2]
    assert u.code[2, B, 0] != CONST


def test_default_is_byte_identical_to_v5_and_v6():
    for flags in (dict(), dict(invasion="asentada")):
        a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, **flags)
        b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True,
                           recombina=False, **flags)
        for _ in range(300):
            a.step()
            b.step()
        np.testing.assert_array_equal(a.code, b.code)
        np.testing.assert_array_equal(a.v, b.v)


def test_recombina_changes_dynamics_on_a_real_world():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True)
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True,
                       recombina=True)
    for _ in range(600):
        a.step()
        b.step()
    assert not (a.n == b.n and np.array_equal(a.code, b.code))
