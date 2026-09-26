"""
El Útero — v6: INVASIÓN de tejido asentado. ¿Un motor ecológico hace típica la
novedad sostenida, sin monocultura, y con auto-reparación?

Lo que trajo hasta acá (docs/EL_UTERO.md): la novedad sostenida es 2/40 y
defendible (linaje + sombra); la auto-reparación depende de la fertilidad de
las llanuras; el motor actual es MUTO (auto-mutación acoplada a la materia) y
la interacción regla↔regla con efecto neto es CERO en tejido asentado. En una
llanura congelada nada se mueve, así que ninguna función determinista de su
estado puede dar variación: la variación tiene que llegarle desde afuera, y
hoy no puede porque SPAWN sólo escribe en el vacío.

v6 = flag `invasion="asentada"` en `UteroCreciente`: un SPAWN dirigido a una
celda viva cuya materia lleva eq_window=100 ticks quieta la REEMPLAZA
(reemplazo, no muerte: v4 mató las llanuras y dejó un desierto). Une las dos
direcciones que quedaron abiertas: motor ecológico (Stringmol/Evoloop) y
turbulencia como atractor (la zona activa invade el borde asentado). Manos
declaradas: eq_eps=1e-9, eq_window=100 (las de v4). `invasion=None` es
byte-idéntico a v5 (test).

BRAZOS (40 semillas, 14000 ticks, memoria ON, germinal+toroidal):
  v5 (base) · v6 (invasión asentada) · v6-sombra (mismas muertes por tick que
  v6, al azar, sin sonda). Más ablación de la bomba en t=8000 para v6 en las
  semillas sostenidas (hasta 8) y siempre en 13 y 35.
VARAS — escritas ANTES de mirar:
  1. Tipicidad FILTRADA (linaje 500): media ≥ 5 genomas persistentes/tramo en
     [8000,12000) y ≥ 2× su sombra. v5 vs v6.
  2. Anti-monocultura: ecología (Shannon de genomas persistentes, bits) y
     cuota del genoma dominante en el régimen maduro, en las sostenidas de v6.
  3. Anti-ilusión de partos: fracción de la novedad atribuible a parto/invasión
     vs MUTO (más nacimientos ≠ más novedad).
  4. Auto-reparación: R = cola ablada / cola sin ablar (protocolo v5) ≥ 0.5.
VEREDICTO (pre-registrado):
  ÉXITO     si tipicidad v6 > v5, Y ecología mediana ≥ 2 bits con cuota
            dominante < 0.5 en las sostenidas, Y R ≥ 0.5 en ≥ la mitad de las
            sostenidas abladas.
  ILUSIÓN   si la tipicidad sube pero la ecología < 1 bit o la cuota > 0.5
            (un invasor barre el mundo: monocultura/ciclo).
  REFUTADO  si la tipicidad no sube.
  PARCIAL   en cualquier otro caso: leer las tablas, no cerrar.

    PYTHONPATH=src python experiments/utero/exp_utero_invasion.py
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

from zeta_life.utero.ablacion import correr as correr_ablacion  # noqa: E402
from zeta_life.utero.ablacion import medir_cola  # noqa: E402
from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.linaje import RastreadorLinaje  # noqa: E402

N0, MAX_N = 16, 256
TICKS = 14000
TRANCHE = 500
SEEDS = list(range(40))
T_FILTRO = 500
MATURE = (8000, 12000)
FILT_MIN, SHADOW_X, R_OK = 5.0, 2.0, 0.5
ECO_OK, ECO_BAD, SHARE_BAD = 2.0, 1.0, 0.5
T_ABL, POST = 8000, 4000
MAX_ABL = 8
V6 = dict(invasion="asentada")
WORKERS = max(1, min(20, (os.cpu_count() or 4) - 4))
RESULTS = Path(__file__).resolve().parents[2] / "results"
NAME = "utero_invasion"


def correr(seed: int, flags: dict, shadow: list | None) -> dict:
    u = UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True,
                       memoria=True, log_events=True, shadow_deaths=shadow, **flags)
    tr = RastreadorLinaje(T_FILTRO)
    seen: set = set(u.seen)
    nt = TICKS // TRANCHE
    raw = np.zeros(TICKS, dtype=np.int64)
    deaths = np.zeros(TICKS, dtype=np.int64)
    invaded = np.zeros(TICKS, dtype=np.int64)
    vivas = np.zeros(TICKS, dtype=np.int64)
    presence = [Counter() for _ in range(nt)]
    causa = np.zeros((nt, 2), dtype=np.int64)          # [parto/invasión, otro]
    for t in range(TICKS):
        m = u.step()
        deaths[t], invaded[t], vivas[t] = m["deaths"], m["invaded"], int(u.alive.sum())
        born = {c for _, c in u.spawns}
        cg = {int(i) - u.left_grown: u.code[i].tobytes() for i in np.flatnonzero(u.alive)}
        k = t // TRANCHE
        for coord, g in cg.items():
            if g not in seen:
                seen.add(g)
                raw[t] += 1
                causa[k, 0 if coord in born else 1] += 1
        presence[k].update(cg.values())
        tr.tick(t, cg, u.spawns)
    filt = tr.novedad_filtrada(TRANCHE, TICKS)
    ok = tr.resueltos()
    eco, share = np.zeros(nt), np.zeros(nt)
    for k, c in enumerate(presence):
        kept = {g: n for g, n in c.items() if ok.get(g, False)}
        tot = sum(kept.values())
        if tot:
            eco[k] = -sum(n / tot * math.log2(n / tot) for n in kept.values())
        share[k] = (max(c.values()) / sum(c.values())) if c else 0.0   # mundo vacío = 0
    return {"raw": raw, "filt": filt, "deaths": deaths, "invaded": invaded, "vivas": vivas,
            "eco": eco, "share": share, "causa": causa}


def job(seed: int) -> tuple:
    v5 = correr(seed, {}, None)
    v6 = correr(seed, V6, None)
    sh = correr(seed, V6, list(v6["deaths"]))
    return seed, v5, v6, sh


def job_abl(seed: int) -> tuple:
    r = correr_ablacion(seed=seed, memoria=True, ticks=T_ABL + POST, ablate_at=T_ABL,
                        n0=N0, max_n=MAX_N, **V6)
    return seed, r["novedad"], r["ablated"]


def tramos(x: np.ndarray) -> np.ndarray:
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
    out("EL UTERO -- v6: INVASION de tejido asentado (SPAWN reemplaza celdas vivas quietas)")
    out("=" * 78)
    out(f"40 semillas, {TICKS} ticks, memoria ON, germinal+toroidal, eq_window=100, "
        f"linaje {T_FILTRO}, maduro {MATURE}, workers={WORKERS}")
    out("varas y veredicto pre-registrados en el docstring")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (seed, v5, v6, sh) in enumerate(ex.map(job, SEEDS), 1):
            res[seed] = {"v5": v5, "v6": v6, "sh": sh}
            if i % 10 == 0:
                print(f"  ... {i}/40 semillas", flush=True)

    rows = {}
    for s in SEEDS:
        r = res[s]
        rows[s] = {arm: dict(raw=maduro(tramos(r[arm]["raw"])), filt=maduro(r[arm]["filt"]),
                             eco=maduro(r[arm]["eco"]), share=maduro(r[arm]["share"]),
                             inv=float(r[arm]["invaded"][MATURE[0]:MATURE[1]].mean()),
                             vivas=int(r[arm]["vivas"][-1]),
                             parto=float(r[arm]["causa"][MATURE[0] // TRANCHE:MATURE[1] // TRANCHE, 0].sum()
                                         / max(r[arm]["causa"][MATURE[0] // TRANCHE:MATURE[1] // TRANCHE].sum(), 1)))
                   for arm in ("v5", "v6", "sh")}

    def sostenida(s: int, arm: str, sombra: str | None) -> bool:
        f = rows[s][arm]["filt"]
        base = rows[s][sombra]["filt"] if sombra else 0.0
        return f >= FILT_MIN and f >= SHADOW_X * base

    sust5 = [s for s in SEEDS if sostenida(s, "v5", None)]
    sust6 = [s for s in SEEDS if sostenida(s, "v6", "sh")]

    out("-" * 78)
    out("REGIMEN MADURO [8000,12000): por semilla (solo las con novedad filtrada >=1 en algun brazo)")
    out(f"  {'seed':>4} | {'v5 cruda':>8} {'v5 linaje':>9} {'eco':>5} | {'v6 cruda':>8} {'v6 linaje':>9} "
        f"{'eco':>5} {'cuota':>5} {'inv/t':>6} {'parto%':>6} {'vivas':>5} | {'sombra linaje':>13}")
    for s in SEEDS:
        a, b, c = rows[s]["v5"], rows[s]["v6"], rows[s]["sh"]
        if a["filt"] < 1 and b["filt"] < 1 and c["filt"] < 1:
            continue
        out(f"  {s:>4} | {a['raw']:>8.1f} {a['filt']:>9.1f} {a['eco']:>5.2f} | {b['raw']:>8.1f} "
            f"{b['filt']:>9.1f} {b['eco']:>5.2f} {b['share']:>5.2f} {b['inv']:>6.2f} "
            f"{100 * b['parto']:>5.0f}% {b['vivas']:>5} | {c['filt']:>13.1f}")
    out("")
    out(f"1. TIPICIDAD FILTRADA: v5 {len(sust5)}/40 {sust5}   v6 {len(sust6)}/40 {sust6}")
    eco6 = [rows[s]["v6"]["eco"] for s in sust6]
    share6 = [rows[s]["v6"]["share"] for s in sust6]
    if sust6:
        out(f"2. ANTI-MONOCULTURA (sostenidas v6): ecologia mediana {np.median(eco6):.2f} bits "
            f"(min {min(eco6):.2f}); cuota dominante mediana {np.median(share6):.2f} (max {max(share6):.2f})")
        parto6 = [rows[s]["v6"]["parto"] for s in sust6]
        out(f"3. NOVEDAD POR PARTO/INVASION (sostenidas v6): mediana {100 * np.median(parto6):.0f}%  "
            f"(v5 seeds 13/35: {100 * rows[13]['v5']['parto']:.0f}% / {100 * rows[35]['v5']['parto']:.0f}%)")
    inv_all = [rows[s]["v6"]["inv"] for s in SEEDS]
    out(f"   invasiones por tick (maduro, 40 semillas): mediana {np.median(inv_all):.2f}, "
        f"max {max(inv_all):.2f}; semillas con >0: {sum(1 for x in inv_all if x > 0)}/40")
    out(f"   vivas al final v6 (mediana 40 semillas): {np.median([rows[s]['v6']['vivas'] for s in SEEDS]):.0f}"
        f"  (v5: {np.median([rows[s]['v5']['vivas'] for s in SEEDS]):.0f})")

    # ---- ablación de auto-reparación (v6) ----
    out("")
    out("-" * 78)
    out("4. AUTO-REPARACION en v6: ablacion de la bomba en t=8000, R = cola ablada / cola sin ablar")
    abl_seeds = list(dict.fromkeys([13, 35] + sust6))[:MAX_ABL + 2]
    abl = {}
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(abl_seeds))) as ex:
        for seed, nov, n_abl in ex.map(job_abl, abl_seeds):
            pre, pulse, tail = medir_cola(nov, T_ABL)
            _, _, tail_base = medir_cola(res[seed]["v6"]["raw"], T_ABL)
            abl[seed] = dict(n_abl=n_abl, pre=pre, tail=tail, base=tail_base,
                             R=tail / max(tail_base, 1.0), alive=pre >= 25)
    out(f"  {'seed':>4} {'abl':>4} {'pre':>7} {'cola':>7} {'sin ablar':>9} {'R':>6}  sostenida")
    for s in abl_seeds:
        a = abl[s]
        out(f"  {s:>4} {a['n_abl']:>4} {a['pre']:>7.0f} {a['tail']:>7.0f} {a['base']:>9.0f} {a['R']:>6.2f}  "
            f"{'si' if s in sust6 else 'no'}")
    rep = [s for s in sust6 if s in abl and abl[s]["R"] >= R_OK]
    out(f"  se reparan (R>={R_OK}) entre las sostenidas abladas: {len(rep)}/{len([s for s in sust6 if s in abl])} {rep}")

    # ---- veredicto ----
    out("")
    out("=" * 78)
    out("VEREDICTO (regla escrita antes de correr)")
    n_abl_s = len([s for s in sust6 if s in abl])
    if len(sust6) <= len(sust5):
        v = "REFUTADO"
    elif sust6 and (np.median(eco6) < ECO_BAD or np.median(share6) > SHARE_BAD):
        v = "ILUSION (monocultura/ciclo)"
    elif (np.median(eco6) >= ECO_OK and np.median(share6) < SHARE_BAD
          and n_abl_s and len(rep) * 2 >= n_abl_s):
        v = "EXITO"
    else:
        v = "PARCIAL"
    out(f"=> {v}: tipicidad v5 {len(sust5)}/40 -> v6 {len(sust6)}/40; "
        + (f"ecologia mediana {np.median(eco6):.2f} bits, cuota {np.median(share6):.2f}; " if sust6 else "")
        + f"auto-reparacion {len(rep)}/{n_abl_s}")

    # ---- figura ----
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    ax = axes[0]
    for s in SEEDS:
        ax.scatter(rows[s]["v5"]["filt"] + 0.1, rows[s]["v6"]["filt"] + 0.1,
                   color="tab:red" if s in (13, 35) else "tab:blue", s=40 if s in (13, 35) else 15)
        if s in sust6 or s in (13, 35):
            ax.annotate(str(s), (rows[s]["v5"]["filt"] + 0.1, rows[s]["v6"]["filt"] + 0.1), fontsize=7)
    lim = (0.08, 5000)
    ax.plot(lim, lim, "k:", lw=0.8)
    ax.axhline(FILT_MIN, color="gray", ls="--", lw=0.8)
    ax.axvline(FILT_MIN, color="gray", ls="--", lw=0.8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("v5: novedad con linaje, maduro (/tramo)")
    ax.set_ylabel("v6: novedad con linaje, maduro (/tramo)")
    ax.set_title(f"tipicidad: v5 {len(sust5)}/40 -> v6 {len(sust6)}/40")
    xs = (np.arange(TICKS // TRANCHE) + 0.5) * TRANCHE
    k = (TICKS - 2000) // TRANCHE
    ax = axes[1]
    for s, ls in ((13, "-"), (35, "--")):
        ax.plot(xs[:k], res[s]["v5"]["filt"][:k], color="k", ls=ls, label=f"v5 seed {s}")
        ax.plot(xs[:k], res[s]["v6"]["filt"][:k], color="tab:red", ls=ls, label=f"v6 seed {s}")
        ax.plot(xs[:k], res[s]["sh"]["filt"][:k], color="tab:orange", ls=ls, alpha=0.7, label=f"sombra {s}")
    ax.set_yscale("symlog")
    ax.set_xlabel("tick")
    ax.set_ylabel("genomas persistentes nuevos / tramo")
    ax.set_title("13 y 35: v5 vs v6 vs sombra")
    ax.legend(fontsize=6)
    ax = axes[2]
    for s in SEEDS:
        ax.scatter(rows[s]["v6"]["filt"] + 0.1, rows[s]["v6"]["eco"],
                   color="tab:red" if s in sust6 else "tab:blue", s=15)
    ax.axhline(ECO_OK, color="gray", ls="--", lw=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("v6: novedad con linaje, maduro")
    ax.set_ylabel("ecología (bits)")
    ax.set_title("anti-monocultura (rojo = sostenida)")
    fig.suptitle("El Útero v6 — invasión de tejido asentado")
    fig.tight_layout()
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / f"{NAME}.png", dpi=110)
    out("")
    out(f"figura: results/{NAME}.png")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
