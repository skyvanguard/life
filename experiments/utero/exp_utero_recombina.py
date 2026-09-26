"""
El Útero — v7: RECOMBINACIÓN al nacer. ¿Dos progenitores rompen el punto fijo
letal del mapa germinal y vuelven típica la novedad sostenida?

La mortalidad infantil mostró el mecanismo de la esterilidad: la mutación
germinal (v2) es un mapa determinista del estado quieto de la madre → siempre
la misma cría → letal → las llanuras de todas las semillas son estériles en
estado estacionario (0% de 3.743 crías sobrevive). El 85–91% de los mutantes
posibles SON viables: la trampa es el determinismo, no el genoma. v7 =
`recombina=True`: la cría toma además UNA instrucción del otro progenitor (el
vecino de la madre del lado opuesto al parto) si su genoma difiere. Cero RNG:
la variación sale del contacto entre reglas distintas — la respuesta de
Evoloop/Sexyloop y de Stringmol al mismo problema (docs/ESTADO_DEL_ARTE).

BRAZOS (40 semillas, 14000 ticks, memoria ON, germinal+toroidal):
  v5 · v7 (recombina) · v6+v7 (invasión asentada-100 + recombina).
  Sombra sólo para las candidatas; ablación de la bomba en t=8000 en las
  sostenidas (hasta 6 por brazo); seguimiento de crías de LLANURA en la seed
  35 (misma clasificación que la mortalidad infantil) para v7.
VARAS — escritas ANTES de mirar:
  1. Tipicidad filtrada (linaje 500, ≥5/tramo en [8000,12000), ≥2× sombra).
     TÍPICA = ≥ 8/40 (20%). Referencia: v5 2/40, v6 3/40.
  2. Ecología mediana ≥ 2 bits en las sostenidas (monocultura = < 1 bit).
  3. Crías de llanura de la 35 que sobreviven 500 ticks: v5 = 0%; predicción
     v7 ≥ 20%, con > 1 genoma de cría distinto.
  4. Auto-reparación (R ≥ 0.5) en ≥ la mitad de las sostenidas abladas.
VEREDICTO (pre-registrado):
  ÉXITO     tipicidad ≥ 8/40 en algún brazo con recombina, ecología ≥ 2 bits
            y auto-reparación ≥ mitad.
  MEJORA    tipicidad > 3/40 con ecología ≥ 2 bits (sin llegar a típica).
  TRAMPA    tipicidad sube pero ecología < 1 bit (un recombinante barre).
  SIN EFECTO tipicidad ≤ 3/40 en ambos brazos con recombina.
  Vara 3 se reporta aparte: si las crías de la 35 siguen muriendo al 100%,
  la recombinación no llegó a las llanuras (clonales) y el problema es la
  diversidad de madres, no el mapa.

    PYTHONPATH=src python experiments/utero/exp_utero_recombina.py
"""

from __future__ import annotations

import importlib.util
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

N0, MAX_N = 16, 256
TICKS = 14000
TRANCHE = 500
SEEDS = list(range(40))
T_FILTRO = 500
MATURE = (8000, 12000)
FILT_MIN, SHADOW_X, R_OK = 5.0, 2.0, 0.5
TIPICA, ECO_OK, ECO_BAD, SURV_OK = 8, 2.0, 1.0, 0.20
T_ABL, POST, MAX_ABL = 8000, 4000, 6
ARMS = {"v5": {}, "v7": dict(recombina=True),
        "v6+v7": dict(recombina=True, invasion="asentada", eq_window=100)}
REF = {"v5": 2, "v6": 3}
WORKERS = max(1, min(20, (os.cpu_count() or 4) - 4))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_recombina"


