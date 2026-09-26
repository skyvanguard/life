"""
El Útero — réplica de v5 en N semillas: ¿la auto-reparación con memoria es
TÍPICA o un accidente de la seed 13?

v5 (exp_utero_memoria.py) mostró, en UNA semilla (13), que con memoria la cola
post-ablación se sostiene en el régimen maduro (cola/pre 2.05 ON vs 0.10 OFF).
Sus tres agujeros declarados: n=1 semilla, no universal en régimen temprano,
régimen sostenido sigue 1/20. Este experimento ataca el primero con el MISMO
protocolo (`zeta_life.utero.ablacion`, extraído de v5 y testeado contra sus
números) en 40 semillas, memoria ON vs OFF, ablación a t=8000 y t=10000.

Añade el control que a v5 le faltaba: una corrida SIN ablación por (semilla,
memoria), para separar "la ablación mató el motor" de "la novedad decae sola
con el tiempo" (cola/pre < 1 puede ser simple deriva).

VARAS — definidas ANTES de mirar (disciplina de la línea):
  1. Motor vivo al ablar: pre >= PRE_MIN (25 genomas nuevos/tramo de 500 =
     el criterio "sostenido" de v5, 100 en 2000 ticks). Tipicidad a horizonte
     largo = cuántas semillas llegan vivas a t=8000/10000, ON vs OFF.
  2. Vara v5: cola/pre > 1 entre las vivas. ON vs OFF.
  3. Vara nueva (con control): R = cola_ablada / max(cola_sin_ablar, 1).
     R >= R_OK (0.5) = la ablación NO dejó daño permanente => se reparó.
  4. Pareado: entre semillas vivas en AMBAS condiciones, signo de R_ON - R_OFF
     y test de signos binomial bilateral.
VEREDICTO (pre-registrado):
  - REPLICA (típica): n_pareado >= 4, mayoría ON > OFF con p < 0.05, y ON se
    repara (R >= R_OK) en la mayoría de las vivas.
  - NO REPLICA: sólo la 13 (o <= 1 más) se repara ON donde OFF no.
  - INCONCLUSO: n_pareado < 4 — el cuello de botella es la rareza del régimen
    maduro, no la memoria; se reporta la tipicidad y se para ahí.
Manos: PRE_MIN, R_OK, ACTIVE_WIN=200, ventanas de medida (las de v5).

    PYTHONPATH=src python experiments/utero/exp_utero_memoria_semillas.py
"""

from __future__ import annotations

import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import binomtest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zeta_life.utero.ablacion import correr, medir_cola  # noqa: E402

N0 = 16
MAX_N = 256
SEEDS = list(range(40))
ABLATE_ATS = (8000, 10000)
POST = 4000                       # ticks después de ablar (cola llega a +3000)
BASE_TICKS = max(ABLATE_ATS) + POST
PRE_MIN = 25.0
R_OK = 0.5
WORKERS = max(1, min(20, (os.cpu_count() or 4) - 4))

RESULTS = Path(__file__).resolve().parents[2] / "results"
NAME = "utero_memoria_semillas"


def job(args: tuple) -> tuple:
    seed, memoria, ablate_at = args
    ticks = BASE_TICKS if ablate_at is None else ablate_at + POST
    res = correr(seed=seed, memoria=memoria, ticks=ticks, ablate_at=ablate_at,
                 n0=N0, max_n=MAX_N)
    return args, res["novedad"], res["ablated"]


def collect() -> dict:
    jobs = [(s, m, a) for s in SEEDS for m in (True, False)
            for a in (None, *ABLATE_ATS)]
    out: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (key, novedad, ablated) in enumerate(ex.map(job, jobs), 1):
            out[key] = (novedad, ablated)
            if i % 20 == 0:
                print(f"  ... {i}/{len(jobs)} corridas", flush=True)
    return out


