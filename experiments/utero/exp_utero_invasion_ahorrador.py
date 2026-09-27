"""
INVASIÓN DESDE RARO — ¿la selección favorece al anticipador?
(docs/PLAN_INTELIGENCIA.md §11; ledger 2026-09-26)

El control positivo mostró que el "ahorrador" (detector de estación en un
registro lento + SPAWN auto-reescrito: pare sólo en la abundancia) es viable,
estable y muere en la hambruna la mitad que el tejido evolucionado. Queda la
pregunta evolutiva: cuando es RARO dentro de un tejido evolucionado, ¿se
propaga? Si invade bajo el orden regular y no bajo el permutado, la selección
favorece la anticipación en esta ecología y los catorce negativos hablan del
CAMINO mutacional, no de la ventaja. Si no invade, la ventaja individual no se
traduce en propagación (p.ej. porque el evolucionado pare 34/100 ticks en la
hambruna y recoloniza más rápido).

DISEÑO: población inicial de 16 celdas: 14 aleatorias + 2 ahorradores en el
centro (posiciones 7 y 8). Ecología v12/v13 (luz finita L0=3, e_mant=0.01,
e0=2, λ=0.02, germinal, invasión asentada). 20 semillas, 20000 ticks.
BRAZOS: clima (A→B→C) · permutado · sin sol (control negativo: sin B el
ahorrador nunca pare; debe extinguirse).
MEDIDAS: fracción de celdas vivas con la firma del ahorrador en maduro (media
y final); TOMA = firma ≥ 0.5 al final; persistencia = firma > 0 al final.
VEREDICTO (escrito antes de correr):
  SELECCIÓN     si toma en clima ≥ 10/20 y ≥ 2× la toma en permutado, y
                extinción en sin sol.
  NEUTRAL       si persiste (firma > 0) en ≥ 10/20 pero no toma.
  ELIMINADO     si se extingue en clima en ≥ 15/20.
  ORDEN-INDEP.  si toma igual en clima y permutado (la ventaja no depende de
                la regularidad, sólo de la estación).

    PYTHONPATH=src python experiments/utero/exp_utero_invasion_ahorrador.py
"""

from __future__ import annotations

import importlib.util
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.sol import Sol  # noqa: E402

N0, MAX_N = 16, 256
TICKS = 20000
SEEDS = list(range(20))
FLAGS = dict(memoria=False, invasion="asentada", eq_window=100, energia=True, luz_finita=3.0,
             e0=2.0, e_mant=0.01, lentos=0.02)
MATURE = 6000
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_invasion_ahorrador"


def _cp():
    spec = importlib.util.spec_from_file_location("cp", HERE / "exp_utero_control_positivo.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def correr(seed: int, arm: str) -> dict:
    cp = _cp()
    sol = None if arm == "sin" else Sol(seed=0, ticks=TICKS, orden="permutado" if arm == "permutado" else "ciclico")
    u = UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True, sol=sol,
                       **FLAGS)
    u.code[7] = cp.AHORRADOR
    u.code[8] = cp.AHORRADOR
    firma = np.zeros(TICKS)
    vivas = np.zeros(TICKS)
    for t in range(TICKS):
        u.step()
        idx = np.flatnonzero(u.alive)
        vivas[t] = len(idx)
        firma[t] = float(np.mean([cp.firma(u.code[i]) for i in idx])) if len(idx) else 0.0
    return dict(seed=seed, arm=arm, firma_med=float(firma[MATURE:].mean()), firma_fin=float(firma[-1]),
                vivas_fin=float(vivas[-1]), firma_1000=float(firma[999]), firma_5000=float(firma[4999]))


def job(a):
    return correr(*a)


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    arms = ("clima", "permutado", "sin")
    out("=" * 80)
    out("INVASION DESDE RARO -- 2 ahorradores entre 14 celdas aleatorias: se propagan?")
    out("=" * 80)
    out(f"flags {FLAGS}; {len(SEEDS)} semillas; {TICKS} ticks; veredicto en el docstring")
    out("")
    res: dict = {a: {} for a in arms}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for r in ex.map(job, [(s, a) for a in arms for s in SEEDS]):
            res[r["arm"]][r["seed"]] = r
    out(f"  {'brazo':<10} {'firma@1000':>10} {'firma@5000':>10} {'firma maduro':>12} {'firma fin':>9} {'toma(>=0.5)':>11} {'persiste(>0)':>12} {'extinto':>8} {'vivas fin':>9}")
    T = {}
    for a in arms:
        R = list(res[a].values())
        toma = sum(1 for r in R if r["firma_fin"] >= 0.5)
        pers = sum(1 for r in R if r["firma_fin"] > 0)
        ext = sum(1 for r in R if r["firma_fin"] == 0)
        T[a] = dict(toma=toma, pers=pers, ext=ext)
        out(f"  {a:<10} {np.median([r['firma_1000'] for r in R]):>10.2f} {np.median([r['firma_5000'] for r in R]):>10.2f} "
            f"{np.median([r['firma_med'] for r in R]):>12.2f} {np.median([r['firma_fin'] for r in R]):>9.2f} "
            f"{toma:>8}/{len(SEEDS):<2} {pers:>9}/{len(SEEDS):<2} {ext:>5}/{len(SEEDS):<2} {np.median([r['vivas_fin'] for r in R]):>9.0f}")
    out("  por semilla (firma final) clima: " + " ".join(f"{res['clima'][s]['firma_fin']:.2f}" for s in SEEDS))
    out("  por semilla (firma final) perm.: " + " ".join(f"{res['permutado'][s]['firma_fin']:.2f}" for s in SEEDS))
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    c, p, n = T["clima"], T["permutado"], T["sin"]
    if c["toma"] >= 10 and c["toma"] >= 2 * max(p["toma"], 1) and n["ext"] >= 15:
        v = "SELECCION: el ahorrador invade bajo el orden regular y no bajo el permutado"
    elif c["toma"] >= 10 and abs(c["toma"] - p["toma"]) < 4:
        v = "ORDEN-INDEPENDIENTE: invade igual con o sin regularidad (le basta la estacion)"
    elif c["ext"] >= 15:
        v = "ELIMINADO: la ventaja individual no se traduce en propagacion"
    elif c["pers"] >= 10:
        v = "NEUTRAL: persiste sin tomar"
    else:
        v = "MIXTO: leer la tabla"
    out(f"=> {v}  (clima toma {c['toma']}, persiste {c['pers']}, extinto {c['ext']}; "
        f"permutado toma {p['toma']}; sin sol extinto {n['ext']})")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
