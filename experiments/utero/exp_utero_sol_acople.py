"""
El Útero bajo un sol que CALIENTA — ¿hay un vestigio de inteligencia?
(docs/PLAN_INTELIGENCIA.md; tercera corrida del programa del sol)

Corrida 1 (sol visible): NADA. Corrida 2 (+ sol consecuente para la sonda):
el diagnóstico estacional mostró actividad PLANA alrededor de los inicios de
estación en todos los brazos y una superficie que no sigue al sol (v_borde
constante): el tejido apenas siente el clima, y sin sentirlo no hay nada que
regular ni anticipar. Este experimento usa `sol_acople=κ`: el sol calienta la
superficie (v ← (1−κ)·v' + κ·sol(t) en las celdas que lindan con el vacío).
Acople físico, no lectura opcional. Mano declarada: κ (se barre en el control
si hay señal).

BRAZOS (configurables en ARMS): calor (κ=0.5) · calor+sonda (κ=0.5 +
sol_sonda) · sin sol · sombra del primer brazo con sol. Las varas se calculan
en todos con el mismo calendario: en "sin" y "sombra" cualquier "efecto" es la
tasa de falsos positivos del método.

VARAS Y VEREDICTO: idénticos a `exp_utero_sol.py` (pre-registrados en
`docs/PLAN_INTELIGENCIA.md`): VESTIGIO si A o L son positivas en ≥ 3/40
semillas de un brazo con sol Y ≥ 2× el máximo de los controles Y R no
negativa; NADA si indistinguible; SOL MATA si vivas < 0.5 × sin sol.
Además, diagnóstico estacional pre-registrado como CONDICIÓN NECESARIA: si
las MUERTES no cambian al inicio de estación (post/pre < 1.2 en mediana), el
tejido no siente el clima y el resultado se lee como "sin contacto", no como
"sin inteligencia".

SERIES (declarado antes de correr los 40): las varas A y L se calculan sobre
DOS series por brazo: `actividad` (la primaria del plan) y `muertes` (agregada
tras un diagnóstico de contacto en 3 semillas —13, 35, 21— que mostró que las
reescrituras de la bomba, ~0.4 por celda-tick, tapan la respuesta estacional,
mientras las muertes suben 3–16× al inicio de estación con κ=0.5). Con dos
series el umbral por brazo se mantiene (≥ 3/40 y ≥ 2× control) y se reporta
cada serie por separado; no se combinan p-values.

    PYTHONPATH=src python experiments/utero/exp_utero_sol_acople.py
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
BASE = dict(memoria=True, invasion="asentada", eq_window=100)
KAPPA = 0.5
ARMS = {"calor": dict(sol_acople=KAPPA),
        "calor+sonda": dict(sol_acople=KAPPA, sol_sonda=True)}
ALPHA, MIN_SEEDS, RATIO, CONTACTO = 0.05, 3, 2.0, 1.2
WORKERS = max(1, min(10, (os.cpu_count() or 4) // 2))   # 4 corridas por semilla: la mitad de obreros
RESULTS = HERE.parents[1] / "results"
NAME = "utero_sol_acople"


def job(seed: int) -> tuple:
    sol = Sol(seed=SOL_SEED, ticks=TICKS)
    series = {arm: correr_series(seed, dict(BASE, **fl), sol, TICKS, n0=N0, max_n=MAX_N)
              for arm, fl in ARMS.items()}
    series["sin"] = correr_series(seed, BASE, None, TICKS, n0=N0, max_n=MAX_N)
    first = next(iter(ARMS))
    series["sombra"] = correr_series(seed, dict(BASE, **ARMS[first]), sol, TICKS,
                                     shadow=list(series[first]["muertes"].astype(int)),
                                     n0=N0, max_n=MAX_N)
    out = {}
    for arm, ser in series.items():
        if arm in ARMS:
            out[("R", arm)] = regulacion(ser, series["sin"], sol, MATURE)
        for tag, serie in (("", ser["actividad"]), ("_m", ser["muertes"])):
            out[("A" + tag, arm)] = anticipacion(serie, sol, rng_seed=seed)
            out[("L" + tag, arm)] = aprendizaje(serie, sol, rng_seed=seed)
        out[("act", arm)] = ser["actividad"]
        out[("muertes", arm)] = ser["muertes"]
        out[("vborde", arm)] = ser["v_borde"]
    return seed, out


def binom_p(k: int, n: int, p0: float) -> float:
    return float(sum(math.comb(n, j) * p0 ** j * (1 - p0) ** (n - j) for j in range(k, n + 1)))


def contacto(act: np.ndarray, sol: Sol) -> float:
    """post/pre de la actividad alrededor de los inicios de estación (mediana)."""
    ratios = []
    for _, ini, _ in sol.estaciones[1:-1]:
        if ini - 100 >= 0 and ini + 100 <= len(act):
            pre, post = act[ini - 100:ini].mean(), act[ini:ini + 100].mean()
            if pre > 0:
                ratios.append(post / pre)
    return float(np.median(ratios)) if ratios else float("nan")


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    sol = Sol(seed=SOL_SEED, ticks=TICKS)
    todos = list(ARMS) + ["sin", "sombra"]
    out("=" * 80)
    out("EL UTERO BAJO UN SOL QUE CALIENTA -- hay un vestigio de inteligencia?")
    out("=" * 80)
    out(f"base {BASE}; brazos {ARMS}; 40 semillas; {TICKS} ticks; sol seed {SOL_SEED}: "
        f"{len(sol.estaciones)} estaciones, tipica {sol.duracion_tipica():.0f}; workers={WORKERS}")
    out("varas y veredicto pre-registrados (docstring, docs/PLAN_INTELIGENCIA.md)")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (seed, r) in enumerate(ex.map(job, SEEDS), 1):
            res[seed] = r
            if i % 10 == 0:
                print(f"  ... {i}/40 semillas", flush=True)

    # ---- contacto (condición necesaria) ----
    out("-" * 80)
    out("CONTACTO: muertes post/pre al inicio de estacion (mediana sobre semillas); acople del borde")
    cont = {}
    for arm in todos:
        c = np.array([contacto(res[s][("muertes", arm)], sol) for s in SEEDS])
        cont[arm] = float(np.nanmedian(c))
        vb = []
        for s in SEEDS:
            v = res[s][("vborde", arm)][MATURE[0]:MATURE[1]]
            ok = ~np.isnan(v)
            ss = sol.serie[MATURE[0]:MATURE[1]][ok]
            vb.append(np.corrcoef(v[ok], ss)[0, 1] if ok.sum() > 10 and v[ok].std() > 0 else np.nan)
        out(f"  {arm:<12} post/pre {cont[arm]:.3f}   corr(v_borde, sol) mediana {np.nanmedian(vb):+.2f}")
    sienten = [arm for arm in ARMS if cont[arm] >= CONTACTO]
    out(f"  -> brazos que SIENTEN el clima (post/pre >= {CONTACTO}): {sienten if sienten else 'ninguno'}")

    # ---- R ----
    out("")
    out("-" * 80)
    out("R. REGULACION (maduro) -- por brazo con sol, contra 'sin sol'")
    r_neg = {}
    for arm in ARMS:
        R = [res[s][("R", arm)] for s in SEEDS]
        viv = np.array([r["vivas_sol"] for r in R])
        viv0 = np.array([r["vivas_sin"] for r in R])
        nov = np.array([r["novedad_sol"] for r in R])
        nov0 = np.array([r["novedad_sin"] for r in R])
        amort = np.array([r["amortiguacion"] for r in R])
        muertes = np.array([res[s][("muertes", arm)][MATURE[0]:MATURE[1]].mean() for s in SEEDS])
        r_neg[arm] = np.median(viv) < 0.5 * np.median(viv0)
        out(f"  {arm:<12} vivas med {np.median(viv):.0f} (sin sol {np.median(viv0):.0f}); "
            f"novedad madura>0: {int((nov > 0).sum())} semillas (sin sol {int((nov0 > 0).sum())}); "
            f"muertes/tick {np.median(muertes):.3f}; amortiguacion {np.nanmedian(amort):.3f} "
            f"-> R {'NEGATIVA' if r_neg[arm] else 'ok'}")

    # ---- A y L ----
    def conteo(vara: str, arm: str, signo: bool) -> list:
        key = "estadistico" if vara.startswith("A") else "rho"
        return [s for s in SEEDS if not np.isnan(res[s][(vara, arm)]["p"])
                and res[s][(vara, arm)]["p"] < ALPHA and (res[s][(vara, arm)][key] > 0 or not signo)]

    C = {}
    for vara, titulo, key, signo in (
            ("A", "ANTICIPACION sobre ACTIVIDAD (exceso en el instante esperado)", "estadistico", True),
            ("A_m", "ANTICIPACION sobre MUERTES", "estadistico", True),
            ("L", "APRENDIZAJE POR RECURRENCIA sobre ACTIVIDAD (rho ocurrencia vs respuesta)", "rho", False),
            ("L_m", "APRENDIZAJE POR RECURRENCIA sobre MUERTES", "rho", False)):
        out("")
        out("-" * 80)
        out(f"{vara}. {titulo}")
        out(f"  {'seed':>4} | " + " | ".join(f"{arm:>12} {'p':>6}" for arm in todos))
        for s in SEEDS:
            if all(np.isnan(res[s][(vara, arm)]["p"]) for arm in todos):
                continue
            out(f"  {s:>4} | " + " | ".join(
                f"{res[s][(vara, arm)][key]:>+12.4f} {res[s][(vara, arm)]['p']:>6.3f}" for arm in todos))
        n_eval = sum(1 for s in SEEDS if not np.isnan(res[s][(vara, todos[0])]["p"]))
        C[vara] = {arm: conteo(vara, arm, signo) for arm in todos}
        out("  positivas (p<0.05" + (", stat>0" if signo else "") + "): "
            + "  |  ".join(f"{arm} {len(C[vara][arm])}" for arm in todos)
            + f"  |  p binomial vs 0.05 (n={n_eval}): "
            + ", ".join(f"{arm} {binom_p(len(C[vara][arm]), n_eval, ALPHA):.3f}" for arm in ARMS))
        out("  semillas: " + "  ".join(f"{arm} {C[vara][arm]}" for arm in todos))
        if vara.startswith("L"):
            out("  habituacion (rho<0): " + "  ".join(
                f"{arm} {[s for s in C[vara][arm] if res[s][(vara, arm)]['rho'] < 0]}" for arm in ARMS))

    # ---- veredicto ----
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    varas = ("A", "A_m", "L", "L_m")
    ctrl = {v: max(len(C[v]["sin"]), len(C[v]["sombra"])) for v in varas}
    v = "NADA"
    detalle = []
    for arm in ARMS:
        if r_neg[arm]:
            detalle.append(f"{arm}: SOL MATA")
            continue
        if cont[arm] < CONTACTO:
            detalle.append(f"{arm}: SIN CONTACTO (post/pre {cont[arm]:.2f}) -- no se lee como 'sin inteligencia'")
        pos = [vv for vv in varas if len(C[vv][arm]) >= MIN_SEEDS and len(C[vv][arm]) >= RATIO * max(ctrl[vv], 1)]
        if pos:
            v = "VESTIGIO"
            detalle.append(f"{arm}: vestigio en {pos}")
        else:
            detalle.append(f"{arm}: nada (" + "; ".join(f"{vv} {len(C[vv][arm])} vs ctrl {ctrl[vv]}" for vv in varas) + ")")
    if all(r_neg[a] for a in ARMS):
        v = "SOL MATA"
    out(f"=> {v}: " + "; ".join(detalle))
    if v == "VESTIGIO":
        out("   ANTES DE CREERLO: replicar con otro sembrado del sol, orden de estaciones permutado y barrido de kappa.")

    # ---- figura ----
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    ax = axes[0]
    span = np.arange(-100, 300)
    for arm, col in zip(todos, ("tab:red", "tab:purple", "gray", "tab:orange")):
        curvas = []
        for s in SEEDS:
            a = res[s][("act", arm)]
            for _, ini, _ in sol.estaciones[1:-1]:
                seg = a[ini - 100:ini + 300]
                if len(seg) == 400 and seg[:100].std() > 0:
                    curvas.append((seg - seg[:100].mean()) / seg[:100].std())
        if curvas:
            ax.plot(span, np.mean(curvas, axis=0), color=col, label=f"{arm} (n={len(curvas)})")
    ax.axvline(0, color="k", ls=":", lw=0.8)
    ax.set_xlabel("ticks desde el inicio de estación")
    ax.set_ylabel("actividad (z respecto de -100..0)")
    ax.set_title("contacto: respuesta al inicio de estación")
    ax.legend(fontsize=7)
    ax = axes[1]
    est = sol.estaciones[:-1]
    eventos = []
    for k, (_, ini, fin) in enumerate(est):
        if k < 5:
            continue
        med = np.median([f - i for _, i, f in est[:k]])
        esp = ini + int(med)
        if fin - esp >= 2 * W_ANT:
            eventos.append(esp)
    span2 = np.arange(-200, 100)
    for arm, col in zip(todos, ("tab:red", "tab:purple", "gray", "tab:orange")):
        curvas = []
        for s in SEEDS:
            a = res[s][("act", arm)]
            for esp in eventos:
                seg = a[esp - 200:esp + 100]
                if len(seg) == 300 and seg[:100].std() > 0:
                    curvas.append((seg - seg[:100].mean()) / seg[:100].std())
        if curvas:
            ax.plot(span2, np.mean(curvas, axis=0), color=col, label=arm)
    ax.axvline(0, color="k", ls=":", lw=0.8)
    ax.axvspan(-W_ANT, W_ANT, color="tab:blue", alpha=0.08)
    ax.set_xlabel("ticks respecto del instante ESPERADO (que no ocurrió)")
    ax.set_title("A: promedio alineado, estaciones largas")
    ax.legend(fontsize=7)
    ax = axes[2]
    for arm, col in zip(todos, ("tab:red", "tab:purple", "gray", "tab:orange")):
        xs = [res[s][("L", arm)]["rho"] for s in SEEDS if not np.isnan(res[s][("L", arm)]["p"])]
        ys = [res[s][("L", arm)]["p"] for s in SEEDS if not np.isnan(res[s][("L", arm)]["p"])]
        ax.scatter(xs, ys, s=14, color=col, label=arm, alpha=0.8)
    ax.axhline(ALPHA, color="k", ls=":", lw=0.8)
    ax.set_xlabel("rho (ocurrencia vs respuesta)")
    ax.set_ylabel("p")
    ax.set_title("L: aprendizaje por recurrencia")
    ax.legend(fontsize=7)
    fig.suptitle("El Útero bajo un sol que calienta — varas de inteligencia contra sus controles")
    fig.tight_layout()
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / f"{NAME}.png", dpi=110)
    out("")
    out(f"figura: results/{NAME}.png")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
