"""
El Útero — ¿la novedad sobrevive a una vara honesta? Filtro de persistencia de
linaje (MODES) + corrida SOMBRA (Bedau & Packard), 40 semillas.

El estado del arte (docs/ESTADO_DEL_ARTE_UTERO.md) dejó dos objeciones a
nuestra vara "genomas nunca vistos por tramo": (1) cuenta ACUÑACIÓN, no
persistencia — se infla por deriva (MODES, Dolson et al. 2019); (2) no tiene
una SOMBRA neutral que diga cuánta novedad produciría la deriva sola, sin
selección (Bedau, Snyder & Packard 1998; Channon 2024). Este experimento aplica
ambas correcciones a la encarnación actual (memoria ON, germinal+toroidal)
sobre las 40 semillas de la réplica, ANTES de diseñar cualquier mecanismo nuevo.

  - Filtro de linaje: un genoma acuñado en t cuenta sólo si t_filtro ticks
    después alguna celda de su LÍNEA (continuidad de la celda + crías por
    SPAWN) sigue viva. t_filtro ∈ {100, 500, 2000} (sensibilidad; el
    principal es 500 ≈ un tramo).
  - Sombra: misma semilla, mismo sustrato, misma cantidad de muertes por tick
    que la corrida real, pero las muertes son AL AZAR en vez de por la sonda
    (la única selección del sistema). Lo que la sombra acuña es deriva.

VARAS — definidas ANTES de mirar:
  1. Tasa de supervivencia de la vara: novedad filtrada / novedad cruda, por
     semilla y en el régimen maduro (t∈[8000,12000)). Cuánto estaba inflada.
  2. Sostenido CRUDO (vara vieja): media ≥ 25 genomas nuevos/tramo en
     [8000,12000). Cuántas semillas, real vs sombra.
  3. Sostenido FILTRADO (vara nueva, t_filtro=500): media ≥ 5 genomas
     persistentes/tramo en [8000,12000) Y ≥ 2× el valor de su sombra.
  4. Actividad normalizada (Bedau): real − sombra por tramo, para la 13 y la
     35, y cuántas semillas tienen real > sombra en el régimen maduro.
VEREDICTO (pre-registrado): si las semillas que pasan la vara 3 son las mismas
que pasaban la cruda (13, 35), el 2/40 es DEFENDIBLE con la vara de la
literatura; si ninguna pasa, la novedad que reportamos era deriva y todo el
arco v3→v5 debe releerse; si pasan otras, la vara vieja escondía señal.
Manos: umbrales 25 y 5 por tramo, t_filtro, PRE=[8000,12000).

    PYTHONPATH=src python experiments/utero/exp_utero_linaje_sombra.py
"""

from __future__ import annotations

import math
import os
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.linaje import RastreadorLinaje  # noqa: E402

N0, MAX_N = 16, 256
TICKS = 14000
TRANCHE = 500
SEEDS = list(range(40))
T_FILTROS = (100, 500, 2000)
T_MAIN = 500
MATURE = (8000, 12000)                    # régimen maduro (deja 2000 para resolver)
RAW_MIN, FILT_MIN, SHADOW_X = 25.0, 5.0, 2.0
WORKERS = max(1, min(20, (os.cpu_count() or 4) - 4))
RESULTS = Path(__file__).resolve().parents[2] / "results"
NAME = "utero_linaje_sombra"


