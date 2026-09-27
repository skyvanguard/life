"""Tests de v16: escritura total (MUTO y el germinal escriben la instruccion entera desde los registros).
Incluye la prueba directa de la cuarta jaula: sin el flag, los trios (a,b,c) de un mundo son un
subconjunto de los de su sopa inicial; con el flag, aparecen trios nuevos."""

import numpy as np

from zeta_life.utero.creciente import UteroCreciente
from zeta_life.utero.nivel2 import CONST, MUTO, K, execute


def prog(*instrs):
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


def trios(u):
    return {tuple(int(x) for x in r[1:]) for r in u.code[u.alive].reshape(-1, 4)}


def test_total_off_is_byte_identical():
    a = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, invasion="asentada")
    b = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, invasion="asentada",
                       escritura_total=False)
    for _ in range(400):
        a.step()
        b.step()
    np.testing.assert_array_equal(a.code, b.code)
    np.testing.assert_array_equal(a.v, b.v)


def test_muto_total_writes_all_four_fields_from_registers():
    # r0=0.25 (CONST a=9), r1=v, r2=vr, r3=R3; MUTO pos 5 <- fila desde b=0: op=|r0|*10, a=|r1|*16, b=|r2|*16, c=|r3|*16
    code = prog((CONST, 9, 0, 0), (MUTO, 5, 0, 0))
    _, own, _, _ = execute(code, 0.1, 0.5, 0.75, (None, code, None), wrap=True, total=True)
    assert tuple(own[5]) == (2, 8, 12, 0)
    _, own_old, _, _ = execute(code, 0.1, 0.5, 0.75, (None, code, None), wrap=True, total=False)
    assert tuple(own_old[5]) == (2, 0, 0, 0)          # sin el flag solo cambia el opcode


def test_fourth_cage_operand_closure_holds_without_flag_and_breaks_with_it():
    T = 3000
    cerrado = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, invasion="asentada")
    inicial = trios(cerrado)
    for _ in range(T):
        cerrado.step()
    assert trios(cerrado) <= inicial, "sin el flag aparecieron trios nuevos: la clausura no se cumple"
    abierto = UteroCreciente(n0=16, seed=13, germinal=True, toroidal=True, memoria=True, invasion="asentada",
                             escritura_total=True)
    inicial2 = trios(abierto)
    for _ in range(T):
        abierto.step()
    assert not (trios(abierto) <= inicial2), "con el flag no aparecio ningun trio nuevo"
