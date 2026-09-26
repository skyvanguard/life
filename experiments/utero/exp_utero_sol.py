"""
El Útero bajo el sol — ¿hay un vestigio de inteligencia? (docs/PLAN_INTELIGENCIA.md)

Diecinueve experimentos midieron novedad: orden. Ninguna versión tenía mundo.
Aquí el vacío está iluminado por un sol con estructura aprendible (estaciones
A→B→C en orden fijo, duraciones típicas pero impredecibles, un día dentro de
cada estación) y se pregunta, con la definición de Ashby / Conant & Ashby, si
el tejido MODELA su entorno y usa el modelo para seguir siendo.

SUSTRATO: la mejor encarnación 1-D conocida (memoria + invasión asentada,
eq_window=100), 40 semillas, 20000 ticks (~28 estaciones por corrida).
BRAZOS: sol · sin sol (mismo tejido, vacío frío) · sombra (sol + muertes al
azar en vez de sonda). Las varas se calculan en los TRES brazos con el mismo
calendario del sol: en "sin sol" y "sombra" cualquier "efecto" es la tasa de
falsos positivos del método.

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
  VESTIGIO   si A o L son positivas en ≥ 3/40 semillas del brazo sol Y ese
             conteo es ≥ 2× el máximo de los brazos control (sin sol, sombra)
             Y R no es negativa. Además se reporta el p binomial del conteo
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


def job(seed: int) -> tuple:
    sol = Sol(seed=SOL_SEED, ticks=TICKS)
    con = correr_series(seed, FLAGS, sol, TICKS, n0=N0, max_n=MAX_N)
    sin = correr_series(seed, FLAGS, None, TICKS, n0=N0, max_n=MAX_N)
    som = correr_series(seed, FLAGS, sol, TICKS, shadow=list(con["muertes"].astype(int)),
                        n0=N0, max_n=MAX_N)
    out = {"R": regulacion(con, sin, sol, MATURE)}
    for arm, ser in (("sol", con), ("sin", sin), ("sombra", som)):
        out[("A", arm)] = anticipacion(ser["actividad"], sol, rng_seed=seed)
        out[("L", arm)] = aprendizaje(ser["actividad"], sol, rng_seed=seed)
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
    out("R. REGULACION (regimen maduro [6000,20000))")
    viv_sol = np.array([res[s]["R"]["vivas_sol"] for s in SEEDS])
    viv_sin = np.array([res[s]["R"]["vivas_sin"] for s in SEEDS])
    nov_sol = np.array([res[s]["R"]["novedad_sol"] for s in SEEDS])
    nov_sin = np.array([res[s]["R"]["novedad_sin"] for s in SEEDS])
    amort = np.array([res[s]["R"]["amortiguacion"] for s in SEEDS])
    acop = np.array([res[s]["R"]["acople_borde"] for s in SEEDS])
    out(f"  vivas mediana: sol {np.median(viv_sol):.0f}  sin sol {np.median(viv_sin):.0f}")
    out(f"  novedad total maduro (mediana): sol {np.median(nov_sol):.0f}  sin sol {np.median(nov_sin):.0f}; "
        f"semillas con novedad>0: sol {int((nov_sol > 0).sum())}, sin {int((nov_sin > 0).sum())}")
    out(f"  amortiguacion var(interior)/var(sol): mediana {np.nanmedian(amort):.3f}  "
        f"(1 = el interior copia al sol; <<1 = lo amortigua)")
    out(f"  acople del borde corr(v_borde, sol): mediana {np.nanmedian(acop):+.2f}")
    r_neg = np.median(viv_sol) < 0.5 * np.median(viv_sin)
    out(f"  -> R {'NEGATIVA: el sol mata' if r_neg else 'no negativa'}")

    # ---- A y L ----
    def conteo(vara: str, arm: str, signo: bool) -> tuple:
        ss = []
        for s in SEEDS:
            r = res[s][(vara, arm)]
            key = "estadistico" if vara == "A" else "rho"
            if np.isnan(r["p"]):
                continue
            if r["p"] < ALPHA and (r[key] > 0 if signo else True):
                ss.append(s)
        return ss

    out("")
    out("-" * 80)
    out("A. ANTICIPACION (exceso de actividad en el instante esperado, estaciones largas)")
    out(f"  {'seed':>4} | {'sol: n':>6} {'stat':>8} {'p':>6} | {'sin: stat':>9} {'p':>6} | {'sombra: stat':>12} {'p':>6}")
    for s in SEEDS:
        a, b, c = res[s][("A", "sol")], res[s][("A", "sin")], res[s][("A", "sombra")]
        if np.isnan(a["p"]):
            continue
        out(f"  {s:>4} | {a['n']:>6} {a['estadistico']:>+8.4f} {a['p']:>6.3f} | {b['estadistico']:>+9.4f} {b['p']:>6.3f} "
            f"| {c['estadistico']:>+12.4f} {c['p']:>6.3f}")
    A = {arm: conteo("A", arm, True) for arm in ("sol", "sin", "sombra")}
    n_eval = sum(1 for s in SEEDS if not np.isnan(res[s][("A", "sol")]["p"]))
    out(f"  positivas (stat>0, p<{ALPHA}): sol {len(A['sol'])}/{n_eval} {A['sol']}  |  sin {len(A['sin'])}  |  sombra {len(A['sombra'])}"
        f"  |  p binomial del conteo sol vs 0.05: {binom_p(len(A['sol']), n_eval, ALPHA):.3f}")

    out("")
    out("-" * 80)
    out("L. APRENDIZAJE POR RECURRENCIA (Spearman ocurrencia vs respuesta; negativo = habituacion)")
    out(f"  {'seed':>4} | {'sol: rho':>8} {'p':>6} | {'sin: rho':>8} {'p':>6} | {'sombra: rho':>11} {'p':>6}")
    for s in SEEDS:
        a, b, c = res[s][("L", "sol")], res[s][("L", "sin")], res[s][("L", "sombra")]
        if np.isnan(a["p"]):
            continue
        out(f"  {s:>4} | {a['rho']:>+8.2f} {a['p']:>6.3f} | {b['rho']:>+8.2f} {b['p']:>6.3f} | {c['rho']:>+11.2f} {c['p']:>6.3f}")
    L = {arm: conteo("L", arm, False) for arm in ("sol", "sin", "sombra")}
    n_eval_l = sum(1 for s in SEEDS if not np.isnan(res[s][("L", "sol")]["p"]))
    hab = [s for s in L["sol"] if res[s][("L", "sol")]["rho"] < 0]
    out(f"  significativas (p<{ALPHA}): sol {len(L['sol'])}/{n_eval_l} {L['sol']} (habituacion {hab})  |  "
        f"sin {len(L['sin'])}  |  sombra {len(L['sombra'])}  |  p binomial sol: {binom_p(len(L['sol']), n_eval_l, ALPHA):.3f}")

    # ---- veredicto ----
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    ctrl_A = max(len(A["sin"]), len(A["sombra"]))
    ctrl_L = max(len(L["sin"]), len(L["sombra"]))
    vest_A = len(A["sol"]) >= MIN_SEEDS and len(A["sol"]) >= RATIO * max(ctrl_A, 1)
    vest_L = len(L["sol"]) >= MIN_SEEDS and len(L["sol"]) >= RATIO * max(ctrl_L, 1)
    if r_neg:
        v = "SOL MATA"
    elif vest_A or vest_L:
        v = "VESTIGIO" + (" (A)" if vest_A else "") + (" (L)" if vest_L else "")
    else:
        v = "NADA"
    out(f"=> {v}: A sol {len(A['sol'])} vs control {ctrl_A}; L sol {len(L['sol'])} vs control {ctrl_L}; "
        f"R {'negativa' if r_neg else 'ok'}")
    if v.startswith("VESTIGIO"):
        out("   ANTES DE CREERLO: replicar con otro sembrado del sol y con el orden de estaciones permutado.")

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
    ax.set_title("A: promedio alineado, estaciones largas")
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
