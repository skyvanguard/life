"""
§34 — v17b: θ Y ESCALA HEREDABLES. ¿Evoluciona el útero cuando la expresión
de la física en la materia puede atenuarse? (docs/PLAN_INTELIGENCIA.md §34;
ledger 2026-09-27)

MOTIVO. §33: un desplazamiento heredable θ no cambia la distancia media al
sol de una materia pseudoaleatoria (error de diseño registrado). El rasgo
que el gradiente premia (§26) es la DISPERSIÓN: materia quieta y lejos del
sol. Eso choca con la sonda, que exige física sensible. v17b separa la física
de su expresión: la sonda ve la salida cruda; la materia visible es (θ +
s·salida) mod 1 con s ∈ [0, 1] heredable, nacido en 1, perturbado ±ε desde la
materia de la madre. Predicción si la selección medida en §26 actúa sobre
perillas heredables: s cae, θ se concentra frente al sol de la hambruna
(≈ 0.58) y w̄_A sube por encima del nulo.

DISEÑO. Como §33 (N = 512, L0 = 14, 12 semillas, 120000 ticks, ε = 0.05), con
escala activa en los tres brazos: theta_s_abierto (programas con escritura
total p = 0.02 + θ, s heredables), theta_s_solo (programas congelados + θ, s
heredables), nulo (programas congelados, θ y s fijos). Regla de §27 sobre
w̄_A pareado contra el nulo. Secundarias: s̄_A (escala media de las vivas en
A: baja si la atenuación se selecciona), R_θ, banda, mortalidad.
VEREDICTO: EVOLUCIONA si algún brazo heredable ADAPTA → primera evolución
darwiniana medida en el útero, hacia dinámica interna viva con estado externo
estable; se replica con otro sol y la regulación por el orden se pregunta
sobre este sustrato (§35). NO EVOLUCIONA si ninguno.

    PYTHONPATH=src python experiments/utero/exp_utero_escala.py
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
EPS = 0.05
ARMS = {"theta_s_abierto": dict(escritura_total=True, tasa_germinal=0.02, parametros=EPS, escala=True),
        "theta_s_solo": dict(congelado=True, parametros=EPS, escala=True),
        "nulo": dict(congelado=True, parametros=EPS, escala=True, theta_fijo=True)}
TRANSITORIO = 6000
MIN_HAMBRUNAS = 4
BANDA = 0.4
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_escala"


def correr(seed: int, arm: str) -> dict:
    sol = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    u = UteroCreciente(n0=N, seed=seed, max_n=N, germinal=True, toroidal=True, sol=sol, **BASE, **ARMS[arm])
    w = np.full(TICKS, np.nan)
    banda = np.full(TICKS, np.nan)
    conc = np.full(TICKS, np.nan)
    escm = np.full(TICKS, np.nan)
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
            conc[t] = float(abs(np.mean(np.exp(2j * np.pi * u.theta[alive]))))
            escm[t] = float(u.esc[alive].mean())
    wA, pcA, bA, cA, sA = [], [], [], [], []
    for nombre, ini, fin in sol.estaciones:
        if nombre != "A" or ini < TRANSITORIO or fin > TICKS:
            continue
        v = vivas[ini:fin].mean()
        if v <= 0 or np.all(np.isnan(w[ini:fin])):
            continue
        wA.append(float(np.nanmean(w[ini:fin])))
        bA.append(float(np.nanmean(banda[ini:fin])))
        cA.append(float(np.nanmean(conc[ini:fin])))
        sA.append(float(np.nanmean(escm[ini:fin])))
        pcA.append(float(muertes[ini:fin].sum() / v))

    def razon(x):
        h = len(x) // 2
        return float(np.mean(x[h:]) / np.mean(x[:h])) if (h >= MIN_HAMBRUNAS and np.mean(x[:h]) > 0) else float("nan")

    return dict(seed=seed, arm=arm, n_h=len(wA), w_nivel=float(np.mean(wA)) if wA else float("nan"),
                w_razon=razon(wA), pc_nivel=float(np.mean(pcA)) if pcA else float("nan"), pc_razon=razon(pcA),
                banda_nivel=float(np.mean(bA)) if bA else float("nan"),
                conc_nivel=float(np.mean(cA)) if cA else float("nan"), conc_razon=razon(cA),
                esc_nivel=float(np.mean(sA)) if sA else float("nan"), esc_razon=razon(sA),
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
    out("v17b THETA Y ESCALA HEREDABLES -- sube el rasgo premiado cuando la expresion de la fisica puede atenuarse? -- peso de luz de la materia durante la hambruna, variacion abierta vs congelado; cerrado, luz escasa")
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
    out(f"  {'brazo':<14} {'vivas med':>9} {'vivas fin':>9} {'hambr':>5} {'w_A nivel':>9} {'w_A t/t':>8} {'banda>=0.4':>10} {'R_theta':>7} {'R t/t':>6} {'s_A':>5} {'s t/t':>6} {'pc_A':>6} {'pc_A t/t':>8} {'genomas':>8}")
    for arm in ARMS:
        out(f"  {arm:<14} {med(arm, 'vivas_med'):>9.0f} {med(arm, 'vivas_fin'):>9.0f} {med(arm, 'n_h'):>5.0f} {med(arm, 'w_nivel'):>9.3f} "
            f"{med(arm, 'w_razon'):>8.2f} {med(arm, 'banda_nivel'):>10.2f} {med(arm, 'conc_nivel'):>7.2f} {med(arm, 'conc_razon'):>6.2f} {med(arm, 'esc_nivel'):>5.2f} {med(arm, 'esc_razon'):>6.2f} {med(arm, 'pc_nivel'):>6.2f} {med(arm, 'pc_razon'):>8.2f} {med(arm, 'genomas'):>8.0f}")
    out("")
    out("-" * 80)
    out("PAREADO por semilla contra NULO (theta fijo, programas congelados)")
    veredictos = {}
    for arm in [a for a in ARMS if a != "nulo"]:
        pr = [(res[arm][s]["w_razon"], res["nulo"][s]["w_razon"]) for s in SEEDS
              if not np.isnan(res[arm][s]["w_razon"]) and not np.isnan(res["nulo"][s]["w_razon"])]
        pn = [(res[arm][s]["w_nivel"], res["nulo"][s]["w_nivel"]) for s in SEEDS
              if not np.isnan(res[arm][s]["w_nivel"]) and not np.isnan(res["nulo"][s]["w_nivel"])]
        kr = sum(1 for a, b in pr if a > b)
        kn = sum(1 for a, b in pn if a > b)
        ok = len(pr) >= 8 and kr / len(pr) >= 0.75 and signo_p(kr, len(pr)) < 0.05 and len(pn) >= 8 and kn / len(pn) >= 0.75
        veredictos[arm] = ok
        out(f"  {arm:<14} w_A tardio/temprano > nulo en {kr}/{len(pr)} (p signo {signo_p(kr, max(len(pr), 1)):.3f}); "
            f"nivel w_A > nulo en {kn}/{len(pn)}; medianas nivel {np.median([a for a, _ in pn]) if pn else float('nan'):.3f} vs "
            f"{np.median([b for _, b in pn]) if pn else float('nan'):.3f} -> {'ADAPTA' if ok else 'no'}")
        pm = [(res[arm][s]["pc_razon"], res["nulo"][s]["pc_razon"]) for s in SEEDS
              if not np.isnan(res[arm][s]["pc_razon"]) and not np.isnan(res["nulo"][s]["pc_razon"])]
        km = sum(1 for a, b in pm if a < b)
        out(f"  {'':<14} (secundaria) mortalidad per capita t/t < nulo en {km}/{len(pm)} (p signo {signo_p(km, max(len(pm), 1)):.3f})")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if any(veredictos.values()):
        out("=> EVOLUCIONA en " + ", ".join(a for a, v in veredictos.items() if v) + ": con un mapa local, el rasgo premiado sube mas que en el nulo. Primera evolucion darwiniana medida en el utero; replicar con otro sol (§35).")
    else:
        out("=> NO EVOLUCIONA: ni con theta y escala heredables; la seleccion medida en §26 no actua sobre perillas heredables.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
