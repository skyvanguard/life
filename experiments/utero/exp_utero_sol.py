"""
El Útero bajo el sol — ¿hay un vestigio de inteligencia? (docs/PLAN_INTELIGENCIA.md)

Diecinueve experimentos midieron novedad: orden. Ninguna versión tenía mundo.
Aquí el vacío está iluminado por un sol con estructura aprendible (estaciones
A→B→C en orden fijo, duraciones típicas pero impredecibles, un día dentro de
cada estación) y se pregunta, con la definición de Ashby / Conant & Ashby, si
el tejido MODELA su entorno y usa el modelo para seguir siendo.

SUSTRATO: la mejor encarnación 1-D conocida (memoria + invasión asentada,
eq_window=100), 40 semillas, 20000 ticks (~28 estaciones por corrida).
BRAZOS: sol VISIBLE (el vacío lleva la materia del sol) · sol CONSECUENTE
(además `sol_sonda=True`: la sonda de ceguera se referencia a la materia actual
del vacío, así cada estación mata físicas distintas y persistir exige
regularse) · sin sol (vacío frío) · sombra del consecuente (muertes al azar).
Las varas se calculan en los CUATRO brazos con el mismo calendario: en "sin
sol" y "sombra" cualquier "efecto" es la tasa de falsos positivos del método.
Corrida 1 (2026-09-26, sólo sol visible): NADA — el sol era visible pero no
consecuente. Esta corrida agrega el brazo consecuente.

VARAS (pre-registradas; ver `utero/inteligencia.py`):
  R. Regulación: vivas y novedad (maduro) con vs sin sol; amortiguación =
     var(materia interior)/var(sol); acople del borde = corr(materia de borde,
     sol). Negativa si el sol MATA (vivas_sol < 0.5·vivas_sin en mediana).
  A. Anticipación: en estaciones donde el cambio real llegó ≥ 100 ticks después
     del instante esperado (inicio + mediana de duraciones ya vistas), exceso
     de actividad interna en esperado ± 50 vs una ventana anterior de la misma
     estación; nulo por reubicación del instante esperado (500 permutaciones).
     Positiva por semilla: estadístico > 0 y p < 0.05.
  L. Aprendizaje por recurrencia: Spearman(ocurrencia k, respuesta_k) por
     régimen, promediado; nulo por permutación de ocurrencias. Positiva por
     semilla: p < 0.05 (se reporta el signo; negativo = habituación).
VEREDICTO (escrito antes de correr):
  VESTIGIO   si A o L son positivas en ≥ 3/40 semillas de un brazo con sol
             (visible o consecuente) Y ese conteo es ≥ 2× el máximo de los
             brazos control (sin sol, sombra) Y R no es negativa en ese brazo. Además se reporta el p binomial del conteo
             contra la tasa nominal 0.05 (esperado 2/40).
  NADA       si los conteos de sol y controles son indistinguibles.
  SOL MATA   si R es negativa: el entorno destruye el tejido y no hay nada que
             medir; volver al diseño del sol (amplitudes, duraciones).
Si hay VESTIGIO, antes de creerlo: replicar con otro sembrado del sol y con el
orden de estaciones permutado (control siguiente, no este experimento).

    PYTHONPATH=src python experiments/utero/exp_utero_sol.py
"""

from __future__ import annotations

import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.inteligencia import (  # noqa: E402
    W_ANT,
    anticipacion,
    aprendizaje,
    correr_series,
    regulacion,
)
from zeta_life.utero.sol import Sol  # noqa: E402

N0, MAX_N = 16, 256
TICKS = 20000
SEEDS = list(range(40))
SOL_SEED = 0
MATURE = (6000, 20000)
FLAGS = dict(memoria=True, invasion="asentada", eq_window=100)
ALPHA, MIN_SEEDS, RATIO = 0.05, 3, 2.0
WORKERS = max(1, min(20, (os.cpu_count() or 4) - 4))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_sol"


ARMS = ("visible", "consecuente", "sin", "sombra")
SUN_ARMS = ("visible", "consecuente")


def job(seed: int) -> tuple:
    sol = Sol(seed=SOL_SEED, ticks=TICKS)
    vis = correr_series(seed, FLAGS, sol, TICKS, n0=N0, max_n=MAX_N)
    con = correr_series(seed, dict(FLAGS, sol_sonda=True), sol, TICKS, n0=N0, max_n=MAX_N)
    sin = correr_series(seed, FLAGS, None, TICKS, n0=N0, max_n=MAX_N)
    som = correr_series(seed, dict(FLAGS, sol_sonda=True), sol, TICKS,
                        shadow=list(con["muertes"].astype(int)), n0=N0, max_n=MAX_N)
    out = {("R", "visible"): regulacion(vis, sin, sol, MATURE),
           ("R", "consecuente"): regulacion(con, sin, sol, MATURE)}
    for arm, ser in (("visible", vis), ("consecuente", con), ("sin", sin), ("sombra", som)):
        out[("A", arm)] = anticipacion(ser["actividad"], sol, rng_seed=seed)
        out[("L", arm)] = aprendizaje(ser["actividad"], sol, rng_seed=seed)
        out[("act", arm)] = ser["actividad"]
        out[("muertes", arm)] = ser["muertes"]
    out["act_sol"] = con["actividad"]
    out["act_sin"] = sin["actividad"]
    return seed, out