def correr(seed: int, shadow: list | None) -> dict:
    u = UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True,
                       memoria=True, log_events=True, shadow_deaths=shadow)
    trackers = {tf: RastreadorLinaje(tf) for tf in T_FILTROS}
    seen: set = set(u.seen)
    raw = np.zeros(TICKS, dtype=np.int64)
    deaths = np.zeros(TICKS, dtype=np.int64)
    vivas = np.zeros(TICKS, dtype=np.int64)
    presence: list[Counter] = [Counter() for _ in range((TICKS + TRANCHE - 1) // TRANCHE)]
    for t in range(TICKS):
        m = u.step()
        deaths[t] = m["deaths"]
        vivas[t] = int(u.alive.sum())
        cg = {int(i) - u.left_grown: u.code[i].tobytes() for i in np.flatnonzero(u.alive)}
        new = 0
        for g in cg.values():
            if g not in seen:
                seen.add(g)
                new += 1
        raw[t] = new
        presence[t // TRANCHE].update(cg.values())
        for tr in trackers.values():
            tr.tick(t, cg, u.spawns)
    filt = {tf: tr.novedad_filtrada(TRANCHE, TICKS) for tf, tr in trackers.items()}
    ok = trackers[T_MAIN].resueltos()
    ecology = []
    for c in presence:
        kept = {g: n for g, n in c.items() if ok.get(g, False)}
        tot = sum(kept.values())
        ecology.append(-sum(n / tot * math.log2(n / tot) for n in kept.values()) if tot else 0.0)
    return {"raw": raw, "filt": filt, "deaths": deaths, "vivas": vivas,
            "ecology": np.array(ecology), "n_resolved": len(ok),
            "n_persist": int(sum(ok.values()))}


def job(seed: int) -> tuple:
    real = correr(seed, None)
    shadow = correr(seed, list(real["deaths"]))
    return seed, real, shadow


def por_tramo(x: np.ndarray) -> np.ndarray:
    return x.reshape(-1, TRANCHE).sum(axis=1)


def maduro(xt: np.ndarray) -> float:
    a, b = MATURE[0] // TRANCHE, MATURE[1] // TRANCHE
    return float(xt[a:b].mean())


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 78)
    out("EL UTERO -- filtro de persistencia de linaje (MODES) + corrida SOMBRA, 40 semillas")
    out("=" * 78)
    out(f"memoria ON, germinal+toroidal, {TICKS} ticks, tramo {TRANCHE}, t_filtro {T_FILTROS} "
        f"(principal {T_MAIN}), maduro {MATURE}, workers={WORKERS}")
    out("varas y veredicto pre-registrados en el docstring")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (seed, real, shadow) in enumerate(ex.map(job, SEEDS), 1):
            res[seed] = (real, shadow)
            if i % 10 == 0:
                print(f"  ... {i}/{len(SEEDS)} semillas", flush=True)

    # ---- tabla por semilla (sólo las que tienen algo que mostrar) ----
    rows = {}
    for seed, (real, shadow) in res.items():
        r_raw = maduro(por_tramo(real["raw"]))
        s_raw = maduro(por_tramo(shadow["raw"]))
        r_f = {tf: maduro(real["filt"][tf]) for tf in T_FILTROS}
        s_f = {tf: maduro(shadow["filt"][tf]) for tf in T_FILTROS}
        rows[seed] = dict(r_raw=r_raw, s_raw=s_raw, r_f=r_f, s_f=s_f,
                          ratio=r_f[T_MAIN] / r_raw if r_raw else float("nan"),
                          eco=maduro(real["ecology"]), eco_s=maduro(shadow["ecology"]),
                          vivas=int(real["vivas"][-1]), vivas_s=int(shadow["vivas"][-1]))
    out("-" * 78)
    out("REGIMEN MADURO t in [8000,12000): novedad por tramo de 500 (media)")
    fcols = " ".join(f"{'f' + str(tf):>6}" for tf in T_FILTROS)
    out(f"  {'seed':>4} | {'REAL cruda':>10} {fcols} "
        f"{'f' + str(T_MAIN) + '/cruda':>10} {'ecol':>5} {'vivas':>5} | {'SOMBRA cruda':>12} "
        f"{'f' + str(T_MAIN):>6} {'ecol':>5} {'vivas':>5}")
    shown = 0
    for seed in SEEDS:
        r = rows[seed]
        if r["r_raw"] < 1 and r["s_raw"] < 1:
            continue
        shown += 1
        fv = " ".join(f"{r['r_f'][tf]:>6.1f}" for tf in T_FILTROS)
        out(f"  {seed:>4} | {r['r_raw']:>10.1f} {fv} "
            f"{r['ratio']:>10.2f} {r['eco']:>5.2f} {r['vivas']:>5} | "
            f"{r['s_raw']:>12.1f} {r['s_f'][T_MAIN]:>6.1f} {r['eco_s']:>5.2f} {r['vivas_s']:>5}")
    out(f"  ({len(SEEDS) - shown} semillas con novedad madura <1/tramo en real y sombra omitidas)")

    # ---- varas ----
    out("")
    out("-" * 78)
    ratios = [rows[s]["ratio"] for s in SEEDS if rows[s]["r_raw"] >= 1]
    out(f"1. SUPERVIVENCIA DE LA VARA (f500/cruda, maduro, semillas con cruda>=1/tramo, n={len(ratios)}):")
    if ratios:
        out(f"   mediana {np.median(ratios):.2f}  min {min(ratios):.2f}  max {max(ratios):.2f}"
            f"   seed13={rows[13]['ratio']:.2f}  seed35={rows[35]['ratio']:.2f}")
    sust_raw = [s for s in SEEDS if rows[s]["r_raw"] >= RAW_MIN]
    sust_raw_s = [s for s in SEEDS if rows[s]["s_raw"] >= RAW_MIN]
    out(f"2. SOSTENIDO CRUDO (>= {RAW_MIN:.0f}/tramo): real {len(sust_raw)}/40 {sust_raw}   "
        f"sombra {len(sust_raw_s)}/40 {sust_raw_s}")
    sust_f = {}
    for tf in T_FILTROS:
        sust_f[tf] = [s for s in SEEDS if rows[s]["r_f"][tf] >= FILT_MIN
                      and rows[s]["r_f"][tf] >= SHADOW_X * max(rows[s]["s_f"][tf], 0.0)]
        out(f"3. SOSTENIDO FILTRADO t_filtro={tf:>4} (>= {FILT_MIN:.0f}/tramo y >= {SHADOW_X:.0f}x sombra): "
            f"{len(sust_f[tf])}/40 {sust_f[tf]}")
    beats = [s for s in SEEDS if rows[s]["r_f"][T_MAIN] > rows[s]["s_f"][T_MAIN]]
    beats_raw = [s for s in SEEDS if rows[s]["r_raw"] > rows[s]["s_raw"]]
    out(f"4. ACTIVIDAD NORMALIZADA (real > sombra, maduro): filtrada {len(beats)}/40, "
        f"cruda {len(beats_raw)}/40")
    for s in (13, 35):
        r = rows[s]
        out(f"   seed {s}: cruda real-sombra = {r['r_raw'] - r['s_raw']:+.1f}/tramo ; "
            f"f{T_MAIN} real-sombra = {r['r_f'][T_MAIN] - r['s_f'][T_MAIN]:+.1f}/tramo ; "
            f"ecologia (bits) real {r['eco']:.2f} vs sombra {r['eco_s']:.2f}")
    out("")
    out("   curvas por tramo (seed 13 / 35):  tramo: cruda | f500 | sombra_cruda | sombra_f500")
    for s in (13, 35):
        real, shadow = res[s]
        rr, rf = por_tramo(real["raw"]), real["filt"][T_MAIN]
        sr, sf = por_tramo(shadow["raw"]), shadow["filt"][T_MAIN]
        pts = [f"{k * TRANCHE}: {rr[k]}|{rf[k]}|{sr[k]}|{sf[k]}"
               for k in range(0, (TICKS - 2000) // TRANCHE, 2)]
        out(f"   seed {s}: " + "  ".join(pts))

    # ---- veredicto ----
    out("")
    out("=" * 78)
    out("VEREDICTO (regla escrita antes de correr)")
    main_set, raw_set = set(sust_f[T_MAIN]), set(sust_raw)
    if not main_set:
        out("=> NINGUNA semilla pasa la vara filtrada: la novedad reportada en v3..v5 era")
        out("   DERIVA (acuñacion sin persistencia). El arco v3->v5 debe releerse.")
    elif main_set == raw_set:
        out(f"=> DEFENDIBLE: las mismas semillas {sorted(main_set)} pasan la vara cruda y la")
        out("   filtrada (>= 2x su sombra). El 2/40 sobrevive a la vara de la literatura.")
    elif main_set < raw_set:
        out(f"=> PARCIAL: de las crudas {sorted(raw_set)} solo {sorted(main_set)} pasan la")
        out("   filtrada; el resto era acuñacion sin linaje.")
    else:
        out(f"=> LA VARA VIEJA ESCONDIA SEÑAL: pasan la filtrada {sorted(main_set)} y la cruda")
        out(f"   {sorted(raw_set)}.")

    # ---- figura ----
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    for ax, s in zip(axes[:2], (13, 35)):
        real, shadow = res[s]
        xs = (np.arange(TICKS // TRANCHE) + 0.5) * TRANCHE
        k = (TICKS - 2000) // TRANCHE
        ax.plot(xs, por_tramo(real["raw"]), color="k", label="real, cruda")
        ax.plot(xs[:k], real["filt"][T_MAIN][:k], color="tab:red", lw=2, label="real, linaje 500")
        ax.plot(xs, por_tramo(shadow["raw"]), color="gray", ls="--", label="sombra, cruda")
        ax.plot(xs[:k], shadow["filt"][T_MAIN][:k], color="tab:orange", ls="--", label="sombra, linaje 500")
        ax.axvspan(*MATURE, color="tab:blue", alpha=0.08)
        ax.set_yscale("symlog")
        ax.set_title(f"seed {s}")
        ax.set_xlabel("tick")
        ax.legend(fontsize=7)
    axes[0].set_ylabel("genomas nuevos por tramo")
    ax = axes[2]
    for s in SEEDS:
        r = rows[s]
        ax.scatter(r["r_raw"] + 0.1, r["r_f"][T_MAIN] + 0.1, color="tab:red" if s in (13, 35) else "tab:blue",
                   s=40 if s in (13, 35) else 15)
        ax.scatter(r["s_raw"] + 0.1, r["s_f"][T_MAIN] + 0.1, facecolors="none",
                   edgecolors="gray", s=15)
        if s in (13, 35):
            ax.annotate(str(s), (r["r_raw"] + 0.1, r["r_f"][T_MAIN] + 0.1), fontsize=8)
    ax.axhline(FILT_MIN, color="gray", ls=":", lw=0.8)
    ax.axvline(RAW_MIN, color="gray", ls=":", lw=0.8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("novedad cruda madura (/tramo)")
    ax.set_ylabel("novedad con linaje 500 (/tramo)")
    ax.set_title("40 semillas: lleno=real, hueco=sombra")
    fig.suptitle("El Útero — ¿la novedad sobrevive al filtro de linaje y a la sombra?")
    fig.tight_layout()
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / f"{NAME}.png", dpi=110)
    out("")
    out(f"figura: results/{NAME}.png")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
