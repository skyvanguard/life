"""§15 — CLAUSURA DE OPERANDOS: ¿el ahorrador es ALCANZABLE por la variación del útero?
Hecho estructural (leído en nivel2.execute): MUTO escribe own_next[a%K, 0]; el germinal escribe
child[c%K, 0]; COPY injerta una fila existente; SPAWN copia. Ningún camino escribe los campos
a,b,c. Los tríos de operandos del mundo son exactamente los de la sopa inicial (n0*K filas).
Medida 1: fracción de los 16^3 tríos presentes en una sopa (esperado 1-(1-1/4096)^256).
Medida 2: para las semillas 0..39 con la config de v14/v15 (m = 6 registros por lentos), ¿la sopa
contiene al menos una fila de cada CLASE FUNCIONAL que el ahorrador necesita (operandos módulo m,
posición módulo K, lado módulo 2)? Y por Monte Carlo (20000 sopas) la probabilidad poblacional.
Esto es una COTA SUPERIOR de alcanzabilidad: tener las piezas no las ensambla.

RESULTADO (2026-09-26): 6.06% de los tríos por sopa, congelados; 3/40 semillas con todas las
piezas; P = 0.157 poblacional. La cuarta jaula: la variación reescribe 1 de los 4 campos.

    PYTHONPATH=src python experiments/utero/exp_utero_alcance_operandos.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
import numpy as np  # noqa: E402

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402

RESULTS = HERE.parents[1] / "results"
LINES: list[str] = []


def out(t: str = "") -> None:
    print(t, flush=True)
    LINES.append(t)

K, M, ARG = 16, 6, 16          # M = 4 registros + 2 lentos (v13+)


def clase(row, op, a=None, b=None, c=None, mod_a=M, mod_b=M, mod_c=M, exact_a=False, cset=None):
    o, x, y, z = (int(v) for v in row)
    if o != op:
        return False
    if a is not None and ((x != a) if exact_a else (x % mod_a != a)):
        return False
    if b is not None and y % mod_b != b:
        return False
    if cset is not None:
        return z % K in cset
    if c is not None and z % mod_c != c:
        return False
    return True


NOP, ADD, SUB, MUL, THR, CONST, READ, MUTO, COPY, SPAWN = range(10)
# piezas del ahorrador (exp_utero_control_positivo.AHORRADOR), como clases funcionales
PIEZAS = {
    "ADD vr,R3->S2 (2,3,5)":      (lambda r: clase(r, ADD, 2, 3, 5), 1),
    "CONST 0.5 ->r0 (a=10)":      (lambda r: clase(r, CONST, 10, None, 0, exact_a=True), 1),
    "THR S2>r0 ->r2 (5,0,2)":     (lambda r: clase(r, THR, 5, 0, 2), 1),
    "CONST 0.75 ->r0 (a=11)":     (lambda r: clase(r, CONST, 11, None, 0, exact_a=True), 1),
    "MUL r2*r0->r2 (2,0,2) x2":   (lambda r: clase(r, MUL, 2, 0, 2), 2),
    "CONST 1.25 ->r0 (a=13)":     (lambda r: clase(r, CONST, 13, None, 0, exact_a=True), 1),
    "MUTO pos9 <- |r2| (a=9,b=2)": (lambda r: clase(r, MUTO, 9, 2, None, exact_a=True), 1),
    "MUL v*v->R3 (1,1,3)":        (lambda r: clase(r, MUL, 1, 1, 3), 1),
    "SPAWN der,b=3,c en fila vacia": (lambda r: clase(r, SPAWN, 1, 3, None, mod_a=2, cset=set(range(10, 16))), 1),
}
# nota: para la CLASE sólo importan los operandos; el opcode lo puede poner MUTO/germinal después.
PIEZAS_OPERANDOS = {k: (lambda r, f=f: f(np.array([int(r[0]), *r[1:]])) or f(np.array([_op(k), *r[1:]])), n)
                    for k, (f, n) in PIEZAS.items()}


def _op(k):
    return {"ADD": ADD, "CONST": CONST, "THR": THR, "MUL": MUL, "MUTO": MUTO, "SPAWN": SPAWN}[k.split()[0]]


def tiene_piezas(code):        # code: (n, K, 4) -> dict pieza -> cuenta de filas cuyo TRÍO sirve
    rows = code.reshape(-1, 4)
    out = {}
    for k, (f, n) in PIEZAS.items():
        op = _op(k)
        cnt = sum(1 for r in rows if f(np.array([op, r[1], r[2], r[3]])))
        out[k] = (cnt, n)
    return out


def main():
    out("MEDIDA 1: tríos distintos en la sopa (16 celdas x 16 filas = 256 filas; 4096 tríos posibles)")
    fr = []
    for s in range(40):
        u = UteroCreciente(n0=16, seed=s, max_n=256, germinal=True, toroidal=True)
        tri = {tuple(int(x) for x in r[1:]) for r in u.code.reshape(-1, 4)}
        fr.append(len(tri))
    out(f"  tríos distintos por sopa: mediana {np.median(fr):.0f} / 4096 = {np.median(fr) / 4096:.3%} "
          f"(esperado {1 - (1 - 1 / 4096) ** 256:.3%}); ese conjunto NO cambia nunca en el mundo")
    out()
    out("MEDIDA 2: ¿la sopa contiene los operandos de cada pieza del ahorrador? (semillas 0..39 de v14/v15)")
    completas = 0
    por_pieza = {k: 0 for k in PIEZAS}
    for s in range(40):
        u = UteroCreciente(n0=16, seed=s, max_n=256, germinal=True, toroidal=True)
        t = tiene_piezas(u.code)
        ok = all(cnt >= n for cnt, n in t.values())
        completas += ok
        for k, (cnt, n) in t.items():
            por_pieza[k] += cnt >= n
        faltan = [k.split(" (")[0] for k, (cnt, n) in t.items() if cnt < n]
        out(f"  seed {s:>2}: {'TODAS las piezas' if ok else 'faltan ' + str(len(faltan)) + ': ' + ', '.join(faltan)}")
    out(f"  sopas con todas las piezas: {completas}/40")
    for k, v in por_pieza.items():
        out(f"    {k:<34} presente en {v}/40 sopas")
    out()
    out("MONTE CARLO poblacional (20000 sopas uniformes como las del útero):")
    rng = np.random.default_rng(0)
    ok = 0
    N = 20000
    for _ in range(N):
        code = np.zeros((16, K, 4), dtype=np.int64)
        code[:, :, 1:] = rng.integers(0, ARG, size=(16, K, 3))
        t = tiene_piezas(code)
        ok += all(cnt >= n for cnt, n in t.values())
    out(f"  P(la sopa contiene los operandos de TODAS las piezas) = {ok / N:.3f}")
    out("  (cota superior: además hay que reunirlas en UNA celda y en ORDEN vía COPY, cuyos propios")
    out("   operandos (b = fila origen, c = fila destino) también están congelados en la sopa)")

    (RESULTS / "utero_alcance_operandos_run.txt").write_text(chr(10).join(LINES), encoding="utf-8")


if __name__ == "__main__":
    main()
