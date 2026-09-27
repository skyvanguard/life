"""
§29 — POBLACIÓN EFECTIVA: §27 con la línea cerrada ocho veces más grande.
(docs/PLAN_INTELIGENCIA.md §29; ledger 2026-09-27)

MOTIVO. §28: el paisaje local del rasgo premiado es una meseta neutra con
escalones raros (0.19% de las escrituras lo suben +0.1; ninguna +0.2). Con
≈14 vivas (§27) un escalón de +0.1 es casi neutro frente a la deriva (s
comparable a 1/N) y aparece una vez cada ~19000 ticks por mundo. Aquí la
línea cerrada tiene 512 lugares y la luz escala igual (L0 = 14 = 1.75 × 8:
misma luz por lugar, misma presión de hambruna): ≈8× más vivas, ≈8× más
variantes por mundo y umbral de deriva 8× menor.

DISEÑO Y VEREDICTO: idénticos a §27 salvo N = 512, L0 = 14, brazos abierto
p = 1 (más variantes), cerrado, congelado; 12 semillas; 120000 ticks. Rasgo:
w̄_A (peso de luz de la materia viva durante la hambruna). ADAPTA si w̄_A
tardío/temprano supera al del congelado en ≥ 75% de los pares (p signo <
0.05, n ≥ 8) y el nivel w̄_A también en ≥ 75%. Si ADAPTA: la evolución en el
útero estaba limitada por la deriva; el camino a la regulación es población
y tiempo. Si NO: la meseta neutra manda con cualquier N alcanzable y hay que
cambiar cómo la materia sale del programa.

    PYTHONPATH=src python experiments/utero/exp_utero_rasgo_grande.py
"""

from __future__ import annotations

import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N = 512
TICKS = 120000
SEEDS = list(range(12))
SOL_SEED = 0
L0 = 14.0               # = 1.75 x 8: misma luz por lugar que §27
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
BASE = dict(memoria=True, invasion="asentada", eq_window=100, energia=True, luz_finita=L0,
            e0=2.0, e_mant=0.01, e_dif=0.25, e_parto=0.5, percepcion=False, lentos=0.02, e_costo=1.0)
ARMS = {"abierto_p1": dict(escritura_total=True),
        "cerrado": dict(),
        "congelado": dict(congelado=True)}
TRANSITORIO = 6000
MIN_HAMBRUNAS = 4
BANDA = 0.4
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_rasgo_grande"


def correr(seed: int, arm: str) -> dict:
    sol = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    u = UteroCreciente(n0=N, seed=seed, max_n=N, germinal=True, toroidal=True, sol=sol, **BASE, **ARMS[arm])
    w = np.full(TICKS, np.nan)
    banda = np.full(TICKS, np.nan)
    vivas = np.zeros(TICKS)
    muertes = np.zeros(TICKS)
    for t in range(TICKS):
        r = u.step()
        alive = u.alive
        n = int(alive.sum())
        vivas[t] = n
        muertes[t] = r["deaths"]
        if n:
            d = np.abs(u.v[alive] - float(sol(t)))
            d = np.minimum(d, 1.0 - d)
            w[t] = float(d.mean() + 0.05)
            banda[t] = float((d >= BANDA).mean())
    wA, pcA, bA = [], [], []
    for nombre, ini, fin in sol.estaciones:
        if nombre != "A" or ini < TRANSITORIO or fin > TICKS:
            continue
        v = vivas[ini:fin].mean()
        if v <= 0 or np.all(np.isnan(w[ini:fin])):
            continue
        wA.append(float(np.nanmean(w[ini:fin])))
        bA.append(float(np.nanmean(banda[ini:fin])))
        pcA.append(float(muertes[ini:fin].sum() / v))

    def razon(x):
        h = len(x) // 2
        return float(np.mean(x[h:]) / np.mean(x[:h])) if (h >= MIN_HAMBRUNAS and np.mean(x[:h]) > 0) else float("nan")

    return dict(seed=seed, arm=arm, n_h=len(wA), w_nivel=float(np.mean(wA)) if wA else float("nan"),
                w_razon=razon(wA), pc_nivel=float(np.mean(pcA)) if pcA else float("nan"), pc_razon=razon(pcA),
                banda_nivel=float(np.mean(bA)) if bA else float("nan"),
                vivas_med=float(np.median(vivas[TRANSITORIO:])), vivas_fin=float(vivas[-1]), genomas=len(u.seen))


