"""
§24 — ¿POSICIÓN O PROGRAMA? Réplicas de un mundo congelado con las POSICIONES
barajadas, en la ecología de frontera abierta y en una de frontera cerrada.
(docs/PLAN_INTELIGENCIA.md §24; ledger 2026-09-27)

MOTIVO. §21 mostró concordancia total entre réplicas que variaban el orden
de actualización pero NO las posiciones de la sopa; §23 mostró que en la
competencia 8 contra 8 la disposición decide el resultado ((1.00, 0.00) en
casi la mitad de las semillas). Si quien gana lo decide dónde está y no qué
programa corre, la selección no ve genomas y nada puede adaptarse: efecto
fundador espacial en una línea con la frontera abierta.

DISEÑO. Mundos CONGELADOS (sin herencia de cambios). Por sopa (10), cinco
réplicas que conservan el MISMO conjunto de genomas y materias iniciales pero
los colocan en posiciones barajadas (permutación sembrada por réplica), con
el mismo orden de actualización. Dos ecologías:
  ABIERTA: la de §17 (n0 = 16, max_n = 512; ≈80 vivas en 512 lugares: la
           frontera está siempre abierta).
  CERRADA: n0 = 64 = max_n (la línea nace llena y no crece): la reproducción
           sólo ocurre hacia lugares que la muerte abre o por invasión de
           tejido asentado; la competencia es interior y local.
30000 ticks, sol seed 0 cíclico, L0 = 9. Al final, cuenta de vivas por genoma
inicial; W de Kendall entre las 5 réplicas, nulo por permutación de etiquetas
(1000).
VEREDICTO por ecología (escrito antes de correr):
  PROGRAMA    si p_W < 0.05 en ≥ 8/10 sopas (el mismo genoma gana aunque
              cambie de lugar).
  POSICIÓN    si p_W < 0.05 en ≤ 3/10 sopas.
  MIXTO       en otro caso.
Lectura conjunta: ABIERTA = POSICIÓN y CERRADA = PROGRAMA significa que la
frontera abierta era la causa estructural de que la selección no viera
genomas; entonces la evolvabilidad (§17) y luego la regulación se vuelven a
medir en la ecología cerrada. ABIERTA = PROGRAMA desmiente la hipótesis.
CERRADA = POSICIÓN también: la posición manda incluso sin frontera y hay que
cambiar la topología (anillo, plano) o el filtro.

    PYTHONPATH=src python experiments/utero/exp_utero_posicion.py
"""

from __future__ import annotations

import importlib.util
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

TICKS = 30000
SOPAS = list(range(10))
REPLICAS = list(range(5))
SOL_SEED = 0
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
BASE = dict(memoria=True, invasion="asentada", eq_window=100, energia=True, luz_finita=9.0,
            e0=2.0, e_mant=0.01, e_dif=0.25, e_parto=0.5, percepcion=False, lentos=0.02, e_costo=1.0,
            congelado=True)
ECOLOGIAS = {"abierta": dict(n0=16, max_n=512), "cerrada": dict(n0=64, max_n=64)}
N_PERM = 1000
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_posicion"


def _kendall():
    spec = importlib.util.spec_from_file_location("rep", HERE / "exp_utero_seleccion_replicas.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.kendall_w


def correr(eco: str, sopa: int, rep: int) -> tuple:
    n0, max_n = ECOLOGIAS[eco]["n0"], ECOLOGIAS[eco]["max_n"]
    sol = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    u = UteroCreciente(n0=n0, seed=sopa, max_n=max_n, germinal=True, toroidal=True, sol=sol,
                       orden_seed=777, **BASE)
    iniciales = [huella(u.code[i]) for i in range(n0)]          # etiquetas fijas por sopa
    perm = np.random.default_rng(10_000 + rep).permutation(n0)   # rep 0 tambien baraja (todas iguales en eso)
    u.code = u.code[perm].copy()
    u.v = u.v[perm].copy()
    for _ in range(TICKS):
        u.step()
    vivos = [huella(u.code[i]) for i in np.flatnonzero(u.alive)]
    cuentas = [vivos.count(g) for g in iniciales]
    return eco, sopa, rep, cuentas, len(vivos)


def job(a):
    return correr(*a)


def main() -> None:
    kendall_w = _kendall()
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("POSICION O PROGRAMA? -- replicas congeladas con las POSICIONES barajadas; frontera abierta vs cerrada")
    out("=" * 80)
    out(f"ecologia base {BASE}; ecologias {ECOLOGIAS}; {len(SOPAS)} sopas x {len(REPLICAS)} replicas; {TICKS} ticks; permutaciones {N_PERM}; workers={WORKERS}")
    out("veredicto pre-registrado (docstring)")
    out("")
    res: dict = {e: {s: {} for s in SOPAS} for e in ECOLOGIAS}
    jobs = [(e, s, r) for e in ECOLOGIAS for s in SOPAS for r in REPLICAS]
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for eco, sopa, rep, cuentas, vivos in ex.map(job, jobs):
            res[eco][sopa][rep] = (cuentas, vivos)
    rng = np.random.default_rng(0)
    veredictos = {}
    for eco in ECOLOGIAS:
        out("-" * 80)
        out(f"ECOLOGIA {eco} {ECOLOGIAS[eco]}")
        out(f"  {'sopa':>4} {'vivas':>6} {'W':>6} {'p_W':>7} {'mismo dominante':>15} {'share dom':>9} {'genomas vivos':>13}")
        sig = n_ok = 0
        for sopa in SOPAS:
            mats = [np.array(res[eco][sopa][r][0]) for r in REPLICAS]
            vivos = [res[eco][sopa][r][1] for r in REPLICAS]
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
            out(f"  {sopa:>4} {int(np.median(vivos)):>6} {w:>6.2f} {p:>7.3f} {mismo:>12}/{len(REPLICAS)} {share:>9.2f} {gv:>13.0f}")
        out(f"  sopas evaluables {n_ok}/{len(SOPAS)}; con p_W < 0.05: {sig}")
        veredictos[eco] = "PROGRAMA" if sig >= 8 else ("POSICION" if sig <= 3 else "MIXTO")
        out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    for eco, v in veredictos.items():
        out(f"=> {eco}: {v}")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
