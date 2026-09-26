"""
El Útero — control de v6: ¿el 3/40 lo hace la INVASIÓN o la MANO declarada?

v6 (`invasion="asentada"`, eq_window=100) dio tipicidad 2/40 → 3/40, sin
monocultura, auto-reparación 1/3. Antes de creerlo hay que separar el efecto
de la invasión (interacción regla↔regla con efecto neto en tejido asentado)
del efecto del umbral de quietud que decide QUÉ es invadible (la mano
declarada, heredada de v4). Dos controles en uno:

  A. `invasion="siempre"`: cualquier vecino vivo es reemplazable, sin umbral.
     Si da lo mismo (o más) que "asentada", la mano sobra — mejor. Si colapsa
     (monocultura o mundo muerto), la mano hace el trabajo.
  B. Barrido de eq_window ∈ {10, 100, 1000} con "asentada": dosis-respuesta.

Brazos: v5 · siempre · asentada-10 · asentada-100 (= v6) · asentada-1000, 40
semillas, 14000 ticks. La sombra (muertes al azar en vez de sonda) se corre
sólo para las semillas candidatas (novedad filtrada ≥ 5/tramo) de cada brazo
— es lo único que necesita el criterio ≥2× sombra. Ablación de la bomba en
t=8000 para las sostenidas de cada brazo (hasta 6 por brazo).

VARAS — escritas ANTES de mirar (lecciones de v6: nada de "cuota < 0.5"
absoluta; la cuota se reporta RELATIVA a v5 y la monocultura se juzga por
ecología):
  1. Tipicidad filtrada por brazo: nº de semillas con ≥ 5 genomas
     persistentes/tramo en [8000,12000) y ≥ 2× su sombra.
  2. Ecología mediana (bits) de las sostenidas; monocultura = < 1 bit.
  3. Vivas al final (mediana 40 semillas) e invasiones/tick.
  4. Auto-reparación (R ≥ 0.5) en las sostenidas abladas.
  5. Identidad: ¿son las mismas semillas (13, 35, 21) en todos los brazos o
     cambian con el brazo? Si cambian, la tipicidad se lee como CONTEO, no
     como identidad (cada brazo es una dinámica distinta).
VEREDICTO (pre-registrado), comparando "siempre" con "asentada-100":
  LA MANO SOBRA      si tipicidad(siempre) ≥ tipicidad(asentada-100) y
                     ecología mediana ≥ 2 bits.
  LA MANO TRABAJA    si tipicidad(siempre) < tipicidad(asentada-100), o
                     ecología(siempre) < 1 bit, o vivas(siempre) < 50.
  Además, "DOSIS": si la tipicidad es monótona en eq_window se reporta el
  sentido; si no, se reporta como insensible/ruidosa.

    PYTHONPATH=src python experiments/utero/exp_utero_invasion_control.py
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

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zeta_life.utero.ablacion import correr as correr_ablacion  # noqa: E402
from zeta_life.utero.ablacion import medir_cola  # noqa: E402
from zeta_life.utero.medidas import correr_medido, media_ventana, por_tramo  # noqa: E402

N0, MAX_N = 16, 256
TICKS = 14000
TRANCHE = 500
SEEDS = list(range(40))
T_FILTRO = 500
MATURE = (8000, 12000)
FILT_MIN, SHADOW_X, R_OK = 5.0, 2.0, 0.5
ECO_OK, ECO_BAD, VIVAS_MIN = 2.0, 1.0, 50
T_ABL, POST, MAX_ABL = 8000, 4000, 6
ARMS = {
    "v5": {},
    "siempre": dict(invasion="siempre"),
    "asentada-10": dict(invasion="asentada", eq_window=10),
    "asentada-100": dict(invasion="asentada", eq_window=100),
    "asentada-1000": dict(invasion="asentada", eq_window=1000),
}
WORKERS = max(1, min(20, (os.cpu_count() or 4) - 4))
RESULTS = Path(__file__).resolve().parents[2] / "results"
NAME = "utero_invasion_control"


def job(args: tuple) -> tuple:
    arm, seed, shadow = args
    r = correr_medido(seed, dict(memoria=True, **ARMS[arm]), ticks=TICKS, tranche=TRANCHE,
                      t_filtro=T_FILTRO, shadow=shadow, n0=N0, max_n=MAX_N)
    return arm, seed, r


def job_abl(args: tuple) -> tuple:
    arm, seed = args
    r = correr_ablacion(seed=seed, memoria=True, ticks=T_ABL + POST, ablate_at=T_ABL,
                        n0=N0, max_n=MAX_N, **ARMS[arm])
    return arm, seed, r["novedad"], r["ablated"]


def resumen(r: dict) -> dict:
    a, b = MATURE[0] // TRANCHE, MATURE[1] // TRANCHE
    causa = r["causa"][a:b]
    return dict(raw=media_ventana(por_tramo(r["raw"], TRANCHE), MATURE, TRANCHE),
                filt=media_ventana(r["filt"], MATURE, TRANCHE),
                eco=media_ventana(r["eco"], MATURE, TRANCHE),
                share=media_ventana(r["share"], MATURE, TRANCHE),
                inv=float(r["invaded"][MATURE[0]:MATURE[1]].mean()),
                vivas=int(r["vivas"][-1]),
                parto=float(causa[:, 0].sum() / max(causa.sum(), 1)))


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 78)
    out("EL UTERO -- control de v6: invasion='siempre' (sin umbral) + barrido de eq_window")
    out("=" * 78)
    out(f"brazos {list(ARMS)}, 40 semillas, {TICKS} ticks, memoria ON, linaje {T_FILTRO}, "
        f"maduro {MATURE}, workers={WORKERS}")
    out("varas y veredicto pre-registrados en el docstring")
    out("")

    # ---- fase 1: corridas reales de todos los brazos ----
    real: dict = {arm: {} for arm in ARMS}
    jobs = [(arm, s, None) for arm in ARMS for s in SEEDS]
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (arm, seed, r) in enumerate(ex.map(job, jobs), 1):
            real[arm][seed] = r
            if i % 40 == 0:
                print(f"  ... {i}/{len(jobs)} corridas reales", flush=True)
        # ---- fase 2: sombras sólo para las candidatas ----
        R = {arm: {s: resumen(real[arm][s]) for s in SEEDS} for arm in ARMS}
        cand = [(arm, s, list(real[arm][s]["deaths"])) for arm in ARMS for s in SEEDS
                if R[arm][s]["filt"] >= FILT_MIN]
        shadow: dict = {arm: {} for arm in ARMS}
        for arm, seed, r in ex.map(job, cand):
            shadow[arm][seed] = resumen(r)
        sust = {arm: [s for s in SEEDS if R[arm][s]["filt"] >= FILT_MIN
                      and R[arm][s]["filt"] >= SHADOW_X * shadow[arm][s]["filt"]]
                for arm in ARMS}
        # ---- fase 3: ablación en las sostenidas ----
        abl_jobs = [(arm, s) for arm in ARMS for s in sust[arm][:MAX_ABL]]
        abl: dict = {arm: {} for arm in ARMS}
        for arm, seed, nov, n_abl in ex.map(job_abl, abl_jobs):
            pre, _, tail = medir_cola(nov, T_ABL)
            _, _, base = medir_cola(real[arm][seed]["raw"], T_ABL)
            abl[arm][seed] = dict(n_abl=n_abl, pre=pre, tail=tail, base=base,
                                  R=tail / max(base, 1.0))

    # ---- tabla por brazo ----
    out("-" * 78)
    out("POR BRAZO (regimen maduro [8000,12000))")
    out(f"  {'brazo':<14} {'sostenidas':>10}  {'semillas':<22} {'eco med':>7} {'cuota/v5':>8} "
        f"{'vivas med':>9} {'inv/t med':>9} {'reparan':>8}")
    for arm in ARMS:
        ss = sust[arm]
        eco = float(np.median([R[arm][s]["eco"] for s in ss])) if ss else float("nan")
        share_rel = (float(np.median([R[arm][s]["share"] / max(R["v5"][s]["share"], 1e-9) for s in ss]))
                     if ss else float("nan"))
        vivas = float(np.median([R[arm][s]["vivas"] for s in SEEDS]))
        inv = float(np.median([R[arm][s]["inv"] for s in SEEDS]))
        rep = [s for s in ss[:MAX_ABL] if abl[arm].get(s, {}).get("R", 0) >= R_OK]
        out(f"  {arm:<14} {len(ss):>7}/40  {str(ss):<22} {eco:>7.2f} {share_rel:>8.2f} "
            f"{vivas:>9.0f} {inv:>9.2f} {len(rep):>3}/{len(ss[:MAX_ABL]):<4}")
    out("  (cuota/v5 = cuota del genoma dominante relativa a la de v5 en la misma semilla)")

    # ---- detalle por semilla candidata ----
    out("")
    out("SEMILLAS CANDIDATAS (filtrada >= 5 en algun brazo): novedad con linaje / tramo")
    cands = sorted({s for arm in ARMS for s in SEEDS if R[arm][s]["filt"] >= FILT_MIN})
    out(f"  {'seed':>4} " + " ".join(f"{arm:>14}" for arm in ARMS))
    for s in cands:
        cells = []
        for arm in ARMS:
            f = R[arm][s]["filt"]
            mark = "*" if s in sust[arm] else " "
            cells.append(f"{f:>13.0f}{mark}")
        out(f"  {s:>4} " + " ".join(cells))
    out("  (* = sostenida: >= 5/tramo y >= 2x su sombra)")
    out("")
    out("ABLACION (sostenidas, hasta 6 por brazo): R = cola ablada / cola sin ablar")
    for arm in ARMS:
        for s, a in abl[arm].items():
            out(f"  {arm:<14} seed {s:>3}: abl {a['n_abl']:>4}  pre {a['pre']:>6.0f}  cola {a['tail']:>6.0f}"
                f"  sin {a['base']:>6.0f}  R {a['R']:>5.2f}")

    # ---- veredicto ----
    out("")
    out("=" * 78)
    out("VEREDICTO (regla escrita antes de correr)")
    t_s, t_a = len(sust["siempre"]), len(sust["asentada-100"])
    eco_s = float(np.median([R["siempre"][s]["eco"] for s in sust["siempre"]])) if sust["siempre"] else 0.0
    viv_s = float(np.median([R["siempre"][s]["vivas"] for s in SEEDS]))
    if t_s >= t_a and eco_s >= ECO_OK:
        out(f"=> LA MANO SOBRA: 'siempre' da {t_s}/40 sostenidas (asentada-100: {t_a}/40) con "
            f"ecologia {eco_s:.2f} bits. El umbral de quietud no es lo que trabaja.")
    elif t_s < t_a or eco_s < ECO_BAD or viv_s < VIVAS_MIN:
        out(f"=> LA MANO TRABAJA: 'siempre' da {t_s}/40 (asentada-100: {t_a}/40), ecologia "
            f"{eco_s:.2f} bits, vivas mediana {viv_s:.0f}. Sin umbral la invasion no rinde igual.")
    else:
        out(f"=> AMBIGUO: siempre {t_s}/40 vs asentada-100 {t_a}/40, ecologia {eco_s:.2f}.")
    dosis = [len(sust[a]) for a in ("asentada-10", "asentada-100", "asentada-1000")]
    if dosis == sorted(dosis) and dosis[0] < dosis[-1]:
        sentido = "CRECIENTE con eq_window"
    elif dosis == sorted(dosis, reverse=True) and dosis[0] > dosis[-1]:
        sentido = "DECRECIENTE con eq_window"
    else:
        sentido = "NO monotona (insensible o ruidosa)"
    out(f"   DOSIS eq_window 10/100/1000 -> sostenidas {dosis}: {sentido}")
    ident = [set(sust[a]) for a in ARMS if a != "v5"]
    inter = set.intersection(*ident) if ident else set()
    out(f"   IDENTIDAD: sostenidas en TODOS los brazos con invasion: {sorted(inter)}; "
        f"union: {sorted(set.union(*ident)) if ident else []}")

    # ---- figura ----
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    ax = axes[0]
    arms = list(ARMS)
    x = np.arange(len(arms))
    ax.bar(x - 0.2, [len(sust[a]) for a in arms], width=0.4, color="tab:red", label="sostenidas (/40)")
    ax2 = ax.twinx()
    ax2.bar(x + 0.2, [np.median([R[a][s]["vivas"] for s in SEEDS]) for a in arms], width=0.4,
            color="tab:gray", alpha=0.6, label="vivas al final (mediana)")
    ax.set_xticks(x)
    ax.set_xticklabels(arms, rotation=20, fontsize=8)
    ax.set_ylabel("semillas sostenidas")
    ax2.set_ylabel("vivas al final")
    ax.set_title("tipicidad y supervivencia por brazo")
    ax.legend(loc="upper left", fontsize=7)
    ax2.legend(loc="upper right", fontsize=7)
    ax = axes[1]
    for s in cands:
        ax.plot(x, [R[a][s]["filt"] + 0.1 for a in arms], "o-", label=f"seed {s}", alpha=0.8)
    ax.axhline(FILT_MIN, color="gray", ls="--", lw=0.8)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(arms, rotation=20, fontsize=8)
    ax.set_ylabel("novedad con linaje, maduro (/tramo)")
    ax.set_title("semillas candidatas a través de los brazos")
    ax.legend(fontsize=7)
    fig.suptitle("El Útero — control de v6: ¿invasión o mano declarada?")
    fig.tight_layout()
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / f"{NAME}.png", dpi=110)
    out("")
    out(f"figura: results/{NAME}.png")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