def _mortalidad_mod():
    spec = importlib.util.spec_from_file_location(
        "mortalidad", HERE / "exp_utero_mortalidad_infantil.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def job_crias(args: tuple) -> tuple:
    arm, seed = args
    mod = _mortalidad_mod()
    r = mod.correr(seed, flags=ARMS[arm])
    return arm, seed, mod.resumen(r["children"], True), mod.resumen(r["children"], False)


def resumen(r: dict) -> dict:
    a, b = MATURE[0] // TRANCHE, MATURE[1] // TRANCHE
    causa = r["causa"][a:b]
    return dict(raw=media_ventana(por_tramo(r["raw"], TRANCHE), MATURE, TRANCHE),
                filt=media_ventana(r["filt"], MATURE, TRANCHE),
                eco=media_ventana(r["eco"], MATURE, TRANCHE),
                vivas=int(r["vivas"][-1]),
                parto=float(causa[:, 0].sum() / max(causa.sum(), 1)))


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 78)
    out("EL UTERO -- v7: RECOMBINACION al nacer (una instruccion del otro progenitor)")
    out("=" * 78)
    out(f"brazos {list(ARMS)}, 40 semillas, {TICKS} ticks, memoria ON, linaje {T_FILTRO}, "
        f"maduro {MATURE}, workers={WORKERS}")
    out("varas y veredicto pre-registrados en el docstring")
    out("")
    real: dict = {arm: {} for arm in ARMS}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        jobs = [(arm, s, None) for arm in ARMS for s in SEEDS]
        for i, (arm, seed, r) in enumerate(ex.map(job, jobs), 1):
            real[arm][seed] = r
            if i % 40 == 0:
                print(f"  ... {i}/{len(jobs)} corridas reales", flush=True)
        R = {arm: {s: resumen(real[arm][s]) for s in SEEDS} for arm in ARMS}
        cand = [(arm, s, list(real[arm][s]["deaths"])) for arm in ARMS for s in SEEDS
                if R[arm][s]["filt"] >= FILT_MIN]
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
        crias = {}
        for arm, seed, llan, bomba in ex.map(job_crias, [("v5", 35), ("v7", 35), ("v6+v7", 35),
                                                         ("v7", 13), ("v6+v7", 13)]):
            crias[(arm, seed)] = (llan, bomba)

    # ---- tabla por brazo ----
    out("-" * 78)
    out("POR BRAZO (regimen maduro [8000,12000))")
    out(f"  {'brazo':<7} {'sostenidas':>10}  {'semillas':<30} {'eco med':>7} {'vivas med':>9} "
        f"{'parto%':>6} {'reparan':>8}")
    for arm in ARMS:
        ss = sust[arm]
        eco = float(np.median([R[arm][s]["eco"] for s in ss])) if ss else float("nan")
        vivas = float(np.median([R[arm][s]["vivas"] for s in SEEDS]))
        parto = float(np.median([R[arm][s]["parto"] for s in ss])) if ss else float("nan")
        rep = [s for s in ss[:MAX_ABL] if abl[arm].get(s, {}).get("R", 0) >= R_OK]
        out(f"  {arm:<7} {len(ss):>7}/40  {str(ss):<30} {eco:>7.2f} {vivas:>9.0f} "
            f"{100 * parto:>5.0f}% {len(rep):>3}/{len(ss[:MAX_ABL]):<4}")
    out("  referencia: v5 2/40, v6 (invasion sola) 3/40")
    out("")
    out("SEMILLAS CANDIDATAS (filtrada >= 5 en algun brazo): novedad con linaje / tramo")
    cands = sorted({s for arm in ARMS for s in SEEDS if R[arm][s]["filt"] >= FILT_MIN})
    out(f"  {'seed':>4} " + " ".join(f"{arm:>12}" for arm in ARMS) + "   ecologia (v7 / v6+v7)")
    for s in cands:
        cells = [f"{R[arm][s]['filt']:>11.0f}{'*' if s in sust[arm] else ' '}" for arm in ARMS]
        out(f"  {s:>4} " + " ".join(cells) + f"   {R['v7'][s]['eco']:.2f} / {R['v6+v7'][s]['eco']:.2f}")
    out("  (* = sostenida)")
    out("")
    out("ABLACION (sostenidas, hasta 6 por brazo): R = cola ablada / cola sin ablar")
    for arm in ARMS:
        for s, a in abl[arm].items():
            out(f"  {arm:<7} seed {s:>3}: abl {a['n_abl']:>4}  pre {a['pre']:>6.0f}  cola {a['tail']:>6.0f}"
                f"  sin {a['base']:>6.0f}  R {a['R']:>5.2f}")
    out("")
    out("CRIAS DE LLANURA (nacidas en [8000,9000), seguidas 500 ticks)")
    out(f"  {'brazo':<7} {'seed':>4} {'crias':>5} {'ciega0':>7} {'1a ejec':>8} {'auto-mut':>9} "
        f"{'reempl':>7} {'sobrev':>7} {'distintas':>9}")
    for (arm, seed), (llan, _) in crias.items():
        if llan["n"] == 0:
            out(f"  {arm:<7} {seed:>4} {0:>5}  (sin nacimientos de llanura: mundo lleno)")
            continue
        out(f"  {arm:<7} {seed:>4} {llan['n']:>5} {100*llan['blind0']:>6.0f}% {100*llan['1a ejecucion']:>7.0f}% "
            f"{100*llan['auto-mutilacion']:>8.0f}% {100*llan['reemplazada']:>6.0f}% "
            f"{100*llan['sobrevive']:>6.0f}% {100*llan['distinct']:>8.0f}%")

    # ---- veredicto ----
    out("")
    out("=" * 78)
    out("VEREDICTO (regla escrita antes de correr)")
    best = max(("v7", "v6+v7"), key=lambda a: len(sust[a]))
    n_best = len(sust[best])
    eco_best = float(np.median([R[best][s]["eco"] for s in sust[best]])) if sust[best] else 0.0
    rep_best = [s for s in sust[best][:MAX_ABL] if abl[best].get(s, {}).get("R", 0) >= R_OK]
    n_abl_best = len(sust[best][:MAX_ABL])
    if n_best >= TIPICA and eco_best >= ECO_OK and n_abl_best and len(rep_best) * 2 >= n_abl_best:
        v = "EXITO"
    elif n_best > REF["v6"] and eco_best < ECO_BAD:
        v = "TRAMPA (monocultura)"
    elif n_best > REF["v6"] and eco_best >= ECO_OK:
        v = "MEJORA"
    elif n_best <= REF["v6"]:
        v = "SIN EFECTO"
    else:
        v = "PARCIAL"
    out(f"=> {v}: mejor brazo {best} = {n_best}/40 (v5 {len(sust['v5'])}/40, ref v6 3/40); "
        f"ecologia {eco_best:.2f} bits; auto-reparacion {len(rep_best)}/{n_abl_best}")
    l35 = crias[("v7", 35)][0]
    if l35["n"]:
        out(f"   vara 3 (crias de llanura de la 35, v7): sobreviven {100*l35['sobrevive']:.0f}% "
            f"(v5: 0%), genomas distintos {100*l35['distinct']:.0f}% -> "
            f"{'la recombinacion LLEGO a las llanuras' if l35['sobrevive'] >= SURV_OK else 'las llanuras siguen esteriles (clonales): el problema es la diversidad de madres'}")

    # ---- figura ----
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    ax = axes[0]
    arms = list(ARMS)
    x = np.arange(len(arms))
    ax.bar(x, [len(sust[a]) for a in arms], color=["gray", "tab:red", "tab:purple"])
    ax.axhline(TIPICA, color="k", ls="--", lw=0.8, label="típica (8/40)")
    ax.set_xticks(x)
    ax.set_xticklabels(arms)
    ax.set_ylabel("semillas sostenidas (/40)")
    ax.set_title("tipicidad por brazo")
    ax.legend(fontsize=8)
    ax = axes[1]
    for s in cands:
        ax.plot(x, [R[a][s]["filt"] + 0.1 for a in arms], "o-", alpha=0.8, label=f"seed {s}")
    ax.axhline(FILT_MIN, color="gray", ls="--", lw=0.8)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(arms)
    ax.set_ylabel("novedad con linaje, maduro (/tramo)")
    ax.set_title("semillas candidatas a través de los brazos")
    if len(cands) <= 14:
        ax.legend(fontsize=6)
    fig.suptitle("El Útero v7 — recombinación al nacer")
    fig.tight_layout()
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / f"{NAME}.png", dpi=110)
    out("")
    out(f"figura: results/{NAME}.png")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