def binom_p(k: int, n: int, p0: float) -> float:
    """P(X >= k) bajo Binomial(n, p0)."""
    return float(sum(math.comb(n, j) * p0 ** j * (1 - p0) ** (n - j) for j in range(k, n + 1)))


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    sol = Sol(seed=SOL_SEED, ticks=TICKS)
    out("=" * 80)
    out("EL UTERO BAJO EL SOL -- hay un vestigio de inteligencia?")
    out("=" * 80)
    out(f"sustrato {FLAGS}, 40 semillas, {TICKS} ticks, sol seed {SOL_SEED}: "
        f"{len(sol.estaciones)} estaciones, duracion tipica {sol.duracion_tipica():.0f}, workers={WORKERS}")
    out("varas y veredicto pre-registrados en el docstring y en docs/PLAN_INTELIGENCIA.md")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (seed, r) in enumerate(ex.map(job, SEEDS), 1):
            res[seed] = r
            if i % 10 == 0:
                print(f"  ... {i}/40 semillas", flush=True)

    # ---- R ----
    out("-" * 80)
    out("R. REGULACION (regimen maduro [6000,20000))  -- por brazo con sol, contra 'sin sol'")
    r_neg = {}
    for arm in SUN_ARMS:
        R = [res[s][("R", arm)] for s in SEEDS]
        viv = np.array([r["vivas_sol"] for r in R])
        viv0 = np.array([r["vivas_sin"] for r in R])
        nov = np.array([r["novedad_sol"] for r in R])
        nov0 = np.array([r["novedad_sin"] for r in R])
        amort = np.array([r["amortiguacion"] for r in R])
        acop = np.array([r["acople_borde"] for r in R])
        muertes = np.array([res[s][("muertes", arm)][MATURE[0]:MATURE[1]].mean() for s in SEEDS])
        r_neg[arm] = np.median(viv) < 0.5 * np.median(viv0)
        out(f"  {arm:<12} vivas med {np.median(viv):.0f} (sin sol {np.median(viv0):.0f}); "
            f"semillas con novedad madura>0: {int((nov > 0).sum())} (sin sol {int((nov0 > 0).sum())}); "
            f"muertes/tick {np.median(muertes):.3f}; amortiguacion {np.nanmedian(amort):.3f}; "
            f"acople borde {np.nanmedian(acop):+.2f} -> R {'NEGATIVA' if r_neg[arm] else 'ok'}")

    # ---- A y L ----
    def conteo(vara: str, arm: str, signo: bool) -> list:
        ss = []
        for s in SEEDS:
            r = res[s][(vara, arm)]
            key = "estadistico" if vara == "A" else "rho"
            if np.isnan(r["p"]):
                continue
            if r["p"] < ALPHA and (r[key] > 0 if signo else True):
                ss.append(s)
        return ss

    CA, CL = {}, {}
    for vara, titulo, key, signo in (
            ("A", "ANTICIPACION (exceso de actividad en el instante esperado)", "estadistico", True),
            ("L", "APRENDIZAJE POR RECURRENCIA (rho ocurrencia vs respuesta)", "rho", False)):
        out("")
        out("-" * 80)
        out(f"{vara}. {titulo}")
        out(f"  {'seed':>4} | " + " | ".join(f"{arm:>12} {'p':>6}" for arm in ARMS))
        for s in SEEDS:
            if np.isnan(res[s][(vara, "visible")]["p"]):
                continue
            cells = [f"{res[s][(vara, arm)][key]:>+12.4f} {res[s][(vara, arm)]['p']:>6.3f}" for arm in ARMS]
            out(f"  {s:>4} | " + " | ".join(cells))
        n_eval = sum(1 for s in SEEDS if not np.isnan(res[s][(vara, "visible")]["p"]))
        C = {arm: conteo(vara, arm, signo) for arm in ARMS}
        out("  positivas (p<0.05" + (", stat>0" if signo else "") + "): "
            + "  |  ".join(f"{arm} {len(C[arm])}" for arm in ARMS)
            + f"  |  p binomial vs 0.05 (n={n_eval}): visible {binom_p(len(C['visible']), n_eval, ALPHA):.3f}, "
              f"consecuente {binom_p(len(C['consecuente']), n_eval, ALPHA):.3f}")
        out(f"  semillas: visible {C['visible']}  consecuente {C['consecuente']}  sin {C['sin']}  sombra {C['sombra']}")
        if vara == "L":
            hab = {arm: [s for s in C[arm] if res[s][("L", arm)]["rho"] < 0] for arm in SUN_ARMS}
            out(f"  habituacion (rho<0): visible {hab['visible']}  consecuente {hab['consecuente']}")
            CL = C
        else:
            CA = C

    # ---- veredicto ----
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    ctrl_A = max(len(CA["sin"]), len(CA["sombra"]))
    ctrl_L = max(len(CL["sin"]), len(CL["sombra"]))
    v = "NADA"
    detalle = []
    for arm in SUN_ARMS:
        va = len(CA[arm]) >= MIN_SEEDS and len(CA[arm]) >= RATIO * max(ctrl_A, 1)
        vl = len(CL[arm]) >= MIN_SEEDS and len(CL[arm]) >= RATIO * max(ctrl_L, 1)
        if r_neg[arm]:
            detalle.append(f"{arm}: SOL MATA")
            continue
        if va or vl:
            v = "VESTIGIO"
            detalle.append(f"{arm}: vestigio" + (" A" if va else "") + (" L" if vl else ""))
        else:
            detalle.append(f"{arm}: nada (A {len(CA[arm])} vs ctrl {ctrl_A}; L {len(CL[arm])} vs ctrl {ctrl_L})")
    if all(r_neg[a] for a in SUN_ARMS):
        v = "SOL MATA"
    out(f"=> {v}: " + "; ".join(detalle))
    if v == "VESTIGIO":
        out("   ANTES DE CREERLO: replicar con otro sembrado del sol y con el orden de estaciones permutado.")
    for s in SEEDS:                       # la figura usa el brazo consecuente como 'sol'
        res[s][("A", "sol")] = res[s][("A", "consecuente")]
        res[s][("L", "sol")] = res[s][("L", "consecuente")]

    # ---- figura: promedio alineado al instante esperado (sol vs sin), y p-values ----
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    ax = axes[0]
    est = sol.estaciones[:-1]
    eventos = []
    for k, (_, ini, fin) in enumerate(est):
        if k < 5:
            continue
        med = np.median([f - i for _, i, f in est[:k]])
        esp = ini + int(med)
        if fin - esp >= 2 * W_ANT:
            eventos.append(esp)
    span = np.arange(-200, 100)
    for arm, col in (("act_sol", "tab:red"), ("act_sin", "gray")):
        curvas = []
        for s in SEEDS:
            a = res[s][arm]
            for esp in eventos:
                seg = a[esp - 200:esp + 100]
                if len(seg) == 300 and seg.std() > 0:
                    curvas.append((seg - seg[:100].mean()) / (seg[:100].std() + 1e-9))
        if curvas:
            ax.plot(span, np.mean(curvas, axis=0), color=col, label=f"{'con sol' if arm == 'act_sol' else 'sin sol'} (n={len(curvas)})")
    ax.axvline(0, color="k", ls=":", lw=0.8)
    ax.axvspan(-W_ANT, W_ANT, color="tab:blue", alpha=0.08)
    ax.set_xlabel("ticks respecto del instante ESPERADO del cambio (que no ocurrió)")
    ax.set_ylabel("actividad (z respecto de -200..-100)")
    ax.set_title("A: promedio alineado (consecuente vs sin sol)")
    ax.legend(fontsize=8)
    ax = axes[1]
    for arm, col in (("sol", "tab:red"), ("sin", "gray"), ("sombra", "tab:orange")):
        ps = [res[s][("A", arm)]["p"] for s in SEEDS if not np.isnan(res[s][("A", arm)]["p"])]
        ax.hist(ps, bins=np.linspace(0, 1, 11), histtype="step", color=col, label=arm, lw=1.5)
    ax.axvline(ALPHA, color="k", ls=":", lw=0.8)
    ax.set_xlabel("p de anticipación por semilla")
    ax.set_title("A: p-values (uniforme = nada)")
    ax.legend(fontsize=8)
    ax = axes[2]
    for arm, col in (("sol", "tab:red"), ("sin", "gray"), ("sombra", "tab:orange")):
        xs = [res[s][("L", arm)]["rho"] for s in SEEDS if not np.isnan(res[s][("L", arm)]["p"])]
        ys = [res[s][("L", arm)]["p"] for s in SEEDS if not np.isnan(res[s][("L", arm)]["p"])]
        ax.scatter(xs, ys, s=14, color=col, label=arm, alpha=0.8)
    ax.axhline(ALPHA, color="k", ls=":", lw=0.8)
    ax.set_xlabel("rho (ocurrencia vs respuesta)")
    ax.set_ylabel("p")
    ax.set_title("L: aprendizaje por recurrencia")
    ax.legend(fontsize=8)
    fig.suptitle("El Útero bajo el sol — varas de inteligencia contra sus controles")
    fig.tight_layout()
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / f"{NAME}.png", dpi=110)
    out("")
    out(f"figura: results/{NAME}.png")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
