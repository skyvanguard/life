"""
§21 — ¿LA SELECCIÓN VE LOS GENOMAS? Réplicas de un mundo congelado con otro
azar de orden. (docs/PLAN_INTELIGENCIA.md §21; ledger 2026-09-27)

PREGUNTA. En un mundo CONGELADO (sin herencia de cambios) sólo existen los 16
genomas de la sopa inicial y su abundancia final es el único resultado de la
selección sobre programas fijos. Si la selección actúa sobre el genoma, la
abundancia final de cada genoma debe CONCORDAR entre réplicas del mismo
mundo que sólo difieren en el azar del orden de actualización (`orden_seed`);
si lo que decide es la posición inicial y el azar, la concordancia será la del
nulo. Es la lógica de las réplicas de Lenski aplicada al único componente que
la hambruna no confunde.

DISEÑO. 10 sopas (seed 0..9) × 5 órdenes (orden_seed 100..104), congelado,
ecología de §17 (L0 = 9, e_dif 0.25), sol seed 0 cíclico, 30000 ticks. Al final:
cuenta de celdas vivas por genoma inicial (16 valores por réplica).
ESTADÍSTICO por sopa: W de Kendall entre las 5 réplicas sobre los rangos de
los 16 genomas; nulo: permutar las etiquetas de genoma dentro de cada réplica
(1000 permutaciones). También: el genoma dominante es el mismo en k/5.
VEREDICTO (escrito antes de correr):
  SELECCIÓN   si p_W < 0.05 en ≥ 8/10 sopas → la ecología discrimina
              programas fijos de forma reproducible; entonces la falta de
              adaptación con herencia (§17/§20) apunta a la tasa de mutación
              (§22).
  POSICIÓN    si p_W < 0.05 en ≤ 3/10 sopas → lo que decide no es el
              programa: hay que cambiar qué mide el filtro.
  MIXTO       en otro caso.

    PYTHONPATH=src python experiments/utero/exp_utero_seleccion_replicas.py
"""

from __future__ import annotations

import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.nivel2 import huella  # noqa: E402
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N0, MAX_N = 16, 512
TICKS = 30000
SOPAS = list(range(10))
ORDENES = list(range(100, 105))
SOL_SEED = 0
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
BASE = dict(memoria=True, invasion="asentada", eq_window=100, energia=True, luz_finita=9.0,
            e0=2.0, e_mant=0.01, e_dif=0.25, e_parto=0.5, percepcion=False, lentos=0.02, e_costo=1.0,
            congelado=True)
N_PERM = 1000
WORKERS = max(1, min(6, (os.cpu_count() or 4) // 4))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_seleccion_replicas"


def correr(sopa: int, orden: int) -> tuple:
    sol = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    u = UteroCreciente(n0=N0, seed=sopa, max_n=MAX_N, germinal=True, toroidal=True, sol=sol,
                       orden_seed=orden, **BASE)
    iniciales = [huella(u.code[i]) for i in range(N0)]
    for _ in range(TICKS):
        u.step()
    vivos = [huella(u.code[i]) for i in np.flatnonzero(u.alive)]
    cuentas = [vivos.count(g) for g in iniciales]
    return sopa, orden, cuentas, len(vivos)


def job(a):
    return correr(*a)


def kendall_w(mat: np.ndarray) -> float:
    """mat: (m réplicas, n genomas) -> W de Kendall sobre rangos (con empates promediados)."""
    m, n = mat.shape
    ranks = np.zeros_like(mat, dtype=float)
    for i in range(m):
        order = mat[i].argsort()
        r = np.empty(n)
        r[order] = np.arange(1, n + 1)
        # empates: promedio de rangos
        for v in np.unique(mat[i]):
            idx = np.flatnonzero(mat[i] == v)
            r[idx] = r[idx].mean()
        ranks[i] = r
    R = ranks.sum(axis=0)
    S = ((R - R.mean()) ** 2).sum()
    return float(12 * S / (m * m * (n ** 3 - n)))


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("SELECCION VE LOS GENOMAS? -- replicas de un mundo CONGELADO con otro azar de orden: concuerda la abundancia final?")
    out("=" * 80)
    out(f"ecologia {BASE}; {len(SOPAS)} sopas x {len(ORDENES)} ordenes; {TICKS} ticks; sol seed {SOL_SEED}; permutaciones {N_PERM}; workers={WORKERS}")
    out("veredicto pre-registrado (docstring)")
    out("")
    res: dict = {s: {} for s in SOPAS}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for sopa, orden, cuentas, vivos in ex.map(job, [(s, o) for s in SOPAS for o in ORDENES]):
            res[sopa][orden] = (cuentas, vivos)
    rng = np.random.default_rng(0)
    out(f"  {'sopa':>4} {'vivas':>6} {'W':>6} {'p_W':>7} {'mismo dominante':>15} {'share dom':>9} {'genomas vivos':>13}")
    sig = 0
    n_ok = 0
    for sopa in SOPAS:
        mats = [np.array(res[sopa][o][0]) for o in ORDENES]
        vivos = [res[sopa][o][1] for o in ORDENES]
        if min(vivos) == 0:
            out(f"  {sopa:>4} {int(np.median(vivos)):>6}   (alguna replica extinta: no evaluable)")
            continue
        n_ok += 1
        mat = np.stack(mats)
        w = kendall_w(mat)
        nul = np.array([kendall_w(np.stack([rng.permutation(row) for row in mat])) for _ in range(N_PERM)])
        p = float((np.sum(nul >= w) + 1) / (N_PERM + 1))
        dom = [int(m.argmax()) for m in mats]
        mismo = max(dom.count(d) for d in set(dom))
        share = float(np.median([m.max() / m.sum() for m in mats]))
        gv = float(np.median([(m > 0).sum() for m in mats]))
        sig += p < 0.05
        out(f"  {sopa:>4} {int(np.median(vivos)):>6} {w:>6.2f} {p:>7.3f} {mismo:>12}/{len(ORDENES)} {share:>9.2f} {gv:>13.0f}")
    out(f"  sopas evaluables {n_ok}/{len(SOPAS)}; con p_W < 0.05: {sig}")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if sig >= 8:
        out(f"=> SELECCION: la abundancia final de los genomas concuerda entre replicas en {sig}/{n_ok} sopas; la ecologia discrimina programas fijos.")
    elif sig <= 3:
        out(f"=> POSICION: concordancia solo en {sig}/{n_ok} sopas; lo que decide no es el programa.")
    else:
        out(f"=> MIXTO: concordancia en {sig}/{n_ok} sopas.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
