"""
El Útero — v8: el PLANO. ¿Dos dimensiones vuelven típica la novedad sostenida?

La línea 1-D quedó cerrada como sustrato donde la novedad sostenida es
posible pero rara: ~5% de las semillas (n=120), insensible al tamaño del
mundo, con tres mecanismos (memoria, invasión, recombinación) que no mueven
el techo y una última jaula nombrada —el barrido del clon viable— que la
literatura resuelve con estructura espacial, no con filtros. `UteroPlano`
(`utero/plano.py`) es el mismo sustrato con vecindario de von Neumann: placa
32×32 con bordes, bloque vivo inicial de 8×8 en el centro (elegido porque con
él la placa SE COLONIZA —250 a 800 vivas—, juzgado por vivas, no por
novedad), vacío colonizable, materia toroidal, sonda, asincronía, y los flags
memoria / invasión / recombinación heredados.

BRAZOS (40 semillas, 14000 ticks): p5 (memoria) · p6 (memoria + invasión
asentada-100) · p67 (p6 + recombinación). Sombra para las candidatas;
ablación de la bomba en t=8000 en las sostenidas (hasta 6 por brazo).
VARAS — escritas ANTES de mirar (idénticas a la línea 1-D):
  1. Tipicidad filtrada: ≥ 5 genomas persistentes/tramo (linaje 500) en
     [8000,12000) y ≥ 2× su sombra. TÍPICA = ≥ 8/40. Referencias 1-D a 1024
     celdas (mismo tamaño): v5 2/40, v6 4/40; a n=120: v5 4,2%, v6 5,8%.
  2. Ecología mediana ≥ 2 bits en las sostenidas (monocultura = < 1 bit).
  3. Auto-reparación (R ≥ 0.5) en ≥ la mitad de las sostenidas abladas.
  4. Anti-ilusión: la novedad cruda en 2-D es enorme (decenas de miles de
     genomas en 3000 ticks en el sondeo); lo que cuenta es la FILTRADA y su
     razón contra la sombra. Se reporta filtrada/cruda.
VEREDICTO (pre-registrado):
  LA PERSPECTIVA PAGA  si algún brazo es TÍPICO (≥ 8/40) con ecología ≥ 2
                       bits y auto-reparación ≥ mitad.
  MEJORA               si algún brazo supera ≥ 2× a su referencia 1-D de 1024
                       (p5 > 4, p6/p67 > 8 se solapa con TÍPICA) con ecología
                       ≥ 2 bits, sin llegar a típico.
  TRAMPA               si la tipicidad sube pero la ecología < 1 bit o la
                       filtrada/cruda < 0.05 (churn sin persistencia).
  SIN EFECTO           si ningún brazo supera su referencia 1-D.

    PYTHONPATH=src python experiments/utero/exp_utero_plano.py
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.ablacion import correr as correr_ablacion  # noqa: E402
from zeta_life.utero.ablacion import medir_cola  # noqa: E402
from zeta_life.utero.medidas import correr_medido, media_ventana, por_tramo  # noqa: E402
from zeta_life.utero.plano import UteroPlano  # noqa: E402

H = W = 32
BLOQUE = 8
TICKS = 14000
TRANCHE = 500
SEEDS = list(range(40))
T_FILTRO = 500
MATURE = (8000, 12000)
FILT_MIN, SHADOW_X, R_OK = 5.0, 2.0, 0.5
TIPICA, ECO_OK, ECO_BAD, CHURN = 8, 2.0, 1.0, 0.05
T_ABL, POST, MAX_ABL = 8000, 4000, 6
ARMS = {"p5": dict(memoria=True),
        "p6": dict(memoria=True, invasion="asentada", eq_window=100),
        "p67": dict(memoria=True, invasion="asentada", eq_window=100, recombina=True)}
REF_1D_1024 = {"p5": 2, "p6": 4, "p67": 4}
WORKERS = max(1, min(10, (os.cpu_count() or 4) // 2))   # 2-D pesa: la mitad de obreros
RESULTS = HERE.parents[1] / "results"
NAME = "utero_plano"


def fabrica(seed: int, shadow, **flags) -> UteroPlano:
    return UteroPlano(h=H, w=W, seed=seed, bloque=BLOQUE, log_events=True,
                      shadow_deaths=shadow, **flags)


def job(args: tuple) -> tuple:
    arm, seed, shadow = args
    r = correr_medido(seed, ARMS[arm], ticks=TICKS, tranche=TRANCHE, t_filtro=T_FILTRO,
                      shadow=shadow, fabrica=fabrica)
    return arm, seed, r


def job_abl(args: tuple) -> tuple:
    arm, seed = args
    flags = dict(ARMS[arm])
    memoria = flags.pop("memoria")
    r = correr_ablacion(seed=seed, memoria=memoria, ticks=T_ABL + POST, ablate_at=T_ABL,
                        fabrica=fabrica, **flags)
    return arm, seed, r["novedad"], r["ablated"]


def resumen(r: dict) -> dict:
    a, b = MATURE[0] // TRANCHE, MATURE[1] // TRANCHE
    raw = media_ventana(por_tramo(r["raw"], TRANCHE), MATURE, TRANCHE)
    filt = media_ventana(r["filt"], MATURE, TRANCHE)
    return dict(raw=raw, filt=filt, ratio=filt / raw if raw else float("nan"),
                eco=media_ventana(r["eco"], MATURE, TRANCHE),
                share=media_ventana(r["share"], MATURE, TRANCHE),
                vivas=int(r["vivas"][-1]), inv=float(r["invaded"][MATURE[0]:MATURE[1]].mean()),
                parto=float(r["causa"][a:b, 0].sum() / max(r["causa"][a:b].sum(), 1)))


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("EL UTERO -- v8: el PLANO (32x32, bloque 8x8, von Neumann)")
    out("=" * 80)
    out(f"brazos {list(ARMS)}, 40 semillas, {TICKS} ticks, linaje {T_FILTRO}, maduro {MATURE}, "
        f"workers={WORKERS}")
    out("varas y veredicto pre-registrados en el docstring")
    out("")
    real: dict = {arm: {} for arm in ARMS}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        jobs = [(arm, s, None) for arm in ARMS for s in SEEDS]
        for i, (arm, seed, r) in enumerate(ex.map(job, jobs), 1):
            real[arm][seed] = r
            if i % 20 == 0:
                print(f"  ... {i}/{len(jobs)} corridas reales", flush=True)
        R = {arm: {s: resumen(real[arm][s]) for s in SEEDS} for arm in ARMS}
        cand = [(arm, s, list(real[arm][s]["deaths"])) for arm in ARMS for s in SEEDS
                if R[arm][s]["filt"] >= FILT_MIN]
        print(f"  ... {len(cand)} sombras", flush=True)
        sh: dict = {arm: {} for arm in ARMS}
        for arm, seed, r in ex.map(job, cand):
            sh[arm][seed] = resumen(r)
        sust = {arm: [s for s in SEEDS if R[arm][s]["filt"] >= FILT_MIN
                      and R[arm][s]["filt"] >= SHADOW_X * sh[arm][s]["filt"]] for arm in ARMS}
        abl: dict = {arm: {} for arm in ARMS}
        for arm, seed, nov, n_abl in ex.map(job_abl, [(a, s) for a in ARMS for s in sust[a][:MAX_ABL]]):
            pre, _, tail = medir_cola(nov, T_ABL)
            _, _, base = medir_cola(real[arm][seed]["raw"], T_ABL)
            abl[arm][seed] = dict(n_abl=n_abl, pre=pre, tail=tail, base=base, R=tail / max(base, 1.0))

    out("-" * 80)
    out("POR BRAZO (regimen maduro [8000,12000))")
    out(f"  {'brazo':<5} {'sostenidas':>10} {'ref 1-D':>7} {'candidatas':>10} {'eco med':>7} "
        f"{'filt/cruda':>10} {'cuota':>5} {'vivas med':>9} {'inv/t':>6} {'parto%':>6} {'reparan':>8}")
    for arm in ARMS:
        ss = sust[arm]
        ncand = sum(1 for s in SEEDS if R[arm][s]["filt"] >= FILT_MIN)
        eco = float(np.median([R[arm][s]["eco"] for s in ss])) if ss else float("nan")
        ratio = float(np.median([R[arm][s]["ratio"] for s in ss])) if ss else float("nan")
        share = float(np.median([R[arm][s]["share"] for s in ss])) if ss else float("nan")
        vivas = float(np.median([R[arm][s]["vivas"] for s in SEEDS]))
        inv = float(np.median([R[arm][s]["inv"] for s in SEEDS]))
        parto = float(np.median([R[arm][s]["parto"] for s in ss])) if ss else float("nan")
        rep = [s for s in ss[:MAX_ABL] if abl[arm].get(s, {}).get("R", 0) >= R_OK]
        out(f"  {arm:<5} {len(ss):>7}/40 {REF_1D_1024[arm]:>4}/40 {ncand:>10} {eco:>7.2f} "
            f"{ratio:>10.2f} {share:>5.2f} {vivas:>9.0f} {inv:>6.2f} {100*parto:>5.0f}% "
            f"{len(rep):>3}/{len(ss[:MAX_ABL]):<4}")
    out("  (candidatas = filtrada >= 5 antes de exigir >= 2x sombra; ref 1-D = mismo brazo a 1024 celdas)")
    out("")
    out("SEMILLAS SOSTENIDAS por brazo")
    for arm in ARMS:
        out(f"  {arm:<5}: {sust[arm]}")
    out("")
    out("DETALLE (semillas candidatas en algun brazo): filtrada | cruda | eco | sombra filtrada")
    cands = sorted({s for arm in ARMS for s in SEEDS if R[arm][s]["filt"] >= FILT_MIN})
    out(f"  {'seed':>4} " + " | ".join(f"{arm:^30}" for arm in ARMS))
    for s in cands[:40]:
        cells = []
        for arm in ARMS:
            r = R[arm][s]
            shf = sh[arm][s]["filt"] if s in sh[arm] else float("nan")
            mark = "*" if s in sust[arm] else " "
            cells.append(f"{r['filt']:>7.0f}{mark}{r['raw']:>8.0f} {r['eco']:>5.2f} {shf:>7.0f}")
        out(f"  {s:>4} " + " | ".join(cells))
    out("")
    out("ABLACION (sostenidas, hasta 6 por brazo): R = cola ablada / cola sin ablar")
    for arm in ARMS:
        for s, a in abl[arm].items():
            out(f"  {arm:<5} seed {s:>3}: abl {a['n_abl']:>4}  pre {a['pre']:>7.0f}  cola {a['tail']:>7.0f}"
                f"  sin {a['base']:>7.0f}  R {a['R']:>5.2f}")

    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    verdict = "SIN EFECTO"
    best = None
    for arm in ARMS:
        ss = sust[arm]
        n = len(ss)
        eco = float(np.median([R[arm][s]["eco"] for s in ss])) if ss else 0.0
        ratio = float(np.median([R[arm][s]["ratio"] for s in ss])) if ss else 0.0
        rep = [s for s in ss[:MAX_ABL] if abl[arm].get(s, {}).get("R", 0) >= R_OK]
        n_abl = len(ss[:MAX_ABL])
        if n > REF_1D_1024[arm] and (eco < ECO_BAD or ratio < CHURN):
            v = "TRAMPA"
        elif n >= TIPICA and eco >= ECO_OK and n_abl and len(rep) * 2 >= n_abl:
            v = "LA PERSPECTIVA PAGA"
        elif n >= 2 * REF_1D_1024[arm] and eco >= ECO_OK:
            v = "MEJORA"
        else:
            v = "sin efecto"
        out(f"  {arm:<5}: {n}/40 sostenidas (ref 1-D {REF_1D_1024[arm]}/40), ecologia {eco:.2f}, "
            f"filt/cruda {ratio:.2f}, reparan {len(rep)}/{n_abl} -> {v}")
        rank = {"LA PERSPECTIVA PAGA": 3, "MEJORA": 2, "TRAMPA": 1, "sin efecto": 0}
        if best is None or rank[v] > rank[best[1]]:
            best = (arm, v)
    verdict = best[1] if best else verdict
    out(f"=> {verdict.upper()} (mejor brazo: {best[0] if best else '-'})")

    # ---- figura ----
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    ax = axes[0]
    arms = list(ARMS)
    x = np.arange(len(arms))
    ax.bar(x - 0.2, [len(sust[a]) for a in arms], width=0.4, color="tab:red", label="2-D sostenidas")
    ax.bar(x + 0.2, [REF_1D_1024[a] for a in arms], width=0.4, color="gray", label="1-D (1024 celdas)")
    ax.axhline(TIPICA, color="k", ls="--", lw=0.8, label="típica (8/40)")
    ax.set_xticks(x)
    ax.set_xticklabels(arms)
    ax.set_ylabel("semillas sostenidas (/40)")
    ax.set_title("tipicidad: plano vs línea")
    ax.legend(fontsize=8)
    ax = axes[1]
    for arm, col in zip(arms, ("tab:blue", "tab:orange", "tab:green")):
        xs = [R[arm][s]["filt"] + 0.1 for s in SEEDS]
        ys = [R[arm][s]["eco"] for s in SEEDS]
        ax.scatter(xs, ys, s=14, color=col, alpha=0.7, label=arm)
    ax.axvline(FILT_MIN, color="gray", ls="--", lw=0.8)
    ax.axhline(ECO_OK, color="gray", ls="--", lw=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("novedad con linaje, maduro (/tramo)")
    ax.set_ylabel("ecología (bits)")
    ax.set_title("40 semillas × 3 brazos")
    ax.legend(fontsize=8)
    fig.suptitle("El Útero v8 — el plano")
    fig.tight_layout()
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / f"{NAME}.png", dpi=110)
    out("")
    out(f"figura: results/{NAME}.png")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