def job(a):
    return correr(*a)


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("POBLACION EFECTIVA (N=512, L0=14): SUBE EL RASGO PREMIADO? -- peso de luz de la materia durante la hambruna, variacion abierta vs congelado; cerrado, luz escasa")
    out("=" * 80)
    out(f"ecologia {BASE}; N={N}; brazos {list(ARMS)}; {len(SEEDS)} semillas; {TICKS} ticks; sol seed {SOL_SEED}; workers={WORKERS}")
    out("veredicto pre-registrado (docstring)")
    out("")
    res: dict = {a: {} for a in ARMS}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for r in ex.map(job, [(s, a) for a in ARMS for s in SEEDS]):
            res[r["arm"]][r["seed"]] = r

    def med(arm, k):
        v = [res[arm][s][k] for s in SEEDS]
        v = [x for x in v if not (isinstance(x, float) and np.isnan(x))]
        return float(np.median(v)) if v else float("nan")

    out("-" * 80)
    out("ESTADO por brazo (medianas)")
    out(f"  {'brazo':<14} {'vivas med':>9} {'vivas fin':>9} {'hambr':>5} {'w_A nivel':>9} {'w_A t/t':>8} {'banda>=0.4':>10} {'pc_A':>6} {'pc_A t/t':>8} {'genomas':>8}")
    for arm in ARMS:
        out(f"  {arm:<14} {med(arm, 'vivas_med'):>9.0f} {med(arm, 'vivas_fin'):>9.0f} {med(arm, 'n_h'):>5.0f} {med(arm, 'w_nivel'):>9.3f} "
            f"{med(arm, 'w_razon'):>8.2f} {med(arm, 'banda_nivel'):>10.2f} {med(arm, 'pc_nivel'):>6.2f} {med(arm, 'pc_razon'):>8.2f} {med(arm, 'genomas'):>8.0f}")
    out("")
    out("-" * 80)
    out("PAREADO por semilla contra CONGELADO")
    veredictos = {}
    for arm in [a for a in ARMS if a != "congelado"]:
        pr = [(res[arm][s]["w_razon"], res["congelado"][s]["w_razon"]) for s in SEEDS
              if not np.isnan(res[arm][s]["w_razon"]) and not np.isnan(res["congelado"][s]["w_razon"])]
        pn = [(res[arm][s]["w_nivel"], res["congelado"][s]["w_nivel"]) for s in SEEDS
              if not np.isnan(res[arm][s]["w_nivel"]) and not np.isnan(res["congelado"][s]["w_nivel"])]
        kr = sum(1 for a, b in pr if a > b)
        kn = sum(1 for a, b in pn if a > b)
        ok = len(pr) >= 8 and kr / len(pr) >= 0.75 and signo_p(kr, len(pr)) < 0.05 and len(pn) >= 8 and kn / len(pn) >= 0.75
        veredictos[arm] = ok
        out(f"  {arm:<14} w_A tardio/temprano > congelado en {kr}/{len(pr)} (p signo {signo_p(kr, max(len(pr), 1)):.3f}); "
            f"nivel w_A > congelado en {kn}/{len(pn)}; medianas nivel {np.median([a for a, _ in pn]) if pn else float('nan'):.3f} vs "
            f"{np.median([b for _, b in pn]) if pn else float('nan'):.3f} -> {'ADAPTA' if ok else 'no'}")
        pm = [(res[arm][s]["pc_razon"], res["congelado"][s]["pc_razon"]) for s in SEEDS
              if not np.isnan(res[arm][s]["pc_razon"]) and not np.isnan(res["congelado"][s]["pc_razon"])]
        km = sum(1 for a, b in pm if a < b)
        out(f"  {'':<14} (secundaria) mortalidad per capita t/t < congelado en {km}/{len(pm)} (p signo {signo_p(km, max(len(pm), 1)):.3f})")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if any(veredictos.values()):
        out("=> EVOLUCIONA en " + ", ".join(a for a, v in veredictos.items() if v) + ": el rasgo premiado sube con la herencia de cambios mas que en el congelado.")
    else:
        out("=> NO EVOLUCIONA: con gradiente real, seleccion fuerte y oferta suficiente, la variacion no sube el rasgo en 120000 ticks (camino).")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