def analyse(runs: dict, t_abl: int) -> dict:
    """Por semilla y condición: pre, cola ablada, cola sin ablar, R."""
    rows: dict = {}
    for seed in SEEDS:
        for mem in (True, False):
            base, _ = runs[(seed, mem, None)]
            abl, n_abl = runs[(seed, mem, t_abl)]
            pre, pulse, tail_abl = medir_cola(abl, t_abl)
            _, _, tail_base = medir_cola(base, t_abl)
            rows[(seed, mem)] = dict(
                pre=pre, pulse=pulse, tail=tail_abl, tail_base=tail_base,
                n_abl=n_abl, alive=pre >= PRE_MIN,
                v5=tail_abl / max(pre, 1.0),
                R=tail_abl / max(tail_base, 1.0))
    return rows


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 76)
    out("EL UTERO -- replica de v5 (memoria) en 40 semillas: tipica o solo la 13?")
    out("=" * 76)
    out(f"n0={N0} -> max {MAX_N}  semillas={len(SEEDS)}  ablacion en {ABLATE_ATS}"
        f"  + control sin ablar ({BASE_TICKS} ticks)")
    out(f"varas pre-registradas: PRE_MIN={PRE_MIN:.0f}/tramo  R_OK={R_OK}  "
        f"(ver docstring)  workers={WORKERS}")
    out("")
    runs = collect()
    summary: dict = {}

    for t_abl in ABLATE_ATS:
        rows = analyse(runs, t_abl)
        out("-" * 76)
        out(f"ABLACION EN t={t_abl}")
        out(f"  {'seed':>4} | {'ON: pre':>8} {'abl':>4} {'cola':>6} {'sin':>6} {'R':>6} "
            f"| {'OFF: pre':>8} {'abl':>4} {'cola':>6} {'sin':>6} {'R':>6}")
        alive_on = [s for s in SEEDS if rows[(s, True)]["alive"]]
        alive_off = [s for s in SEEDS if rows[(s, False)]["alive"]]
        reignited = {True: [], False: []}
        for s in SEEDS:
            for mem in (True, False):
                r = rows[(s, mem)]
                if not r["alive"] and r["tail"] >= PRE_MIN:
                    reignited[mem].append(s)
        for s in SEEDS:
            a, b = rows[(s, True)], rows[(s, False)]
            if not (a["alive"] or b["alive"] or s in reignited[True]
                    or s in reignited[False]):
                continue
            out(f"  {s:>4} | {a['pre']:>8.0f} {a['n_abl']:>4} {a['tail']:>6.0f} "
                f"{a['tail_base']:>6.0f} {a['R']:>6.2f} | {b['pre']:>8.0f} "
                f"{b['n_abl']:>4} {b['tail']:>6.0f} {b['tail_base']:>6.0f} "
                f"{b['R']:>6.2f}")
        out("  (abl = celdas vaciadas; semillas muertas en ambas condiciones y")
        out("   sin reencendido omitidas)")
        out("")
        out(f"  1. motor vivo al ablar (pre>={PRE_MIN:.0f}): "
            f"ON {len(alive_on)}/{len(SEEDS)} {alive_on}   "
            f"OFF {len(alive_off)}/{len(SEEDS)} {alive_off}")
        v5_on = [s for s in alive_on if rows[(s, True)]["v5"] > 1.0]
        v5_off = [s for s in alive_off if rows[(s, False)]["v5"] > 1.0]
        out(f"  2. vara v5 (cola/pre>1) entre vivas: ON {len(v5_on)}/{len(alive_on)}"
            f" {v5_on}   OFF {len(v5_off)}/{len(alive_off)} {v5_off}")
        rep_on = [s for s in alive_on if rows[(s, True)]["R"] >= R_OK]
        rep_off = [s for s in alive_off if rows[(s, False)]["R"] >= R_OK]
        out(f"  3. se repara (R>={R_OK}) entre vivas: ON {len(rep_on)}/{len(alive_on)}"
            f" {rep_on}   OFF {len(rep_off)}/{len(alive_off)} {rep_off}")
        paired = [s for s in SEEDS if rows[(s, True)]["alive"]
                  and rows[(s, False)]["alive"]]
        wins = [s for s in paired if rows[(s, True)]["R"] > rows[(s, False)]["R"]]
        ties = [s for s in paired if rows[(s, True)]["R"] == rows[(s, False)]["R"]]
        n_eff = len(paired) - len(ties)
        p = binomtest(len(wins), n_eff, 0.5).pvalue if n_eff > 0 else float("nan")
        out(f"  4. pareado (vivas en ambas): n={len(paired)} {paired}  "
            f"ON>OFF en {len(wins)}  p(signos)={p:.3f}")
        out(f"  5. [POST-HOC, no pre-registrado] REENCENDIDO: motor muerto al ablar "
            f"(pre<{PRE_MIN:.0f}) pero cola>={PRE_MIN:.0f} tras la perturbacion: "
            f"ON {reignited[True]}   OFF {reignited[False]}")
        only_on = [s for s in rep_on if s not in rep_off]
        summary[t_abl] = dict(rows=rows, alive_on=alive_on, alive_off=alive_off,
                              rep_on=rep_on, rep_off=rep_off, paired=paired,
                              wins=wins, p=p, only_on=only_on)
        out("")

    # ---- veredicto pre-registrado (sobre el régimen maduro, ambos tiempos) ----
    out("=" * 76)
    out("VEREDICTO (regla escrita antes de correr)")
    verdicts = []
    for t_abl, S in summary.items():
        n_pair = len(S["paired"])
        maj_rep = len(S["rep_on"]) > len(S["alive_on"]) / 2 if S["alive_on"] else False
        if n_pair < 4:
            v = "INCONCLUSO"
        elif len(S["wins"]) > n_pair / 2 and S["p"] < 0.05 and maj_rep:
            v = "REPLICA"
        elif len(S["only_on"]) <= 2:
            v = "NO REPLICA"
        else:
            v = "PARCIAL"
        verdicts.append(v)
        out(f"  t={t_abl}: {v}  (pareadas={n_pair}, ON>OFF={len(S['wins'])}, "
            f"p={S['p']:.3f}, se reparan solo-ON={S['only_on']})")
    out("")
    if all(v == "INCONCLUSO" for v in verdicts):
        out("=> INCONCLUSO: casi ninguna semilla llega con motor vivo a t>=8000.")
        out("   El cuello de botella NO es la memoria sino la RAREZA del regimen")
        out("   maduro. La afirmacion de v5 queda como n=1: honesta, no tipica.")
    elif all(v == "REPLICA" for v in verdicts):
        out("=> REPLICA: la auto-reparacion con memoria es TIPICA del regimen")
        out("   maduro, no idiosincrasia de la seed 13.")
    elif all(v == "NO REPLICA" for v in verdicts):
        out("=> NO REPLICA: fuera de la seed 13 la memoria no separa la auto-")
        out("   reparacion. v5 fue un accidente de una semilla.")
    else:
        out("=> MIXTO: leer las tablas; el veredicto depende del tiempo de")
        out("   ablacion. No cerrar nada.")

    # ---- figura: R_ON vs R_OFF por semilla, un panel por t_abl ----
    fig, axes = plt.subplots(1, len(ABLATE_ATS), figsize=(11, 5), sharey=True)
    lim = (5e-4, 20)   # los valores fuera de rango se recortan al borde (visibles)
    for ax, (t_abl, S) in zip(np.atleast_1d(axes), summary.items()):
        rows = S["rows"]
        for s in SEEDS:
            a, b = rows[(s, True)], rows[(s, False)]
            if not (a["alive"] or b["alive"]):
                continue
            both = a["alive"] and b["alive"]
            x = float(np.clip(b["R"] + 1e-3, *lim))
            y = float(np.clip(a["R"] + 1e-3, *lim))
            ax.scatter(x, y, s=60 if both else 25, alpha=0.9 if both else 0.5,
                       color="tab:red" if s == 13 else "tab:blue",
                       edgecolor="k" if both else "none")
            ax.annotate(str(s), (x, y), fontsize=7,
                        xytext=(3, 3), textcoords="offset points")
        ax.plot(lim, lim, "k:", lw=0.8)
        ax.axhline(R_OK, color="gray", ls="--", lw=0.8)
        ax.axvline(R_OK, color="gray", ls="--", lw=0.8)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(lim)
        ax.set_ylim(lim)
        ax.set_xlabel("R sin memoria (cola ablada / cola sin ablar)")
        ax.set_title(f"ablación t={t_abl}  (rojo = seed 13, borde = viva en ambas)")
    np.atleast_1d(axes)[0].set_ylabel("R con memoria")
    fig.suptitle("El Útero — réplica de v5 en 40 semillas: ¿se repara con memoria?")
    fig.tight_layout()
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / f"{NAME}.png", dpi=110)
    out("")
    out(f"figura: results/{NAME}.png")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
