"""
El Útero — ¿ya existe interacción EFECTIVA regla↔regla? (transferencia
horizontal por COPY) y ¿de dónde sale la novedad: COPY, MUTO o parto?

El estado del arte (docs/ESTADO_DEL_ARTE_UTERO.md) converge en que el motor
de novedad sostenida es ECOLÓGICO —parasitismo (Stringmol), colisión y sexo
(Evoloop)— y no una mutación germinal más ingeniosa. En El Útero la op COPY
(copiar una instrucción de un vecino al propio programa) es interacción
regla↔regla en potencia. Nunca medimos si ocurre de verdad, cuánto, ni si
acuña novedad. Este experimento lo mide con `log_events=True` (observación
pura, byte-idéntica), antes de tocar el sustrato.

Definiciones (por celda y tick, desde `execute(stats=)`):
  - COPY efectiva: una COPY que CAMBIÓ una instrucción propia (por-op, BRUTA:
    una escritura posterior en la misma ejecución puede deshacerla).
  - TH (transferencia horizontal): COPY efectiva cuya fuente es un vecino de
    GENOMA DISTINTO al propio (no de sí misma, no de un clon).
  - MUTO efectiva: una MUTO que cambió el opcode de una instrucción (bruta).
  - NETO: el genoma de la celda al final del tick difiere del anterior. Las
    tasas NETAS (cambio neto; cambio neto con TH; cambio neto sólo MUTO) son
    la medida honesta de reescritura; las brutas muestran cuánta reescritura
    se deshace a sí misma dentro de una ejecución (reescritura idempotente).
  - Atribución de un genoma NUEVO acuñado en una coord: parto (SPAWN esa
    coord ese tick) > TH > copia-de-clon > MUTO > otro (prioridad).
  - bomba/llanura: código reescrito en los últimos 200 ticks / no.

PREDICCIONES — escritas ANTES de mirar (n=2 para 13 vs 35; n=40 para la
correlación), con criterio:
  P1 Las llanuras de la 13 tienen ≥2× la tasa de TH de las llanuras de la 35
     (régimen maduro t∈[8000,12000)).
  P2 A través de las 40 semillas, la tasa de TH en [4000,8000) correlaciona
     con la novedad cruda tardía [8000,12000): Spearman ρ ≥ 0.3.
  P3 En la 13, una fracción mayor de la novedad se atribuye a TH que en la 35
     (≥2×).
  P4 (sanidad) La mayor parte de la novedad NO viene de MUTO sola — si viniera,
     la interacción no importa y la literatura no aplica aquí.
Manos: ventana de actividad 200, ventanas de tiempo, prioridad de atribución.

    PYTHONPATH=src python experiments/utero/exp_utero_interaccion.py
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
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402

N0, MAX_N = 16, 256
TICKS = 12000
TRANCHE = 500
SEEDS = list(range(40))
ACTIVE_WIN = 200
EARLY, MATURE = (4000, 8000), (8000, 12000)
CAUSES = ("parto", "TH", "copia_clon", "muto", "otro")
WORKERS = max(1, min(20, (os.cpu_count() or 4) - 4))
RESULTS = Path(__file__).resolve().parents[2] / "results"
NAME = "utero_interaccion"


def correr(seed: int) -> dict:
    u = UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True,
                       memoria=True, log_events=True)
    seen: set = set(u.seen)
    last_code: dict = {}
    last_change: dict = {}
    nt = TICKS // TRANCHE
    # [tramo, bomba/llanura, {celdas, copy_eff, TH, muto_eff, neto, neto_TH, neto_solo_muto}]
    acc = np.zeros((nt, 2, 7), dtype=np.int64)
    attrib = np.zeros((nt, len(CAUSES)), dtype=np.int64)
    raw = np.zeros(TICKS, dtype=np.int64)
    for t in range(TICKS):
        u.step()
        k = t // TRANCHE
        born = {c for _, c in u.spawns}
        cg = {int(i) - u.left_grown: u.code[i].tobytes() for i in np.flatnonzero(u.alive)}
        for coord, st in u.events.items():
            pump = 0 if (t - last_change.get(coord, -10**9)) <= ACTIVE_WIN else 1
            acc[k, pump, 0] += 1
            acc[k, pump, 1] += st["copy_writes"] > 0
            acc[k, pump, 2] += st["copy_distinct"]
            acc[k, pump, 3] += st["muto_writes"] > 0
            net = coord in last_code and coord in cg and last_code[coord] != cg[coord]
            if net:
                acc[k, pump, 4] += 1
                acc[k, pump, 5] += st["copy_distinct"]
                acc[k, pump, 6] += (st["muto_writes"] > 0 and st["copy_writes"] == 0)
        for coord, g in cg.items():
            if coord in last_code and last_code[coord] != g:
                last_change[coord] = t
            if g in seen:
                continue
            seen.add(g)
            raw[t] += 1
            st = u.events.get(coord)
            if coord in born:
                cause = "parto"
            elif st is None:
                cause = "otro"
            elif st["copy_distinct"]:
                cause = "TH"
            elif st["copy_writes"] > 0:
                cause = "copia_clon"
            elif st["muto_writes"] > 0:
                cause = "muto"
            else:
                cause = "otro"
            attrib[k, CAUSES.index(cause)] += 1
        last_code = cg
    return {"seed": seed, "acc": acc, "attrib": attrib, "raw": raw}


def tasas(acc: np.ndarray, win: tuple) -> dict:
    a, b = win[0] // TRANCHE, win[1] // TRANCHE
    out = {}
    def fila(block: np.ndarray) -> dict:
        cells = block[:, 0].sum()
        net = block[:, 4].sum()
        return {"celdas": int(cells),
                "copy": block[:, 1].sum() / max(cells, 1),
                "TH": block[:, 2].sum() / max(cells, 1),
                "muto": block[:, 3].sum() / max(cells, 1),
                "neto": net / max(cells, 1),
                "neto_TH": block[:, 5].sum() / max(net, 1),
                "neto_muto": block[:, 6].sum() / max(net, 1)}
    for j, lab in enumerate(("bomba", "llanura")):
        out[lab] = fila(acc[a:b, j])
    out["todas"] = fila(acc[a:b].sum(axis=1))
    return out


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 78)
    out("EL UTERO -- interaccion EFECTIVA regla<->regla (COPY / transferencia horizontal)")
    out("=" * 78)
    out(f"memoria ON, germinal+toroidal, {TICKS} ticks, 40 semillas, workers={WORKERS}")
    out("predicciones P1..P4 y criterios en el docstring, escritos antes de correr")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for r in ex.map(correr, SEEDS):
            res[r["seed"]] = r

    # ---- 13 vs 35: tasas por celda-tick, bomba vs llanura, régimen maduro ----
    out("-" * 78)
    out(f"TASAS POR CELDA-TICK (regimen maduro t in {list(MATURE)})  -- 13 vs 35, y seed 0 de ref.")
    out(f"  {'seed':>4} {'zona':<8} {'celda-ticks':>11} | {'BRUTAS: COPY':>12} {'TH':>7} {'MUTO':>7} | "
        f"{'NETO cambio':>11} {'con TH':>7} {'solo MUTO':>9}")
    T = {s: tasas(res[s]["acc"], MATURE) for s in SEEDS}
    for s in (13, 35, 0):
        for zona in ("bomba", "llanura", "todas"):
            z = T[s][zona]
            out(f"  {s:>4} {zona:<8} {z['celdas']:>11} | {z['copy']:>12.4f} {z['TH']:>7.4f} "
                f"{z['muto']:>7.4f} | {z['neto']:>11.4f} {z['neto_TH']:>7.3f} {z['neto_muto']:>9.3f}")
    out("  (brutas = por operacion; NETO = el genoma cambio al final del tick; 'con TH' y")
    out("   'solo MUTO' son fracciones de los cambios netos)")
    # ---- atribución de la novedad ----
    out("")
    out("ATRIBUCION DE LOS GENOMAS NUEVOS (regimen maduro): % por causa")
    out(f"  {'seed':>4} {'nuevos':>7} " + " ".join(f"{c:>11}" for c in CAUSES))
    A = {}
    a, b = MATURE[0] // TRANCHE, MATURE[1] // TRANCHE
    for s in SEEDS:
        v = res[s]["attrib"][a:b].sum(axis=0)
        A[s] = (int(v.sum()), v / max(v.sum(), 1))
    for s in (13, 35, 0):
        n, fr = A[s]
        out(f"  {s:>4} {n:>7} " + " ".join(f"{100 * f:>10.1f}%" for f in fr))
    # ---- 40 semillas: correlación TH temprana -> novedad tardía ----
    out("")
    out(f"40 SEMILLAS: tasa de TH en {list(EARLY)} vs novedad cruda tardia {list(MATURE)}")
    th_early = np.array([tasas(res[s]["acc"], EARLY)["todas"]["TH"] for s in SEEDS])
    th_plain_early = np.array([tasas(res[s]["acc"], EARLY)["llanura"]["TH"] for s in SEEDS])
    late = np.array([res[s]["raw"][MATURE[0]:MATURE[1]].sum() / ((MATURE[1] - MATURE[0]) / TRANCHE)
                     for s in SEEDS])
    rho, p = spearmanr(th_early, late)
    rho_p, p_p = spearmanr(th_plain_early, late)
    out(f"  Spearman TH(todas) vs novedad tardia: rho={rho:+.2f} p={p:.3f}")
    out(f"  Spearman TH(llanuras) vs novedad tardia: rho={rho_p:+.2f} p={p_p:.3f}")
    out(f"  semillas con TH>0 en [4000,8000): {int((th_early > 0).sum())}/40 ; "
        f"con novedad tardia >=25/tramo: {[s for s in SEEDS if late[s] >= 25]}")
    top = np.argsort(-th_early)[:8]
    out("  top-8 por TH temprana: " + ", ".join(f"s{SEEDS[i]}={th_early[i]:.4f}(nov {late[i]:.0f})" for i in top))

    # ---- veredicto por predicción ----
    out("")
    out("=" * 78)
    out("PREDICCIONES (criterios pre-registrados)")
    th13, th35 = T[13]["llanura"]["TH"], T[35]["llanura"]["TH"]
    r1 = th13 / th35 if th35 > 0 else (float("inf") if th13 > 0 else 1.0)
    out(f"  P1 TH llanuras 13/35 = {th13:.4f}/{th35:.4f} = {r1:.2f}  -> {'SI' if r1 >= 2 else 'no'}")
    out(f"  P2 rho(TH temprana, novedad tardia) = {rho:+.2f}  -> {'SI' if rho >= 0.3 else 'no'}")
    fth13, fth35 = A[13][1][CAUSES.index("TH")], A[35][1][CAUSES.index("TH")]
    r3 = fth13 / fth35 if fth35 > 0 else (float("inf") if fth13 > 0 else 1.0)
    out(f"  P3 fraccion de novedad por TH 13/35 = {100*fth13:.1f}%/{100*fth35:.1f}% = {r3:.2f}  "
        f"-> {'SI' if r3 >= 2 else 'no'}")
    for s in (13, 35):
        fm = A[s][1][CAUSES.index("muto")]
        out(f"  P4 seed {s}: novedad por MUTO sola = {100*fm:.1f}%  -> "
            f"{'la interaccion importa' if fm < 0.5 else 'MUTO domina: la interaccion NO es el motor'}")

    # ---- figura ----
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    xs = (np.arange(TICKS // TRANCHE) + 0.5) * TRANCHE
    for ax, s in zip(axes[:2], (13, 35)):
        acc = res[s]["acc"]
        for j, lab, col in ((0, "bomba", "tab:red"), (1, "llanura", "tab:blue")):
            cells = np.maximum(acc[:, j, 0], 1)
            ax.plot(xs, acc[:, j, 2] / cells, color=col, label=f"TH {lab}")
            ax.plot(xs, acc[:, j, 3] / cells, color=col, ls=":", label=f"MUTO {lab}")
        ax.set_yscale("log")
        ax.set_title(f"seed {s} — tasa por celda-tick")
        ax.set_xlabel("tick")
        ax.legend(fontsize=7)
    axes[0].set_ylabel("eventos efectivos / celda-tick")
    ax = axes[2]
    ax.scatter(th_early + 1e-5, late + 0.1, s=15, color="tab:blue")
    for s in (13, 35):
        ax.scatter(th_early[s] + 1e-5, late[s] + 0.1, s=50, color="tab:red")
        ax.annotate(str(s), (th_early[s] + 1e-5, late[s] + 0.1), fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("TH por celda-tick en [4000,8000)")
    ax.set_ylabel("novedad cruda tardía (/tramo)")
    ax.set_title(f"40 semillas: Spearman ρ={rho:+.2f}")
    fig.suptitle("El Útero — ¿hay interacción efectiva regla↔regla y acuña novedad?")
    fig.tight_layout()
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / f"{NAME}.png", dpi=110)
    out("")
    out(f"figura: results/{NAME}.png")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
